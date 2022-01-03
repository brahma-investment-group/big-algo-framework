import dash
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html
from strategies.all_strategy_files.database.database import createDB
import time
import pandas as pd

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

db = createDB("market_data", "../strategies/all_strategy_files/data/config.ini")
time.sleep(1)

# open_positions = pd.read_sql_query(
#             f"select * from orb LEFT OUTER JOIN orb ON orb.profit_order_id = order_id WHERE orb.status IN ('Open');", con=db)


tp_df = pd.read_sql_query(f"select * from orb LEFT OUTER JOIN orders ON orb.profit_order_id = order_id;", con=db)
sl_df = pd.read_sql_query(f"select * from orb LEFT OUTER JOIN orders ON orb.stoploss_order_id = order_id;", con=db)
entry_df = pd.read_sql_query(f"select * from orb LEFT OUTER JOIN orders ON orb.parent_order_id = order_id;", con=db)

# open_positions = pd.concat([open_positions]*3, ignore_index=True)

rows = []
for ind in entry_df.index:
    first_card = dbc.Card(
        dbc.CardBody(
            [
                html.H5("Trade Details", className="card-title"),
                html.P("Ticker: " '{}'.format(entry_df.iloc[ind]['cont_ticker'])),
                html.P("Asset: " '{}'.format(entry_df.iloc[ind]['sec_type'])),
                html.P("Exp. Date: " '{}'.format(entry_df.iloc[ind]['cont_date'])),
                html.P("Strike: " '{}'.format(entry_df.iloc[ind]['strike'])),
                html.P("Right: " '{}'.format(entry_df.iloc[ind]['opt_right'])),
                html.P("Entry Price: " '{}'.format(entry_df.iloc[ind]['entry_price'])),
                html.P("SL Price: " '{}'.format(entry_df.iloc[ind]['sl_price'])),
                html.P("TP1 Price: " '{}'.format(entry_df.iloc[ind]['tp1_price'])),
                html.P("TP2 Price: " '{}'.format(entry_df.iloc[ind]['tp2_price'])),
                html.P("Risk: " '{}'.format(entry_df.iloc[ind]['risk_share'])),
                html.P("Time Frame: " '{}'.format(entry_df.iloc[ind]['timeframe'])),
            ]
        )
    )

    second_card = dbc.Card(
        dbc.CardBody(
            [
                html.H5("Entry", className="card-title"),
                html.P("Time: " '{}'.format(entry_df.iloc[ind]['time'])),
                html.P("Shares: " '{}'.format(entry_df.iloc[ind]['shares'])),
                html.P("Price: " '{}'.format(entry_df.iloc[ind]['price'])),
                html.P("Commission: " '{}'.format(entry_df.iloc[ind]['commission'])),
            ]
        )
    )

    third_card = dbc.Card(
        dbc.CardBody(
            [
                html.H5("Take Profit", className="card-title"),
                html.P("Time: " '{}'.format(tp_df.iloc[ind]['time'])),
                html.P("Shares: " '{}'.format(tp_df.iloc[ind]['shares'])),
                html.P("Price: " '{}'.format(tp_df.iloc[ind]['price'])),
                html.P("Commission: " '{}'.format(tp_df.iloc[ind]['commission'])),
                html.P("Profit: " '{}'.format(tp_df.iloc[ind]['realized_pnl'])),
            ]
        )
    )

    fourth_card = dbc.Card(
        dbc.CardBody(
            [
                html.H5("Stop Loss", className="card-title"),
                html.P("Time: " '{}'.format(sl_df.iloc[ind]['time'])),
                html.P("Shares: " '{}'.format(sl_df.iloc[ind]['shares'])),
                html.P("Price: " '{}'.format(sl_df.iloc[ind]['price'])),
                html.P("Commission: " '{}'.format(sl_df.iloc[ind]['commission'])),
                html.P("Loss: " '{}'.format(sl_df.iloc[ind]['realized_pnl'])),
            ]
        )
    )


    x = dbc.Row(
        [
            dbc.Col(first_card, width=3),
            dbc.Col(second_card, width=3),
            dbc.Col(third_card, width=3),
            dbc.Col(fourth_card, width=3),
        ]
    )

    rows.append(x)

title = html.H2("Trades", className="display-4", style=CONTENT_STYLE)

# app.layout = html.Div(html.Div(children=title), children=rows )


app.layout = html.Div(children=[
    html.H1(children=title),
    html.Div(children=rows),
])
if __name__ == '__main__':
    app.run_server(debug=True)