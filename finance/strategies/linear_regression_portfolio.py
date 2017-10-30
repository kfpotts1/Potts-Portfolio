"""
Linear Regression Portfolio

Created by Kenneth Potts

This is an algorithm written for the Zipline backtest and live trading platform created by Quantopian.
It is still under development and I have many other versions of this in the works. If you have
advise or feedback on this algorithm pla
"""
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters.morningstar import Q1500US, Q500US
from talib import RSI, ATR
import numpy as np
import pandas as pd
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
 
def initialize(context):
    """
    Called once at the start of the algorithm.
    """   
    # Rebalance every day, 1 hour after market open.
    # schedule_function(my_rebalance, date_rules.every_day(), time_rules.market_open(hours=1))
     
    # Record tracking variables at the end of each day.
    schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())
    
    
    ##### HYPER PARAMS #####
    context.run_ETFs = False
    context.r_squared_filter = True
    context.r_squared_cutoff = 0.02
    # context.single_asset = "QQQ"
    context.even_weights = True
    
    context.short_period = 7
    context.long_period = 21
    context.rsi_period = 12
    context.atr_period = 12
    
    context.data_lookback = 150
    context.history_frequency = '1d'
    context.target_look_forward_period = 1
    
    context.max_tree_depth = 12 # None # none for no restriction
    context.n_estimators = 500 # number of trees in ensemble forest
    context.full_data_model = True # filter for training on all available data after test score is verifited.
    ########################
    
    # will record the ml models
    context.models = {}
    context.best_model_securities = []
    context.r_squared = None
    
    context.month = -1
    
    if context.history_frequency == '1d':
        # Rebalance every day, 1 hour after market open.
        schedule_function(my_rebalance, date_rules.every_day(), time_rules.market_open(hours=1))
    
    
    
    # Create our dynamic stock selector.
    attach_pipeline(make_pipeline(), 'my_pipeline')
         
def make_pipeline():
    """
    A function to create our dynamic stock selector (pipeline). Documentation on
    pipeline can be found here: https://www.quantopian.com/help#pipeline-title
    """
    
    # Base universe set to the Q500US
    base_universe = Q1500US()

    return Pipeline(screen=base_universe)

def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.output = pipeline_output('my_pipeline')
  
    # These are the securities that we are interested in trading each day.
    context.security_list = np.array(context.output.index)
    
    # Remove after debugging
    if context.run_ETFs:
        # context.security_list = np.array([symbol('QQQ')])
        load_symbols(context)
    
    if context.month == -1 or context.month != get_datetime("US/Eastern").month:
        context.month = get_datetime('US/Eastern').month
        my_train_models(context, data)

    
    # if get_datetime('US/Eastern').weekday()==0:
    #     log.info("Monday, time to train up...")
    #     my_train_models(context, data)

            
def get_features(data_history, security, context, data):
    security_data = pd.DataFrame()

    # inputs = {
    #     'open': data_history['open'][security].values,
    #     'high': data_history['high'][security].values,
    #     'low': data_history['low'][security].values,
    #     'close': data_history['close'][security].values,
    #     'volume': data_history['volume'][security].values
    # }

    # MAKE FEATURES

    security_data["1_lag_returns"] = data_history['close'][security].pct_change()
    
    rsi_df = pd.DataFrame(index=data_history['close'][security].index,columns=[security])
    rsi_df[security] = RSI(data_history['close'][security].values, context.rsi_period)
    security_data['rsi'] = rsi_df[security]
    
    atr_df = pd.DataFrame(index=data_history['close'][security].index,columns=[security])
    atr_df[security] = ATR(data_history['high'][security].values, 
                           data_history['low'][security].values, 
                           data_history['close'][security].values,
                           context.atr_period)
    security_data['atr'] = atr_df[security]


    security_data['price_volatility_ratio'] = data_history['close'][security].rolling(context.short_period).std() / data_history['close'][security].rolling(context.long_period).std()

    security_data['ema_distance'] = (data_history['close'][security] - data_history['close']                                                        [security].rolling(context.short_period).mean()) / data_history['close'][security].rolling(context.long_period).mean()

    security_data['std_per_contract'] = data_history['close'][security].rolling(context.long_period).std() / data_history['volume'][security]

    security_data['volume_volatility_ratio'] = data_history['volume'][security].rolling(context.short_period).std() / data_history['volume'][security].rolling(context.long_period).std()

    security_data['volume_ratio'] = data_history['volume'][security].rolling(context.short_period).mean() / data_history['volume'][security].rolling(context.long_period).mean()
    
    security_data['distance_from_max'] = data_history['high'][security].rolling(context.long_period).max() - data_history['close'][security]
    security_data['distance_from_min'] = data_history['close'][security] - data_history['low'][security].rolling(context.long_period).min()

    # CALCULATE TARGETS

    security_data[str(context.target_look_forward_period)+'_forward_return'] = ((data_history['close'][security].shift((-1)*context.target_look_forward_period - 1) - data_history['close'][security].shift(-1)) / data_history['close'][security].shift(-1))

    # TODO: create indicator features, multiple period trailbacks for pattern detection
    
    # drop the NANs in the data from calculations
    security_data.dropna(inplace=True)
    
    # TODO: get training and testing data

    X = security_data.iloc[:,:-1].values
    y = security_data.loc[:,str(context.target_look_forward_period)+'_forward_return'].values

    return X, y

def get_latest_data_point(data_history, security, context, data):
    security_data = pd.DataFrame()
    
    security_data["1_lag_returns"] = data_history['close'][security].pct_change()
    
    rsi_df = pd.DataFrame(index=data_history['close'][security].index,columns=[security])
    rsi_df[security] = RSI(data_history['close'][security].values, context.rsi_period)
    security_data['rsi'] = rsi_df[security]
    
    atr_df = pd.DataFrame(index=data_history['close'][security].index,columns=[security])
    atr_df[security] = ATR(data_history['high'][security].values, 
                           data_history['low'][security].values, 
                           data_history['close'][security].values,
                           context.atr_period)
    security_data['atr'] = atr_df[security]

    security_data['price_volatility_ratio'] = data_history['close'][security].rolling(context.short_period).std() / data_history['close'][security].rolling(context.long_period).std()

    security_data['ema_distance'] = (data_history['close'][security] - data_history['close']                                                        [security].rolling(context.short_period).mean()) / data_history['close'][security].rolling(context.long_period).mean()

    security_data['std_per_contract'] = data_history['close'][security].rolling(context.long_period).std() / data_history['volume'][security]

    security_data['volume_volatility_ratio'] = data_history['volume'][security].rolling(context.short_period).std() / data_history['volume'][security].rolling(context.long_period).std()

    security_data['volume_ratio'] = data_history['volume'][security].rolling(context.short_period).mean() / data_history['volume'][security].rolling(context.long_period).mean()
    
    security_data['distance_from_max'] = data_history['high'][security].rolling(context.long_period).max() - data_history['close'][security]
    security_data['distance_from_min'] = data_history['close'][security] - data_history['low'][security].rolling(context.long_period).min()


    # TODO: create indicator features, multiple period trailbacks for pattern detection
    
    
    # TODO: get training and testing data
    security_data.dropna(inplace=True)
    X = security_data.iloc[-1,:].values
    
    # if np.nan in X:
    #     log.info("found a nan")

    return X
    
def my_train_models(context, data):
    
    del context.best_model_securities
    

        # TODO: get historical price and volume data for each asset in context.security_list
    data_history = data.history(context.security_list, fields=['open','high','low','close','volume'], bar_count=context.data_lookback, frequency=context.history_frequency)
    
    # initialize r-squared values to -infinity
    r_squared = np.full(len(context.security_list), -np.inf)

    for i in range(len(context.security_list)): # or security in context.security_list:
        X, y = get_features(data_history, context.security_list[i], context, data)
        split_row = int(X.shape[0]*0.6666)
        x_tr = X[:split_row,:]
        x_te = X[split_row:,:]
        y_tr = y[:split_row]
        y_te = y[split_row:]

        model = LinearRegression()
        # Fit the model
        # log.info("Training RandomForestRegressor for {0}".format(context.security_list[i]))
        # model.fit(x_tr, y_tr)
        if context.r_squared_filter:
            my_flag = True
            try:
                model.fit(x_tr, y_tr)
            except Exception as e:
                log.info(str(e))
                log.info("Shape of X data is: "+str(x_tr.shape))
                log.info("asset is: {0}".format(context.security_list[i].symbol))
                my_flag = False


            if my_flag:
                score = model.score(x_te, y_te)
            else:
                score = -np.inf
            # log.info("{0} model scored an r-squared of: {1}".format(context.security_list[i], score))


            if context.full_data_model:
                if score > context.r_squared_cutoff:
                    # retrain model on full data
                    model.fit(X, y)
            # record r-squared values
            r_squared[i] = score
        else:
            # model.fit(X, y)
            try:
                model.fit(X, y)
            except Exception as e:
                log.info(str(e))
                log.info("Shape of X data is: "+str(x_tr.shape))
                log.info("asset is: {0}".format(context.security_list[i].symbol))
                my_flag = False
        
        context.models[context.security_list[i]] = model
    
    
    # sorted_r_squarednp.argmax(r_squared)
    if not context.r_squared_filter:
        context.best_model_securities = context.security_list
        context.r_squared = r_squared
    else:
        context.best_model_securities = context.security_list[r_squared > context.r_squared_cutoff]
        context.r_squared = r_squared[r_squared > context.r_squared_cutoff]

def my_assign_weights(context, data):
    """
    Assign weights to securities that we want to order.
    """
    pass
 
def my_rebalance(context,data):
    """
    Execute orders according to our schedule_function() timing. 
    """
    for security in context.portfolio.positions.keys():
        if security not in context.best_model_securities:
            order_target_percent(security, 0.0)
    
    if len(context.best_model_securities) > 0:
        # weight = 1.0 / len(context.best_model_securities)

        max_lookback_required = np.max([context.long_period, context.atr_period, context.rsi_period]) + 1

        data_history = data.history(context.best_model_securities, fields=['open','high','low','close','volume'], bar_count=max_lookback_required, frequency=context.history_frequency)
        
        predictions = np.zeros(len(context.best_model_securities))
        for i in range(len(context.best_model_securities)):
            if len(get_open_orders(context.best_model_securities[i])) == 0:
                X = get_latest_data_point(data_history, context.best_model_securities[i], context, data)
                # if X.shape == (0,7):
                #     X = X.T
                
                if np.isnan(X).sum() == 0:# and X.shape != (0,7):
                    try:
                        prediction = context.models[context.best_model_securities[i]].predict(X.astype(np.float32))
                        predictions[i] = prediction
                    except:
                        predictions[i] = 0.0
                        log.info("prediction failed")
        
        if context.r_squared_filter and not context.even_weights:
            predictions = predictions * context.r_squared
        weight_total = np.abs(predictions).sum()
        for i in range(len(context.best_model_securities)):
            
            try:
                # if predictions[i] > 0:
                order_target_percent(context.best_model_securities[i], predictions[i]/weight_total)
            except:
                log.info("weight total is: {0}".format(weight_total))
                log.info("prediction is: {0}".format(predictions[i]))
 
def my_record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    record(num_securities=len(context.best_model_securities))
    record(Leverage = context.account.leverage)
    record(Exposure = context.account.net_leverage)
    
    
def handle_data(context,data):
    """
    Called every minute.
    """
    if context.history_frequency == '1m':
        my_rebalance(context, data)
        
def load_symbols(context):
    context.equities = symbols(
        # Equity
        'DIA',    # Dow
        'QQQ',    # NASDAQ
        # 'SPY',    # S&P 500
    )
    context.fixedincome = symbols(
        # Fixed income
        'LQD',    # Corporate bond
        'HYG',    # High yield
    )
    context.alternative = symbols(
        'USO',    # Oil
        'GLD',    # Gold
        'VNQ',    # US Real Estate
        'RWX',    # Dow Jones® Global ex-U.S. Select Real Estate Securities Index
        'UNG',    # Natual gas
        'DBA',    # Agriculture
        'FXE',    # EURO ETF
        'FXB',    # British Pound ETF
    )
    context.security_list = np.array(context.equities + context.fixedincome + context.alternative)
    
    