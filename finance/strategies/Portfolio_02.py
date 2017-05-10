import oandapy as opy
from datetime import datetime
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels import regression
import matplotlib.pyplot as plt

"""
Created on April 22 21:29:53 2017
trend continuation trading algorithm using linear regression channels

@author: kenny potts
"""

"""
NOTES:
 - labeled todos
 - manage insufficient funds (max margin)
 - unrealized pnl, may not be easy without v20 api
 - 
 
"""

# from matplotlib import animation
# from matplotlib import syle
# style.use('seaborn_whitegrid')

class Position:
    def __init__(self, instrument, position_size, side):
        self.instrument = instrument
        self.position_size = position_size
        self.side = side
        self.status = False  # True if open position
        self.trade_id = None
        self.executed_price = None
        self.closed_price = None
        self.execution_time = None
        self.closed_time = None
        self.dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        self.profit = 0

    def open_position(self, oanda, account_id):
        if not self.status:
            response = oanda.create_order(
                account_id,
                instrument=self.instrument,
                units=self.position_size,
                side=self.side,
                type='market')

            if response is not None:
                self.executed_price = float(response["price"])
                self.trade_id = int(response['tradeOpened']['id'])
                self.execution_time = datetime.strptime(response['time'], self.dt_format)
                print("Placed order %s %s %s at market." % (self.side, self.position_size, self.instrument))
                self.status = True
                return True  # Order is successful

            return False  # Order is unsuccessful
        return False

    def close_position(self, oanda, account_id):
        if self.status:
            response = oanda.close_trade(
                account_id,
                trade_id=self.trade_id
            )

            if response is not None:
                self.closed_price = float(response["price"])
                self.profit = float(response['profit'])
                self.closed_time = datetime.strptime(response['time'], self.dt_format)
                self.side = response['side']
                self.status = False
                print("Closed position %s %s %s at market for %s profit." % (self.side, self.position_size,
                                                                             self.instrument, self.profit))
                return True  # Order is successful

            return False  # Order is unsuccessful
        return False


class Pair:
    def __init__(self, **kwargs):
        self.oanda = kwargs['oanda']
        self.account_id = kwargs['account_id']
        self.instrument = kwargs['instrument']
        self.positions = []
        self.num_positions = 0
        self.running_profit = 0
        self.resample_interval = kwargs['resample_interval']
        self.history_granularity = 'M1' # "S10" #TODO: integrate with resample interval, only one necessary
                                                # parse to correct form for pandas and oanda.
        self.lookback_period = kwargs['lookback_period']
        self.std_multiplier = kwargs['std_multiplier']
        self.dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"

        self.prices = pd.DataFrame()
        self.spreads = pd.DataFrame()
        # self.history = pd.DataFrame()
        self.slopes = pd.DataFrame()
        self.intercepts = pd.DataFrame()
        self.preds = pd.DataFrame()
        self.upper_preds = pd.DataFrame()
        self.lower_preds = pd.DataFrame()
        self.stds = pd.DataFrame()

        self.current_reg_line = None
        self.current_lower_line = None
        self.current_upper_line = None

        self.tick_count = 0
        self.tick_update = kwargs['tick_update']
        self.current_units = 0
        self.current_side = None

    def download_history(self):
        # Download some historical data so we have accurate data from the start
        print('Downloading {0} Historical Rates...'.format(self.instrument))
        resp = self.oanda.get_history(instrument=self.instrument,
                                      granularity=self.history_granularity,
                                      count=2*self.lookback_period+10)  # 5000 max here
        data = pd.DataFrame(resp['candles'])
        data.set_index('time', inplace=True)
        data.index = [pd.datetime.strptime(x, self.dt_format) \
                      for x in data.index]

        self.prices.loc[:, self.instrument] = data.closeAsk
        self.spreads.loc[:, self.instrument] = data.closeAsk - data.closeBid
        time = data.index[-1]
        self.preds.loc[time, self.instrument], self.upper_preds.loc[time, self.instrument], \
            self.lower_preds.loc[time, self.instrument], self.slopes.loc[time, self.instrument], \
            self.intercepts.loc[time, self.instrument], self.stds.loc[time, self.instrument] = \
            self.lin_reg()
        print('Historical {0} Rates Download Complete.'.format(self.instrument))
        print('Running historical regression on {0}'.format(self.instrument))
        self.historical_lin_reg()
        print('{0} Historical regression complete'.format(self.instrument))

    def open_new_position(self, size, side):
        if side == self.current_side or self.current_units == 0:  # check to make sure not illegal hedge position
            p = Position(self.instrument, size, side)

            if p.open_position(self.oanda, self.account_id):
                self.positions.append(p)
                self.current_side = side
                if side == 'buy':
                    self.current_units += size
                else:
                    self.current_units -= size
                return True
            else:
                del p
                return False
        else:
            return False

    def close_all_positions(self):
        for p in self.positions:
            if p.status: # there should't be any positions with status False, but just in case
                closed = False
                while not closed:
                    if p.close_position(self.oanda, self.account_id):
                        self.running_profit += p.profit
                        closed = True
                        # TODO: write to a history df
            else:
                self.running_profit += p.profit
                # TODO: write to a history df
        for i in range(len(self.positions)):
            p = self.positions.pop()
            del p
        self.current_units = 0
        self.current_side = None

    def close_position_fifo(self):
        if len(self.positions) > 0:
            p = self.positions.pop(0)
            closed = False
            while not closed:
                if p.close_position(self.oanda, self.account_id):
                    closed = True
                    if p.side == 'buy':
                        self.current_units -= p.position_size
                    else:
                        self.current_units += p.position_size
                    self.running_profit += p.profit
            del p

    def update(self, time, symbol, bid, ask):
        midprice = (ask + bid) / 2.
        self.prices.loc[time, symbol] = midprice

        self.spreads.loc[time, symbol] = ask - bid

        if self.tick_count >= self.tick_update:
            self.tick_count = 0

            self.preds.loc[time, symbol], self.upper_preds.loc[time, symbol], \
            self.lower_preds.loc[time, symbol], self.slopes.loc[time, symbol], \
            self.intercepts.loc[time, symbol], self.stds.loc[time, symbol] = \
                self.lin_reg()


        else:
            self.tick_count += 1

    def historical_lin_reg(self):  # TODO: try a kalman filter for beta/alpha, compare to OLS
        resampled_prices = self.prices.resample(
            self.resample_interval,
            how='last',
            fill_method="ffill")
        # num_updates = resampled_prices.shape[0] - self.lookback_period
        for i in range(self.lookback_period):
            prices = resampled_prices[self.instrument].iloc[i - (2*self.lookback_period):i - self.lookback_period]

            time = prices.index[-1]
            x = (prices.index - prices.index[0]).astype('timedelta64[s]').values
            x = sm.add_constant(x)
            y = prices.values
            model = regression.linear_model.OLS(y, x).fit()
            intercept = model.params[0]
            slope = model.params[1]
            x = x[:, 1]

            y_hat = x * slope + intercept
            pred = x[-1] * slope + intercept

            std = (prices - y_hat).abs().std()

            upper = pred + self.std_multiplier * std
            lower = pred - self.std_multiplier * std

            self.preds.loc[time, self.instrument] = pred
            self.upper_preds.loc[time, self.instrument] = upper
            self.lower_preds.loc[time, self.instrument] = lower
            self.slopes.loc[time, self.instrument] = slope
            self.intercepts.loc[time, self.instrument] = intercept
            self.stds.loc[time, self.instrument] = std

    def lin_reg(self):  # TODO: try a kalman filter for beta/alpha, compare to OLS
        # Running the linear regression
        # NOTE: timedelta64[s] changed to 's' for second increment
        resampled_prices = self.prices.resample(
            self.resample_interval,
            how='last',
            fill_method="ffill")
        prices = resampled_prices[self.instrument].iloc[-self.lookback_period:]

        x = (prices.index - prices.index[0]).astype('timedelta64[s]').values
        x = sm.add_constant(x)
        y = prices.values
        model = regression.linear_model.OLS(y, x).fit()
        intercept = model.params[0]
        slope = model.params[1]
        x = x[:, 1]

        del self.current_reg_line
        self.current_reg_line = x * slope + intercept
        pred = x[-1] * slope + intercept

        std = (prices - self.current_reg_line).abs().std()

        upper = pred + self.std_multiplier * std
        lower = pred - self.std_multiplier * std

        del self.current_upper_line
        del self.current_lower_line
        self.current_upper_line = self.current_reg_line + self.std_multiplier * std
        self.current_lower_line = self.current_reg_line - self.std_multiplier * std

        return pred, upper, lower, slope, intercept, std


class Regressor_Reverter(opy.Streamer):
    def __init__(self, *args, **kwargs):
        opy.Streamer.__init__(self, *args, **kwargs)
        self.oanda = opy.API(kwargs["environment"],
                             kwargs["access_token"])

        self.instruments = None
        self.account_id = None
        self.qty = 0
        self.resample_interval = '10s'
        self.history_granularity = "S10"
        self.chart_update_seconds = 30

        self.lookback_period = 0
        self.std_multiplier = 0
        self.spread_filter = True

        self.pairs = {}

        self.max_loss = 100

        self.zones = {}
        self.plots = dict()
        self.fig, self.axarr = None, None
        self.num_ticks = 0

        self.base_currency = 'USD'

        self.tick_update = 0

        # for updating plot/s
        self.plot_update_time = datetime.now()


        self.unrealized_pnl = 0 # TODO: unrealized pnl
        self.realized_pnl = 0
        self.position = 0
        self.dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    def set_up_charts(self):
        # Setup for live plots TODO: plotting, make a separate plotting function
        num_pairs = len(self.instruments)
        self.fig, self.axarr = plt.subplots(2, num_pairs, figsize=(20, 15))
        for i in range(num_pairs):
            pair_plots = dict()
            pair_plots['prices_1'], = self.axarr[0, i].plot([], [], alpha=0.5)
            pair_plots['mid_reg_line'], = self.axarr[0, i].plot([], [], alpha=0.8)
            pair_plots['upper_reg_line'], = self.axarr[0, i].plot([], [], alpha=0.6)
            pair_plots['lower_reg_line'], = self.axarr[0, i].plot([], [], alpha=0.6)
            pair_plots['prices_2'], = self.axarr[1, i].plot([], [], alpha=0.5)
            pair_plots['rolling_mid_reg_line'], = self.axarr[1, i].plot([], [], alpha=0.8)
            pair_plots['rolling_upper_reg_line'], = self.axarr[1, i].plot([], [], alpha=0.6)
            pair_plots['rolling_lower_reg_line'], = self.axarr[1, i].plot([], [], alpha=0.6)
            # Autoscale on unknown axis
            self.axarr[0, i].set_autoscaley_on(True)
            self.axarr[0, i].set_autoscalex_on(True)
            self.axarr[0, i].grid()
            self.axarr[0, i].set_title(self.instruments[i])  # +" current regression")
            self.axarr[1, i].set_title(self.instruments[i])  # + " rolling regression")
            self.axarr[1, i].set_autoscaley_on(True)
            self.axarr[1, i].set_autoscalex_on(True)
            self.axarr[1, i].grid()
            self.plots[self.instruments[i]] = pair_plots
        self.fig.show()

    def update_charts(self):
        counter = 0
        for symbol, pair in self.pairs.items():
            resampled_prices = pair.prices.resample(
                self.resample_interval,
                how='last',
                fill_method="ffill")
            preds_resampled = pair.preds.resample(
                self.resample_interval,
                how='last',
                fill_method="ffill")
            upper_preds_resampled = pair.upper_preds.resample(
                self.resample_interval,
                how='last',
                fill_method="ffill")
            lower_preds_resampled = pair.lower_preds.resample(
                self.resample_interval,
                how='last',
                fill_method="ffill")
            prices = resampled_prices[symbol].iloc[-self.lookback_period:]
            preds = preds_resampled[symbol].iloc[-self.lookback_period:]
            upper_preds = upper_preds_resampled[symbol].iloc[-self.lookback_period:]
            lower_preds = lower_preds_resampled[symbol].iloc[-self.lookback_period:]
            x = (prices.index - prices.index[0]).astype('timedelta64[s]').values
            x_preds = (preds.index - preds.index[0]).astype('timedelta64[s]').values
            x_upper_preds = (upper_preds.index - upper_preds.index[0]).astype('timedelta64[s]').values
            x_lower_preds = (lower_preds.index - lower_preds.index[0]).astype('timedelta64[s]').values
            self.plots[symbol]['prices_1'].set_data(x, prices.values)
            self.plots[symbol]['mid_reg_line'].set_data(x, pair.current_reg_line)

            self.plots[symbol]['upper_reg_line'].set_data(x, pair.current_upper_line)
            self.plots[symbol]['lower_reg_line'].set_data(x, pair.current_lower_line)

            self.plots[symbol]['prices_2'].set_data(x, prices.values)
            self.plots[symbol]['rolling_mid_reg_line'].set_data(x_preds, preds.values)
            self.plots[symbol]['rolling_upper_reg_line'].set_data(x_upper_preds, upper_preds.values)
            self.plots[symbol]['rolling_lower_reg_line'].set_data(x_lower_preds, lower_preds.values)

            # self.axarr[0, counter].set_xticklabels(prices.index)
            self.axarr[0, counter].relim()
            self.axarr[0, counter].autoscale_view()
            # self.axarr[1, counter].set_xticklabels(prices.index)
            try:
                self.axarr[1, counter].relim()
                self.axarr[1, counter].autoscale_view()
            except:
                print('error plotting')
                pass  # TODO: determine issue with plotting relim, number of data points
                      # I believe to the issue has been resolved, will need to follow closely

            counter += 1

            try:
                self.fig.autofmt_xdate()
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
            except:
                print('error plotting')
                pass  # TODO: determine issue with plotting, number of data points does not match
                      # I believe to the issue has been resolved, will need to follow closely

        # print('update charts')

    def begin(self, **params):
        self.instruments = params["instruments"]
        self.account_id = params["accountId"]
        self.base_currency = params['base_currency']
        self.qty = params["qty"]
        self.resample_interval = params["resample_interval"]
        self.lookback_period = params["lookback_period"]
        self.std_multiplier = params['std_multiplier']
        self.spread_filter = params['spread_filter']
        self.max_loss = params['max_loss']
        self.tick_update = params['tick_update']
        self.set_up_charts()

        for instrument in self.instruments:
            # make the pairs
            p = Pair(oanda=self.oanda, account_id=self.account_id,
                     instrument=instrument, resample_interval=self.resample_interval,
                     lookback_period=self.lookback_period, std_multiplier=self.std_multiplier,
                     tick_update=self.tick_update)
            self.pairs[instrument] = p
            # download history
            p.download_history()

        self.start(**params)  # Start streaming prices

    def on_success(self, data):
        time, symbol, bid, ask = self.parse_tick_data(
            data["tick"])
        self.pairs[symbol].update(time, symbol, bid, ask)
        self.perform_trade_logic()
        if (datetime.now() - self.plot_update_time).seconds > self.chart_update_seconds:
            self.update_charts()
            self.plot_update_time = datetime.now()
        # if self.num_ticks >= self.tick_update:
        #     self.num_ticks = 0
        #     print('performing trade logic')
        #     self.perform_trade_logic()
        # else:
        #     self.num_ticks += 1

    def parse_tick_data(self, dict_data):
        time = pd.datetime.strptime(dict_data["time"],
                                    self.dt_format)
        ask = float(dict_data["ask"])
        bid = float(dict_data["bid"])
        instrument = dict_data["instrument"]
        return time, instrument, bid, ask

    def perform_trade_logic(self):
        total_pnl = 0
        # TODO: make comparison with resample i.e. ohlc bar close in location
        for symbol, pair in self.pairs.items():
            latest_price = pair.prices[symbol].iloc[-1]
            latest_spread = pair.spreads[symbol].iloc[-1]
            latest_pred = pair.preds[symbol].iloc[-1]
            latest_upper_pred = pair.upper_preds[symbol].iloc[-1]
            latest_lower_pred = pair.lower_preds[symbol].iloc[-1]
            latest_slope = pair.slopes[symbol].iloc[-1]

            if self.spread_filter:
                if np.abs(latest_price - latest_pred) > \
                                1.5 * np.abs(latest_spread + latest_pred):
                    trade_is_possible = True
                else:
                    trade_is_possible = False
            else:
                trade_is_possible = True

            # Max loss triggered, exit trade - Will need to be adjusted for
            # individual instruments as well as total portfolio
            # also for multiple positions on same pair
            # if self.unrealized_pnl < (-1) * self.max_loss:
            #     if self.position > 0:
            #         self.check_and_send_order(False)
            #     elif self.position < 0:
            #         self.check_and_send_order(True)

            # Go Long
            if latest_slope > 0 and latest_price < latest_lower_pred:
                self.zones[symbol] = "long_trigger"
                if pair.current_units == 0 and trade_is_possible:
                    pair.open_new_position(self.qty, 'buy')
                    pair.open_new_position(self.qty, 'buy')
                elif self.position < 0:
                    pair.close_all_positions()
            # Go short
            elif latest_slope < 0 and latest_price > latest_upper_pred:
                self.zones[symbol] = "short_trigger"
                if pair.current_units == 0 and trade_is_possible:
                    pair.open_new_position(self.qty, 'sell')
                    pair.open_new_position(self.qty, 'sell')
                elif self.position > 0:
                    pair.close_all_positions()
            # don't be short
            elif latest_price <= latest_pred:
                self.zones[symbol] = "half_or_no_shorts"
                if pair.current_units < -self.qty:
                    pair.close_position_fifo()
            # don't be long
            elif latest_price >= latest_pred:
                self.zones[symbol] = "half_or_no_longs"
                if pair.current_units > self.qty:
                    pair.close_position_fifo()

            # exit short if slope is positive
            if pair.current_units < 0 and latest_slope > 0:
                print('emergency out 1')
                pair.close_all_positions()
            # exit long if slope is negative
            elif pair.current_units > 0 and latest_slope < 0:
                print('emergency out 2')
                pair.close_all_positions()
            total_pnl += pair.running_profit
        self.realized_pnl = total_pnl


 # TODO: uncrealized pnl, require currency conversion with rest api


    def on_error(self, data):
        print(data)
        self.disconnect()


if __name__ == "__main__":
    f = open('/Users/kennypotts/Desktop/Data/oanda_demo_api_key.txt', 'r')
    key = f.read()
    key = key.strip()
    account_id = 2181424
    system1 = Regressor_Reverter(environment="practice", access_token=key)
    system1.begin(accountId=account_id,
                  instruments=["EUR_USD", 'GBP_USD', 'USD_JPY', 'GBP_JPY', 'EUR_GBP',
                               'USD_CAD', 'NZD_USD', 'AUD_USD', 'EUR_JPY'],
                  base_currency="USD",
                  qty=10000,
                  resample_interval="1min",
                  lookback_period=240,
                  std_multiplier=2.7,
                  spread_filter=False,
                  max_loss=60,
                  tick_update=15)
