#
#   Created by Kenneth Potts
# 
#   This Algorithm was built for Quantconnect's Lean trading/backtesting engine.
#   It is an example of a donchian channel trend following algorithm with dynamic
#   positition sizing that adjusts based on current volitility.
# 
#   This algorithm is a work in progress and is an base example of other similar
#   algorithms that I am working on.
# 
#   For questions, conceerns, advice, feedback please email me at kfpotts1@gmail.com
#
#    You can view the QCAlgorithm base class on Github: 
#    https://github.com/QuantConnect/Lean/tree/master/Algorithm
#
"""
##### NOTES ######

FOR POSITION SIZING IMPLEMENTATION SEE https://www.quantconnect.com/forum/discussion/1324/getting-started---multi-pair-forex-trend-system




###################
"""




import numpy as np
import pandas as pd
# import inspect
import decimal as d


class BasicTemplateAlgorithm(QCAlgorithm):

    def Initialize(self):
        # Set the cash we'd like to use for our backtest
        # This is ignored in live trading 
        self.equity = 10000
        self.SetCash(self.equity)
        
        # Start and end dates for the backtest.
        # These are ignored in live trading.
        self.SetStartDate(2012,4,1)
        self.SetEndDate(2014,4,8)        
        
        self.long_period = 200
        # self.short_period =4
        # self.size = 1000
        # self.size = 1.0/len(self.pairs)
        # self.size = 10000
        
        # percentage of the Portfolio to risk on each trade
        self.pct_portfolio_risk = 0.02
        
        self.atr_trail_mult = 6
        # Use same mult as above
        # self.atr_entry_mult = self.atr_trail_mult
        self.atr_entry_mult = 6
        self.atr_period = 40
        self.pos_max_num = 15
        self.my_resolution = Resolution.Hour
        
        ############################
        
        # Add assets you'd like to see
        self.pairs = ['EURUSD',
                      'GBPUSD',
                      'USDJPY',
                      'GBPJPY',
                      'EURGBP',
                      'USDCAD',
                      'NZDUSD',
                      'AUDUSD',
                      'EURJPY',
                      'USDCHF',
                      'GBPNZD',
                      'EURCAD']
        
        self.next_positions = {}
        self.bars_since_entry = {}
        self.ATRs = {}
        self.last_stop_prices = {}
        self.next_position_entry = {}
        self.current_positions = {}
        self.next_position_sizes = {}
        # self.num_positions = {}
        for i in range(len(self.pairs)):
            # self.AddForex(self.pairs[i], Resolution.Minute)
            self.AddForex(str(self.pairs[i]), self.my_resolution, Market.Oanda)
            # self.AddForex(str(self.pairs[i]), Resolution.Minute)
            
            # initialize dicts for positions as all 0
            self.next_positions[self.pairs[i]] = 0
            self.bars_since_entry[self.pairs[i]] = 0
            self.ATRs[self.pairs[i]] = 0 #self.ATR(self.pairs[i], self.atr_period)
            # self.ATRs[self.pairs[i]] = self.ATR(self.pairs[i], self.atr_period)
            self.last_stop_prices[self.pairs[i]] = 0
            self.next_position_entry[self.pairs[i]] = 0
            self.current_positions[self.pairs[i]] = 0
            self.next_position_sizes[self.pairs[i]] = 0
        
        
        # self.RemoveSecurity('SPY')
        
        self.in_position = False
        
        # TODO: add warmup period
        # self.SetWarmUp(self.lookback_period+10)
        # self.SetWarmUp
        self.close_prices = pd.DataFrame(np.zeros((self.long_period, len(self.pairs))), columns=self.pairs)
        self.high_prices = pd.DataFrame(np.zeros((self.long_period, len(self.pairs))), columns=self.pairs)
        self.low_prices = pd.DataFrame(np.zeros((self.long_period, len(self.pairs))), columns=self.pairs)
        # self.open_prices = pd.DataFrame(np.zeros((self.long_period, len(self.pairs))), columns=self.pairs)
        
        self.true_ranges = pd.DataFrame(np.zeros((self.long_period, len(self.pairs))), columns=self.pairs)
        
        self.Debug("Algo Initialized")
        self.counter = 0
        
        self.warmup_timer = 0
        
        self.debug_flag = False
        
        self.larger_tp = True
        
        self.reverse_strategy = False
        
        if self.reverse_strategy:
            self.position_mult = -1
        else:
            self.position_mult = 1


    def OnData(self, slice):
        # self.RemoveSecurity('SPY')
        
        # closes
        new_closes = pd.DataFrame(np.zeros(len(self.pairs))).T
        new_closes.columns = self.pairs
        
        # highs
        new_highs = pd.DataFrame(np.zeros(len(self.pairs))).T
        new_highs.columns = self.pairs
        
        # lows
        new_lows = pd.DataFrame(np.zeros(len(self.pairs))).T
        new_lows.columns = self.pairs
        
        # # opens
        # new_opens = pd.DataFrame(np.zeros(len(self.pairs))).T
        # new_opens.columns = self.pairs
        
        for security in self.pairs:

            # Note: slice[security].Close is of type decimal.Decimal which is causing some troubles
            try:
                new_closes[security].iloc[0] = np.float(slice[str(security)].Close)
                new_highs[security].iloc[0] = np.float(slice[str(security)].High)
                new_lows[security].iloc[0] = np.float(slice[str(security)].Low)
            except:
                self.Debug("No data for {}".format(security))
                new_closes[security].iloc[0] = self.close_prices[security].iloc[-1]
                new_highs[security].iloc[0] = self.high_prices[security].iloc[-1]
                new_lows[security].iloc[0] = self.low_prices[security].iloc[-1]
            # new_opens[security].iloc[0] = np.float(slice[str(security)].Open)
            
            # update ATR
            # if not self.debug_flag:
                # self.Debug(str(inspect.getargspec(self.ATRs[security].Update)))
                # self.Debug(inspect.getargspec(self.ATRs[security].ComputeNextValue))
                # self.debug_flag = True
            # self.ATRs[security].Update()
            
        # then fix the index before appending
        # """
        # new_closes.index = [self.close_prices.shape[0]]
        # new_highs.index = [self.high_prices.shape[0]]
        # new_lows.index = [self.low_prices.shape[0]]
        # new_opens.index = [self.open_prices.shape[0]]
        
        #preventing over usage of memory
        new_data_closes = self.close_prices.append(new_closes, ignore_index=True)#.iloc[-self.long_period:,:]
        new_data_highs = self.high_prices.append(new_highs, ignore_index=True)#.iloc[-self.long_period:,:]
        new_data_lows = self.low_prices.append(new_lows, ignore_index=True)#.iloc[-self.long_period:,:]
        # new_data_opens = self.open_prices.append(new_opens).iloc[-self.long_period:,:]
        
        del self.close_prices
        del self.high_prices
        del self.low_prices
        # del self.open_prices
        
        # new_data_closes.index = np.arange(new_data_closes.shape[0])
        # new_data_highs.index = np.arange(new_data_highs.shape[0])
        # new_data_lows.index = np.arange(new_data_lows.shape[0])
        # new_data_opens.index = np.arange(new_data_opens.shape[0])
        
        # trim length if needed
        if new_data_closes.shape[0] > 2*self.atr_period and self.atr_period > self.long_period:
            new_data_closes.drop(np.arange(self.atr_period), inplace=True)
            new_data_highs.drop(np.arange(self.atr_period), inplace=True)
            new_data_lows.drop(np.arange(self.atr_period), inplace=True)
            # new_data_opens.drop(np.arange(self.atr_period), inplace=True)
            
            new_data_closes.index = np.arange(new_data_closes.shape[0])
            new_data_highs.index = np.arange(new_data_highs.shape[0])
            new_data_lows.index = np.arange(new_data_lows.shape[0])
            # new_data_opens.index = np.arange(new_data_opens.shape[0])
        elif new_data_closes.shape[0] > 2*self.long_period:
            new_data_closes.drop(np.arange(self.long_period), inplace=True)
            new_data_highs.drop(np.arange(self.long_period), inplace=True)
            new_data_lows.drop(np.arange(self.long_period), inplace=True)
            # new_data_opens.drop(np.arange(self.long_period), inplace=True)
            
            new_data_closes.index = np.arange(new_data_closes.shape[0])
            new_data_highs.index = np.arange(new_data_highs.shape[0])
            new_data_lows.index = np.arange(new_data_lows.shape[0])
            # new_data_opens.index = np.arange(new_data_opens.shape[0])
        
        self.close_prices = new_data_closes
        self.high_prices = new_data_highs
        self.low_prices = new_data_lows
        # self.open_prices = new_data_opens

        
        self.warmup_timer += 1
        
        # calculate true range
        self.calc_true_range()
        
        if self.warmup_timer > self.long_period:
            # Call necessary trading functions
            
            # FOR DEBUG
            # if not self.in_position:
            #     self.SetHoldings("EURUSD", 0.1)
            #     self.in_position = True
                        
            # calculate atr
            self.calc_atr_trail()
            
            # calc new positions
            self.perform_trade_logic()
            
            # update Portfolio equity
            self.calc_equity()
            
            # calculate position sizes
            self.calc_next_position_sizes()
            
            # execute new positions
            self.execute_trades()
            
                    
        # """
        
    def calc_equity(self):
        self.equity = np.float(self.Portfolio.TotalPortfolioValue)
        
    def calc_next_position_sizes(self):
        # TODO: calculate either all position sizes, or individual pos sizes
        # self.Debug(str(self.counter)+": "+str(self.equity))
        # self.counter += 1
        
        for security in self.pairs:
            if not self.debug_flag:
                # self.Debug("Debugging Portfolio")
                # t = ""
                # dirs = dir(self.Securities[security].SymbolProperties)#.SymbolProperties)
                # for i in len(dirs):
                #     t += ", "+dirs[i]
                #     if i % 10 == 0 or i == len(dirs) -1:
                #         self.Debug(t)
                #         t = ""
                
                # self.Debug("hello")
                # self.Debug(str(self.Securities["GBPJPY"].QuoteCurrency.ConversionRate))
                
                # self.debug_flag = True
                
                if self.next_positions[security] == 0:
                    self.next_position_sizes[security] = 0
                else:
                    # get lot size in case other broker's only offer round lots
                    # Oanda allows for 1 unit lot sizes so this isn't necessary with Oanda
                    lot_size = np.float(self.Securities[security].SymbolProperties.LotSize)
                    # conversion rate for USD
                    conversion_rate = np.float(self.Securities[security].QuoteCurrency.ConversionRate)
                    point_value = lot_size * conversion_rate
                    
                    distance_to_stop = self.ATRs[security]*self.atr_trail_mult
                    
                    desired_pct_val = self.pct_portfolio_risk * self.equity
                    
                    if distance_to_stop == 0:
                        self.Debug(security+" distance is 0: "+str(distance_to_stop))
                        self.Debug("ATR is "+str(self.ATRs[security]))
                        self.Debug("ATR trail mult is "+str(self.atr_trail_mult))
                    if point_value == 0:
                        self.Debug(security+" point value is 0: "+str(point_value))
                    
                    if distance_to_stop == 0 or point_value == 0:
                        self.next_position_sizes[security] = 0
                    else:
                        self.next_position_sizes[security] = int(desired_pct_val / (distance_to_stop * point_value))
                    
        
    def calc_true_range(self):
        close_to_highs = (self.close_prices.iloc[-2,:] - self.high_prices.iloc[-1,:]).abs()
        close_to_lows = (self.close_prices.iloc[-2,:] - self.low_prices.iloc[-1,:]).abs()
        new_true_ranges = close_to_highs.where(close_to_highs > close_to_lows, close_to_lows)
        
        new_TR_df = self.true_ranges.append(new_true_ranges, ignore_index=True)
        del self.true_ranges
        self.true_ranges = new_TR_df
        
        # trim length if needed
        if self.true_ranges.shape[0] > 2*self.atr_period and self.atr_period > self.long_period:
            self.true_ranges.drop(np.arange(self.atr_period), inplace=True)
            self.true_ranges.index = np.arange(self.true_ranges.shape[0])
        elif self.true_ranges.shape[0] > 2*self.long_period:
            self.true_ranges.drop(np.arange(self.long_period), inplace=True)
            self.true_ranges.index = np.arange(self.true_ranges.shape[0])
        
    def calc_atr_trail(self):
        # calc and update ATRs
        for security in self.pairs:
        
            self.ATRs[security] = self.true_ranges[security].iloc[-self.atr_period:].mean()
            
            # if security == "GBPJPY" and self.ATRs[security] == 0:
            if self.ATRs[security] == 0:
                self.Debug("Debugging {} ATR".format(security))
                self.Debug(str(self.true_ranges[security].tail()))
                self.Debug(str(self.counter)+": And ATR is: "+str(self.ATRs[security]))
            
            # if security == "GBPJPY":
            #     self.counter += 1
            
            # self.ATRs[security] = np.float(self.ATR(security, self.atr_period))
            
            # For long positions
            if self.Portfolio[security].IsLong:
                current_atr_pos = self.high_prices[security].iloc[-1] - self.ATRs[security]*self.atr_trail_mult # np.float(self.atr_trail_mult*self.ATRs[security].Current.Value)
                if not self.last_stop_prices[security] == 0:
                    if current_atr_pos > self.last_stop_prices[security]:
                        self.last_stop_prices[security] = current_atr_pos
                else:
                    self.last_stop_prices[security] = current_atr_pos
            # For Short positions
            elif self.Portfolio[security].IsShort:
                current_atr_pos = self.low_prices[security].iloc[-1] + self.ATRs[security]*self.atr_trail_mult # np.float(self.atr_trail_mult*self.ATRs[security].Current.Value)
                if not self.last_stop_prices[security] == 0:
                    if current_atr_pos < self.last_stop_prices[security]:
                        self.last_stop_prices[security] = current_atr_pos
                else:
                    self.last_stop_prices[security] = current_atr_pos
            else:
                # no current position
                self.last_stop_prices[security] = 0
        
    def execute_trades(self):
        # TODO: loop through pairs and execute new positions
        for security in self.pairs:
            if self.next_positions[security] == 0 and np.float(self.Portfolio[security].Quantity) != 0:
                self.SetHoldings(security, 0.0)
                self.current_positions[security] = self.next_positions[security]
            elif self.next_positions[security] != 0 and \
            self.Portfolio[security].Quantity != self.next_positions[security]*self.next_position_sizes[security]:
                self.MarketOrder(security, self.next_positions[security]*self.next_position_sizes[security] - self.Portfolio[security].Quantity)
                # self.SetHoldings(security, self.size*self.position_mult)
                self.current_positions[security] = self.next_positions[security]
            # elif self.next_positions[security] < 0 and self.next_positions[security] != self.current_positions[security]:
            #     self.MarketOrder(security, (self.next_positions[security]*self.size - self.Portfolio[security].Quantity)*self.position_mult)
            #     # self.SetHoldings(security, -self.size*self.position_mult)
            #     self.current_positions[security] = self.next_positions[security]
                
        
    def perform_trade_logic(self):
        # Debug a little, need to determine why only trading last security in self.pairs
        
        for security in self.pairs:
            # trade logic
            # TODO: calculate new position states
            
            # For enter long positions
            if not self.Portfolio[security].IsLong and \
            self.close_prices[security].iloc[-1] == self.high_prices[security].iloc[-self.long_period:].max():
                self.next_positions[security] = 1
                # for multiple entries
                self.next_position_entry[security] = self.close_prices[security].iloc[-1] + self.atr_entry_mult*self.ATRs[security]
                
            # for entering additional LONG positions
            elif self.Portfolio[security].IsLong and self.close_prices[security].iloc[-1] > self.next_position_entry[security] and \
            self.next_positions[security] + 1 <= self.pos_max_num:
                self.next_positions[security] += 1
                self.next_position_entry[security] = self.close_prices[security].iloc[-1] + self.atr_entry_mult*self.ATRs[security]
                
            # for entering additional SHORT positions
            elif self.Portfolio[security].IsShort and self.close_prices[security].iloc[-1] < self.next_position_entry[security] and \
            self.next_positions[security] - 1 >= (-1)*self.pos_max_num:
                self.next_positions[security] += 1
                self.next_position_entry[security] = self.close_prices[security].iloc[-1] - self.atr_entry_mult*self.ATRs[security]
                
            # For enter short positions
            elif not self.Portfolio[security].IsShort and \
            self.close_prices[security].iloc[-1] == self.low_prices[security].iloc[-self.long_period:].min():
                self.next_positions[security] = -1
                # for multiple entries
                self.next_position_entry[security] = self.close_prices[security].iloc[-1] - self.atr_entry_mult*self.ATRs[security]
                
                
            # Exit short positions:
            elif self.Portfolio[security].IsShort and \
            self.close_prices[security].iloc[-1] > self.last_stop_prices[security]:
                self.next_positions[security] = 0
                
                self.next_position_entry[security] = 0
            
            # Exit long positions
            elif self.Portfolio[security].IsLong and \
            self.close_prices[security].iloc[-1] < self.last_stop_prices[security]:
                self.next_positions[security] = 0
                
                self.next_position_entry[security] = 0