
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Principal OrderBook and Public Trades metrics calculation and visualization                -- #
# -- visualizations.py : It's a python script with data visualization functions                          -- #
# -- author: @bmanica                                                                                    -- #
# -- license: GNU General Public License v3.0                                                            -- #
# -- repository: https://github.com/bmanica/obmetrics-lab1.git                                           -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# ====================================== Requierd packages ================================================ #

### Libraries to use
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ===================================== OrderBook bar plot ================================================ #

### Function definition
def plot_orderbook(ob_data_df,
                   depth):

    # First define data structure
    bid = ob_data_df['bid_size'][:depth].tolist()
    ask = ob_data_df['ask_size'][:depth].tolist()

    # Chart definition
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True,
                        subplot_titles=("Bid size", "Ask size"),
                        horizontal_spacing=0)

    # Traces
    fig.add_trace(
        go.Bar(name='Bid size', x=[str(i) for i in np.arange(1, len(bid) + 1).tolist()[::-1]],
               y=bid[::-1],
               marker={'color': '#15569B'}), row=1, col=1)

    fig.add_trace(
        go.Bar(name='Ask size', x=[str(i) for i in np.arange(1, len(ask) + 1).tolist()],
               y=ask,
               marker={'color': '#C22911'}), row=1, col=2)

    # Plot configurations
    fig.update_layout(barmode='group', height=500,
                      font_family='Oswald, sans-serif', title_text='<b>Limit Orderbook Chart<b>')
    fig['layout']['title']['font'] = dict(size=19)
    fig.update_yaxes(title_text='Volume', row=1, col=1)
    fig.update_xaxes(title_text='Orderbook depth')
    fig.layout.annotations[0].update(y=1.03)
    fig.layout.annotations[1].update(y=1.03)

    return fig

# =================================== PublicTrades bar-line plot ========================================== #

### Function definition
def plot_publictrades(pt_data,
                      hours):

    # Data preparation
    # Each change in 0.01 USD
    changes = pd.cut(pt_data["price"], bins=np.arange(min(pt_data.price), max(pt_data.price), 0.01),
                     right=False).cat.codes
    pt_data['time'] = pd.to_datetime(pt_data.index.values.tolist()) # Time for sorting

    plot_data = pt_data.groupby((changes!=changes.shift(1)).cumsum()).agg(
                                {'time': 'max', "price": "max", "amount": "sum"})

    plot_data['hour'] = [i.hour for i in pd.to_datetime(plot_data['time'])]
    plot_data.sort_values(by='time', inplace=True)

    final_data = plot_data[plot_data.hour <= (0+hours)-1]

    # Plot definition
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_heights=[0.75,0.25])

    fig.add_trace(
        go.Line(name='Traded price', x=final_data['time'],
                                     y=final_data.price,
                                     marker={'color': '#B2B641'}), row=1, col=1)

    fig.add_trace(
        go.Bar(name='Traded volume', x=final_data['time'],
                                     y=final_data.amount,
                                     marker={'color': '#050505'}), row=2, col=1)

    fig.update_layout(barmode='group',
                      font_family='Oswald, sans-serif', title_text='<b>Public Trades Chart<b>')
    fig['layout']['title']['font'] = dict(size=19)
    fig.update_yaxes(title_text='Prices in USD', row=1, col=1)
    fig.update_yaxes(title_text='Volume', row=2, col=1)
    fig.update_xaxes(title_text='Time', row=2, col=1)
    fig.update_traces(marker_color='black',
                      marker_line_color='black',
                      selector=dict(type="bar"))

    return fig

