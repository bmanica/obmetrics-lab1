
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
def get_ob_metrics(ob_data,
                   depth):

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
    price_levels = {j: len(list(ob_data.values())[i]) for i, j in zip(range(len(list(ob_data.keys()))),
                                                                      ob_data.keys())}
    # Bid volume for each OrderBook
    bid_volume = {i: round(ob_data[i]['bid_size'].sum(), 6) for i in ob_data}

    # Ask volume for each OrderBook
    ask_volume = {i: round(ob_data[i]['ask_size'].sum(), 6) for i in ob_data}

    # Total volume for each OrderBook
    total_volume = np.add(list(bid_volume.values()), list(ask_volume.values())).round(6).tolist()
    total_volume = dict(zip(list(ob_data.keys()), total_volume))

    # OHLCV (Open, High, Low, Close, Volume)

    # -- Depth dependant metrics -- #
    if depth is None:

        # Spread, in this case defined just for top of the book
        spread = {i: ob_data[i].iloc[0,:]['ask'] - ob_data[i].iloc[0,:]['bid'] for i in ob_data}

        # Mid price, in this case defined just for top of the book
        mid_price = {i: (ob_data[i].iloc[0,:]['ask'] + ob_data[i].iloc[0,:]['bid']) * 0.5
                     for i in ob_data}

        # OrderBook inbalance for each OrderBook, by default takes all
        ob_inbalance = {i: calc_inbalace(ob_data[i]['bid_size'], ob_data[i]['ask_size'],
                                         len(ob_data[i])) for i in ob_data}

        # Weighted midprice, default option top of the book
        weight_mid_a = {i: w_mid(ob_data[i]['bid'], ob_data[i]['bid_size'],
                                 ob_data[i]['ask'], ob_data[i]['ask_size'],1) for i in ob_data}

        # VWAP (Volume-Weigthed Average Price), in this section just top of the book
        ob_vwap = {i: calc_vwap(ob_data[i]['bid'], ob_data[i]['bid_size'],
                                ob_data[i]['ask'], ob_data[i]['ask_size'], 1)
                                for i in ob_data}

        # Stats momentums for OrderBook inbalance
        stats_m = [np.mean(list(ob_inbalance.values())),
                   np.var(list(ob_inbalance.values())),
                   st.skew(list(ob_inbalance.values())),
                   st.kurtosis(list(ob_inbalance.values()))]

        # Return data definition
        r_dict = {'update_median':delta_median, 'price_levels':price_levels,
                  'bid_volume':bid_volume, 'ask_volume':ask_volume,
                  'total_volume':total_volume, 'volume_inbalance':ob_inbalance,
                  'weighted_mid':weight_mid_a, 'vwap':ob_vwap,
                  'stats_momentums':stats_m}

        return r_dict

    else:

        # Spread, in this case defined for the depth input
        spread = {i: ob_data[i].iloc[0:depth,:]['ask'] - ob_data[i].iloc[0:depth,:]['bid']
                  for i in ob_data}

        # Mid price, in this case defined for the depth input
        mid_price = {i: (ob_data[i].iloc[0:depth,:]['ask'] + ob_data[i].iloc[0:depth,:]['bid']) * 0.5
                     for i in ob_data}

        # OrderBook inbalance for each OrderBook, depth input
        ob_inbalance = {i: calc_inbalace(ob_data[i]['bid_size'], ob_data[i]['ask_size'],
                                         depth) for i in ob_data}

        # Weighted midprice, for depth input
        # First way to calculate
        weight_mid_a = {i: w_mid(ob_data[i]['bid'], ob_data[i]['bid_size'],
                                 ob_data[i]['ask'], ob_data[i]['ask_size'], depth) for i in ob_data}

        # Second way to calculate

        # VWAP (Volume-Weigthed Average Price), in this section just top of the book
        ob_vwap = {i: calc_vwap(ob_data[i]['bid'], ob_data[i]['bid_size'],
                                ob_data[i]['ask'], ob_data[i]['ask_size'], depth)
                   for i in ob_data}

        # Stats momentums for OrderBook inbalance
        stats_m = [np.mean(list(ob_inbalance.values())),
                   np.var(list(ob_inbalance.values())),
                   st.skew(list(ob_inbalance.values())),
                   st.kurtosis(list(ob_inbalance.values()))]

        # Return data definition
        r_dict = {'update_median':delta_median, 'price_levels':price_levels,
                  'bid_volume':bid_volume, 'ask_volume':ask_volume,
                  'total_volume':total_volume, 'volume_inbalance':ob_inbalance,
                  'weighted_mid':weight_mid_a, 'vwap':ob_vwap,
                  'stats_momentums':stats_m}

        return r_dict


