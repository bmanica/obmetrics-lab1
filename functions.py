
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Principal OrderBook and Public Trades metrics calculation and visualization                -- #
# -- functions.py : It's a python script with general functions for key metrics obtention                -- #
# -- author: @bmanica                                                                                    -- #
# -- license: GNU General Public License v3.0                                                            -- #
# -- repository: https://github.com/bmanica/obmetrics-lab1.git                                           -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# ====================================== Requierd packages ================================================ #

### Libraries to use
import pandas as pd
import numpy as np
import scipy.stats as st

# ======================================= OrderBook metrics function ====================================== #

### Function definition
def get_ob_metrics(ob_data, depth=None):

    # -- General lambda functions definition -- #
    calc_inbalace = lambda b,a,d: np.sum(b[:d]) / np.sum(np.add(b[:d],a[:d]))
    data_adder = lambda each_list,values: each_list.append(values)
    w_mid = lambda b,bv,a,av,d: (bv[:d]/np.add(bv[:d],av[:d]))*a[:d] + (av[:d]/np.add(bv[:d],av[:d]))*b[:d]
    calc_vwap = lambda b,bv,a,av,d: (b[:d]*bv[:d] + a[:d]*av[:d]) / np.add(bv[:d],av[:d])

    # -- Non depth dependant metrics -- #
    # Median time of OrderBook to update
    times_ob = pd.to_datetime(pd.Series(list(ob_data.keys())))
    delta_median = np.median([times_ob[i+1] - times_ob[i]
                              for i in range(len(times_ob)-1)]).total_seconds()*1000

    # Price levels for each OrderBook
    price_levels = {j: [len(list(ob_data.values())[i])] for i, j in zip(range(len(list(ob_data.keys()))),
                                                                      ob_data.keys())}
    # Bid volume for each OrderBook
    bid_volume = {i: [round(ob_data[i]['bid_size'].sum(), 6)] for i in ob_data}

    # Ask volume for each OrderBook
    ask_volume = {i: [round(ob_data[i]['ask_size'].sum(), 6)] for i in ob_data}

    # Total volume for each OrderBook
    total_volume = np.add(list(bid_volume.values()), list(ask_volume.values())).round(6).tolist()
    total_volume = dict(zip(list(ob_data.keys()), total_volume))

    # OHLCV (Open, High, Low, Close, Volume)
    # Mid price and volume for OHLCV calcultation
    mid_ohlcv = {i: [(ob_data[i].iloc[0, :]['ask'] + ob_data[i].iloc[0, :]['bid']) * 0.5,
                     np.add(ob_data[i]['bid_size'], ob_data[i]['ask_size']).cumsum()[-1]]
                     for i in ob_data}

    ohlcv = pd.DataFrame.from_dict(mid_ohlcv).T
    ohlcv.columns = ['Midprice', 'Volume']
    ohlcv.index = pd.to_datetime(pd.Series(ohlcv.index.values.tolist()))
    ohlcv = ohlcv.resample('1min').agg({'Midprice': 'ohlc', 'Volume': 'sum'}) # Change per minute

    # -- Depth dependant metrics -- #
    if depth is None:

        # Spread, in this case defined just for top of the book
        spread = {i: [ob_data[i].iloc[0,:]['ask'] - ob_data[i].iloc[0,:]['bid']] for i in ob_data}

        # Mid price, in this case defined just for top of the book
        mid_price = {i: [(ob_data[i].iloc[0,:]['ask'] + ob_data[i].iloc[0,:]['bid']) * 0.5]
                     for i in ob_data}

        # OrderBook inbalance for each OrderBook, by default takes all
        ob_inbalance = {i: [calc_inbalace(ob_data[i]['bid_size'], ob_data[i]['ask_size'],
                                         len(ob_data[i]))] for i in ob_data}

        # Weighted midprice, default option top of the book
        weight_mid_a = {i: w_mid(ob_data[i]['bid'], ob_data[i]['bid_size'],
                                 ob_data[i]['ask'], ob_data[i]['ask_size'],1) for i in ob_data}

        # VWAP (Volume-Weigthed Average Price), in this section just top of the book
        ob_vwap = {i: calc_vwap(ob_data[i]['bid'], ob_data[i]['bid_size'],
                                ob_data[i]['ask'], ob_data[i]['ask_size'], 1)
                                for i in ob_data}

        # Stats momentums for OrderBook inbalance
        stats_m = {'median': [np.median(list(ob_inbalance.values()))],
                   'var': [np.var(list(ob_inbalance.values()))],
                   'skewness': st.skew(list(ob_inbalance.values())),
                   'kurtosis': st.kurtosis(list(ob_inbalance.values()))}

        # Return data definition
        r_dict = {'update_median':delta_median, 'price_levels':price_levels,
                  'bid_volume':bid_volume, 'ask_volume':ask_volume,
                  'total_volume':total_volume, 'spread':spread,
                  'midprice':mid_price, 'volume_inbalance':ob_inbalance,
                  'weighted_mid':weight_mid_a, 'vwap':ob_vwap,
                  'stats_moments':stats_m, 'ohlcv':ohlcv}

        return r_dict

    else:

        # Spread, in this case defined for the depth input
        spread = {i: [ob_data[i].iloc[0:depth,:]['ask'] - ob_data[i].iloc[0:depth,:]['bid']]
                  for i in ob_data}

        # Mid price, in this case defined for the depth input
        mid_price = {i: [(ob_data[i].iloc[0:depth,:]['ask'] + ob_data[i].iloc[0:depth,:]['bid']) * 0.5]
                     for i in ob_data}

        # OrderBook inbalance for each OrderBook, depth input
        ob_inbalance = {i: [calc_inbalace(ob_data[i]['bid_size'], ob_data[i]['ask_size'],
                                         depth)] for i in ob_data}

        # Weighted midprice, for depth input
        # First way to calculate
        weight_mid_a = {i: [w_mid(ob_data[i]['bid'], ob_data[i]['bid_size'],
                                 ob_data[i]['ask'], ob_data[i]['ask_size'], depth)] for i in ob_data}

        # Second way to calculate

        # VWAP (Volume-Weigthed Average Price), in this section just top of the book
        ob_vwap = {i: calc_vwap(ob_data[i]['bid'], ob_data[i]['bid_size'],
                                ob_data[i]['ask'], ob_data[i]['ask_size'], depth)
                   for i in ob_data}

        # Stats moments for OrderBook inbalance
        stats_m = {'median': [np.median(list(ob_inbalance.values()))],
                   'var': [np.var(list(ob_inbalance.values()))],
                   'skewness': [st.skew(list(ob_inbalance.values()))],
                   'kurtosis': [st.kurtosis(list(ob_inbalance.values()))]}

        # Return data definition
        r_dict = {'update_median':delta_median, 'price_levels':price_levels,
                  'bid_volume':bid_volume, 'ask_volume':ask_volume,
                  'total_volume':total_volume, 'spread':spread,
                  'midprice':mid_price, 'volume_inbalance':ob_inbalance,
                  'weighted_mid':weight_mid_a, 'vwap':ob_vwap,
                  'stats_moments':stats_m, 'ohlcv':ohlcv}

        return r_dict

# =================================== PublicTrades metrics function ======================================= #

### Function definition
def get_pt_metrics(pt_data):

    # -- Count metrics -- #
    pt_data['hour'] = [i.hour for i in pd.to_datetime(pt_data['timestamp'])] # Hour extract

    # Buy trade count
    buy_count = pt_data[pt_data.side=='buy'].pivot_table(values='price', index='hour', aggfunc='count')

    # Sell trade count
    sell_count = pt_data[pt_data.side=='sell'].pivot_table(values='price', index='hour', aggfunc='count')

    # Total trade count
    total_count = np.add(buy_count, sell_count)

    # Diff in trade count (buy-sell). If negatives means more sell than buy
    diff_count = np.subtract(buy_count, sell_count)

    # -- Volume metrics -- #
    # Buy volume
    buy_volume = pt_data[pt_data.side=='buy'].pivot_table(values='amount', index='hour', aggfunc='sum')

    # Sell volume
    sell_volume = pt_data[pt_data.side=='sell'].pivot_table(values='amount', index='hour', aggfunc='sum')

    # Total volume
    total_volume = np.add(buy_volume, sell_volume)

    # Diff in trade volume (buy-sell). If negatives means more operated volume in sell
    diff_volume = np.subtract(buy_volume, sell_volume)

    # OHLCV (Open, High, Low, Close, Volume): (Traded volume)
    ohlcv_data = pt_data
    ohlcv_data.index = pd.to_datetime(ohlcv_data.timestamp)
    ohlcv_data.drop(['timestamp', 'side', 'hour'], axis=1, inplace=True) # OHLCV prepared data

    ohlcv_data = ohlcv_data.resample('1h').agg({'price': 'ohlc', 'amount': 'sum'})

    # Statistical moments for diff volume
    stats_m = {'median': np.median(diff_volume),
               'var': np.var(diff_volume),
               'skewness': st.skew(diff_volume),
               'kurtosis': st.kurtosis(diff_volume)}

    # Return data definition
    r_dict = {'buy_count':buy_count, 'sell_count':sell_count,
              'total_count':total_count, 'diff_count':diff_count,
              'buy_volume':buy_volume, 'sell_volume':sell_volume,
              'total_volume':total_volume, 'diff_volume':diff_volume,
              'ohlcv':ohlcv_data, 'stats_moments':stats_m}

    return r_dict



