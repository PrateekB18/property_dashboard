# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 16:37:32 2022

@author: Prateek

Dashboard to view Greater Sydney property market stats
"""

import sqlite3
import numpy as np
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

google_api = "Add Google Map Embed API Here"

##### Fetching and Filtering Suburbs based on available Data ######

conn = sqlite3.connect('Suburb_names.db')
suburbs = pd.read_sql('SELECT * FROM [SubNames]' , conn)
conn = sqlite3.connect('Unit_data.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables1 = cursor.fetchall()
conn = sqlite3.connect('House_data.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables2 = cursor.fetchall()
all_tables = list( dict.fromkeys(tables1+tables2))

names = []
for table_name in all_tables:
        names.append(table_name[0])

key = []
for i, row in suburbs.iterrows():
    Sub = row['Locality']
    if Sub in names:
        key.append(1)
    else:
        key.append(0)

suburbs['Filter'] = key
suburbs.drop(suburbs[suburbs['Filter'] ==0].index, inplace = True)

###############

suburb_dict = dict(zip( suburbs['Locality']+ ' [' +suburbs['Postcode'].astype(str)+']' , '['+suburbs['Locality']+']'))

bedrooms = pd.DataFrame([['1 Bedroom', '1'],['2 Bedrooms', '2'],
                         ['3 Bedrooms', '3'],['4 Bedrooms', '4'],
                         ['5 Bedrooms', '5']],
                         columns=['Label', 'Value'])

parameters_dict = {'Median Sold Price':'[medianSoldPrice]', 'Highest Sold Price':'[highestSoldPrice]',
                   'Lowest Sold Price':'[lowestSoldPrice]', '5th Percentile Sold Price':'[5thPercentileSoldPrice]',
                   '25th Percentile Sold Price':'[25thPercentileSoldPrice]','75th Percentile Sold Price':'[75thPercentileSoldPrice]',
                   '95th Percentile Sold Price':'[95thPercentileSoldPrice]','Median Sale Listing Price':'[medianSaleListingPrice]',
                   'Highest Sale Listing Price':'[highestSaleListingPrice]','Lowest Sale Listing Price':'[lowestSaleListingPrice]',
                   'Median Rent Listing Price':'[medianRentListingPrice]','Highest Rent Listing Price':'[highestRentListingPrice]',
                   'Lowest Rent Listing Price':'[lowestRentListingPrice]'}

bed_dict = dict(zip(bedrooms['Label'], bedrooms['Value']))

type_dict = {"Apartment": "Unit", "House": "House"}

demo_dict = {'Weekly Rent':'Rent', 'Weekly Household Income':'Income',
             'Education':'Education','Occupation':'Occupation',
             'Modes of Transport to Work':'Transport',
             'Age':'Age','Marital Status':'MaritalStatus',
             'Country of Birth':'CountryOfBirth', 'Religion':'Religion',
             'Type of Occupancy':'Occupancy'}

app = dash.Dash(__name__,
                external_stylesheets=['custom.css', dbc.themes.BOOTSTRAP])

app.layout = html.Div([

    dbc.Row([dbc.Col(html.H2('Greater Sydney Property Market Dashboard',
                             style = {'font-family':"Candara",
                                           'font-size': '28px',
                                           "text-align": "center",
                                           "margin-top":"0%",
                                           "margin-bottom":"1%",
                                           "color":"#FFFFFF",
                                           "background-color": "#4F555A",
                                           "height": "90%",
                                           'box-shadow': '#4F555A 0px 0px 5px 0px, #4F555A 0px 0px 1px 0px'}))]),

    dbc.Row([
            dbc.Col([
            html.Div(children = [
                dbc.Row([
                    dbc.Col([ html.Label(['Select Suburb'],
                                         style={'font-family':"Candara",
                                                'font-size': '18px',
                                                "text-align": "center",
                                                "marginLeft":'5%',
                                                "margin-top":"2.5%"})])]),

                dbc.Row([
                    dcc.Dropdown(
                    id='dropdown1',
                    options=[{'label':label, 'value': value} for label,
                             value in suburb_dict.items()],
                    value = '[Alexandria]',
                    placeholder="Select Suburb",
                    multi=False,
                    style=dict(
                        verticalAlign="middle",
                        marginLeft ='2.5%',
                        width='95%',
                        )),
                    ]),

                dbc.Row([
                    dbc.Col([ html.Label(['Select Number of Bedrooms'],
                                         style={'font-family':"Candara",
                                                'font-size': '18px',
                                                "text-align": "center",
                                                "marginLeft":'5%',
                                                "margin-top":"2.5%"})])]),

                dbc.Row([
                    dbc.Col([ dcc.Dropdown(
                            id='dropdown2',
                            options=[{'label':label, 'value': value} for label, value in bed_dict.items()],
                            value = '2',
                            placeholder="Select Bedrooms",
                            multi=False,
                            style=dict(
                                verticalAlign="middle",
                                marginLeft ='2.5%',
                                width='95%'
                                )),
                            ])]),

                dbc.Row([
                    dbc.Col([ html.Label(['Select Property Type'],
                                         style={'font-family':"Candara",
                                                'font-size': '18px',
                                                "text-align": "center",
                                                "marginLeft":'5%',
                                                "margin-top":"2.5%"})])]),

                dbc.Row([
                    dbc.Col([ dcc.Dropdown(
                            id='dropdown3',
                            options=[{'label':label, 'value': value}for label, value in type_dict.items()],
                            value = 'Unit',
                            placeholder="Select Property Type",
                            multi=False,
                            style=dict(
                                verticalAlign="middle",
                                marginLeft ='2.5%',
                                width='95%'
                                ))
                            ])]),
                ],
                style={'width':'99%',
                       "marginLeft":'1.5%',
                       "marginTop":'1.5%',
                       'height':'270px',
                       "background-color": "#FFFFFF",
                       "border-radius": "4px",
                       "border-top-left-radius": "40px",
                       'box-shadow': 'rgba(0, 0, 0, 0.2) 0px 0px 5px 0px, rgba(0, 0, 0, 0.2) 0px 0px 1px 0px'},)
                ]),

            dbc.Col([
                html.Div(children = [
                    html.Iframe(id="google-map",
                                className="googlemap",
                                width='100%',
                                height='100%',
                                src=f"https://www.google.com/maps/embed/v1/place?key={google_api}&q=Alexandria,NSW"
                                )],

                    style={'border-style': 'solid',
                           'border-width': '0px',
                           'width':'99%',
                           "marginLeft":'-0.5%',
                           "marginTop":'1.5%',
                           'height':'270px',
                           'border-color': '#93979A',
                           "border-radius": "4px",
                           "border-top-right-radius": "40px",
                           "overflow": "hidden",
                           "background-color": "#FFFFFF",
                           'box-shadow': 'rgba(0, 0, 0, 0.2) 0px 0px 5px 0px, rgba(0, 0, 0, 0.2) 0px 0px 1px 0px'},

                ),]),
            ]),

            dbc.Row([

                dbc.Col([
                    html.Div([
                        dcc.Graph(id="graph_price",
                              style = {'width':'95%',
                                        "marginLeft":'2.5%'})],
                        style = {'width':'99%',
                                 "marginLeft":'1.5%',
                                 "marginTop":'2%',
                                 'background-color':'#FFFFFF',
                                 "overflow": "hidden",
                                 "border-radius": "4px",
                                 "border-bottom-left-radius": "40px",
                                 'box-shadow': 'rgba(0, 0, 0, 0.2) 0px 0px 5px 0px, rgba(0, 0, 0, 0.2) 0px 0px 1px 0px'})
                    ]),

            dbc.Col([
                html.Div([
                    dcc.Graph(id="graph_rent",
                              style = {'width':'95%',
                                        "marginLeft":'2.5%'})],
                    style = {
                           'width':'99%',
                           "marginTop":'2%',
                           "marginLeft":'-0.5%',
                           "background-color": "#FFFFFF",
                           "overflow": "hidden",
                           "border-radius": "4px",
                           "border-bottom-right-radius": "40px",
                           'box-shadow': 'rgba(0, 0, 0, 0.2) 0px 0px 5px 0px, rgba(0, 0, 0, 0.2) 0px 0px 1px 0px'})
                ]),
            ]),

        html.Div([
            dbc.Row([dbc.Col(html.H2('Demographic Information for Alexandria (2021 Census)',
                                     id="demogrphic-heading",
                                     style = {'font-family':"Candara",
                                              'font-size': '22px',
                                              "text-align": "center",
                                              "margin-bottom":"2%",
                                              "margin-top":"1%"}))]),


            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                            id='dropdown4',
                            options=[{'label':label, 'value': value} for label, value in demo_dict.items()][:5],
                            value = 'Rent',
                            placeholder="Select Demographic Information",
                            style=dict(
                                verticalAlign="middle",
                                marginLeft ='15%',
                                width='70%'
                                ))
                    ]),

            dbc.Col([
                dcc.Dropdown(
                        id='dropdown5',
                        options=[{'label':label, 'value': value} for label, value in demo_dict.items()][5:],
                        value = 'Age',
                        placeholder="Select Demographic Information",
                        style=dict(
                            verticalAlign="middle",
                            marginLeft ='15%',
                            width='70%'
                            ))
                ]),
            ]),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(id="graph_demo1")],
                        style = {'float':'left',
                                 'width':'95%',
                                 "marginLeft":'2.5%'})
                    ]),

            dbc.Col([
                html.Div([
                    dcc.Graph(id="graph_demo2")],
                    style = {'float':'right',
                             'width':'95%',
                            "marginRight":'5%'})
                ]),
            ]),
            ],
            style = {
                   'width':'98.5%',
                   "marginTop":'1%',
                   "marginLeft":'0.75%',
                   "marginRight":'0.75%',
                   "background-color": "#FFFFFF",
                   "overflow": "hidden",
                   "border-radius": "40px",
                   'box-shadow': 'rgba(0, 0, 0, 0.2) 0px 0px 5px 0px, rgba(0, 0, 0, 0.2) 0px 0px 1px 0px'}),

        html.Div([

        dbc.Row([dbc.Col(html.H2('Comparison between Suburbs',
                                 id="comparison-heading",
                                 style = {'font-family':"Candara",
                                          'font-size': '22px',
                                          "text-align": "center",
                                          "marginLeft":'30%',
                                          "marginTop":'1%',
                                          "width":"40%"}))]),

        dbc.Row([
            dbc.Col([ html.Label(['Select Suburbs to Compare'],
                                 style={'font-family':"Candara",
                                        'font-size': '18px',
                                        "text-align": "center",
                                        "marginLeft":'30%',
                                        "width":"40%"})]),

            dbc.Col([ html.Label(['Select Parameter'],
                                 style={'font-family':"Candara",
                                        'font-size': '18px',
                                        "text-align": "center",
                                        "marginLeft":'30%',
                                        "width":"40%"})])
            ]),

        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                        id='dropdown6',
                        options=[{'label':label, 'value': value} for label, value in suburb_dict.items()],
                        placeholder="Select Suburbs to Compare",
                        value = ['[Alexandria]','[Mascot]','[Waterloo]','[Zetland]'],
                        multi = True,
                        style=dict(
                            verticalAlign="middle",
                            marginLeft ='15%',
                            width='70%'
                            ),
                        className="custom-dropdown")
                ]),

            dbc.Col([
                dcc.Dropdown(
                        id='dropdown7',
                        options=[{'label':label, 'value': value} for label, value in parameters_dict.items()],
                        value = '[medianSoldPrice]',
                        placeholder="Select Parameters to Compare",
                        multi = False,
                        style=dict(
                            verticalAlign="middle",
                            marginLeft ='15%',
                            width='70%'
                            ))
                ]),
            ]),

        dbc.Row([
                html.Div([
                    dcc.Graph(id="graph_compare")],
                    style = {'float':'left',
                             'width':'90%',
                             'marginLeft':'5%'
                             })
                ]),
        ],
        style = {
               'width':'98.5%',
               "marginTop":'1%',
               "marginLeft":'0.75%',
               "marginRight":'0.75%',
               "marginBottom":'1%',
               "background-color": "#FFFFFF",
               "overflow": "hidden",
               "border-radius": "40px",
               'box-shadow': 'rgba(0, 0, 0, 0.2) 0px 0px 5px 0px, rgba(0, 0, 0, 0.2) 0px 0px 1px 0px'}),

        dbc.Row([dbc.Col(html.Hr(style={"height":"0px",
                                    "color":"#E9EAEA"}))]),

],
    style = {
           "background-color": "#F4F5F5"}
    )

@app.callback(
    Output("google-map", "src"),
    Input('dropdown1', 'value'),
    prevent_initial_call=True
)

def update_google_map(dropdown1):
    return f"https://www.google.com/maps/embed/v1/place?key={google_api}&q={dropdown1[1:-1]},NSW"

@app.callback(
    Output("demogrphic-heading", "children"),
    Input('dropdown1', 'value'),
    prevent_initial_call=True
)

def update_demographic_title(dropdown1):
    return f'Demographic Information for {dropdown1[1:-1]} (2021 Census)'


@app.callback(
    Output("graph_price", "figure"),
    [Input('dropdown1', 'value'),
    Input('dropdown2', 'value'),
    Input('dropdown3', 'value')
    ])

def price_plot(dropdown1, dropdown2, dropdown3):
    locality = dropdown1
    bedrooms = dropdown2
    prop_type = dropdown3

    if prop_type == 'Unit':
        conn = sqlite3.connect('Unit_data.db')
    else:
        conn = sqlite3.connect('House_data.db')

    query = f'SELECT * FROM {locality}  WHERE bedrooms IS {bedrooms}'
    df = pd.read_sql(query , conn)
    ticks = df['year'].astype(str)+' (Q'+df['quater'].astype(int).astype(str)+')'
    fig = fig = go.Figure()
    fig.add_trace(go.Scatter(x=ticks,
                              y=df['lowestSoldPrice'],
                              mode='lines+markers',
                              name="Lowest Sold Price",
                              hovertemplate = '%{x}<br>'+'$%{y}',
                              line_color = '#20a9ca',
                              visible="legendonly")),

    fig.add_trace(go.Scatter(x=ticks,
                              y=df['lowestSaleListingPrice'],
                              mode='lines+markers',
                              name="Lowest Listing Price",
                              hovertemplate = '%{x}<br>'+'$%{y}',
                              line=dict(color='#20a9ca',
                                        dash='dot'))),

    fig.add_trace(go.Scatter(x=ticks,
                             y=df['medianSoldPrice'],
                             mode='lines+markers',
                             name="Median Sold Price",
                             hovertemplate = '%{x}<br>'+'$%{y}',
                             line_color = 'rgb(37,202,160)')),

    fig.add_trace(go.Scatter(x=ticks,
                             y=df['medianSaleListingPrice'],
                             mode='lines+markers',
                             name="Median Listing Price",
                             hovertemplate = '%{x}<br>'+'$%{y}',
                             line=dict(color='rgb(37,202,160)',
                                       dash='dot'))),

    fig.add_trace(go.Scatter(x=ticks,
                             y=df['75thPercentileSoldPrice'],
                             mode='lines+markers',
                             name="75th Percentile Price",
                             hovertemplate = '%{x}<br>'+'$%{y}',
                             line_color = 'rgb(279,179,71)',
                             visible="legendonly")),

    fig.add_trace(go.Scatter(x=ticks,
                             y=df['95thPercentileSoldPrice'],
                             mode='lines+markers',
                             name="95th Percentile Price",
                             hovertemplate = '%{x}<br>'+'$%{y}',
                             line_color = 'rgb(249,91,58)',
                             visible="legendonly")),

    fig.add_trace(go.Scatter(x=ticks,
                             y=df['highestSaleListingPrice'],
                             mode='lines+markers',
                             name="Highest Listing Price",
                             hovertemplate = '%{x}<br>'+'$%{y}',
                             line=dict(color='rgb(249,91,58)',
                                       dash='dot'))),



    fig.update_layout(
        hoverlabel=dict(
            font_family="Candara",
            font_size=16),
        margin=dict(t=70),
        autosize=True,
        height=380,
        title=f'{dropdown2} Bedroom {prop_type} Price Trend in {locality[1:-1]} ',
        title_x=0.4,
        title_y=0.9,
        titlefont = dict(size=22),
        yaxis_title='Price ($)',
        plot_bgcolor='rgba(51,61,71,0)',
        font_family="Candara",
        legend = dict(
            font = dict(size = 16)),
        yaxis = dict(
            tickfont = dict(size=16),
            titlefont = dict(size=18),
            linecolor='rgba(51,61,71,0.6)',
            gridcolor='rgba(51,61,71,0.1)',
            showline=True,
            showgrid = True,
            griddash='dash',
            mirror=True,
            linewidth=1,
            gridwidth = 1
            ),
        xaxis = dict(
            tickfont = dict(size=16),
            linecolor='rgba(51,61,71,0.6)',
            gridcolor='rgba(51,61,71,0.1)',
            showline=True,
            showgrid = True,
            griddash='dash',
            mirror=True,
            linewidth=1,
            gridwidth = 1,
            range=[0, 15]
            ),
        )

    return fig

@app.callback(
    Output("graph_rent", "figure"),
    [Input('dropdown1', 'value'),
    Input('dropdown2', 'value'),
    Input('dropdown3', 'value')
    ])

def rent_plot(dropdown1, dropdown2, dropdown3):
    locality = dropdown1
    bedrooms = dropdown2
    prop_type = dropdown3

    if prop_type == 'Unit':
        conn = sqlite3.connect('Unit_data.db')
    else:
        conn = sqlite3.connect('House_data.db')

    query = f'SELECT * FROM {locality}  WHERE bedrooms IS {bedrooms}'
    df = pd.read_sql(query , conn)
    ticks = df['year'].astype(str)+' (Q'+df['quater'].astype(int).astype(str)+')'
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ticks,
                             y=df['medianRentListingPrice'],
                             mode='lines+markers',
                             name="Median Rent",
                             hovertemplate = '%{x}<br>'+'$%{y}',
                             line_color = 'rgb(37,202,160)'))


    fig.add_trace(go.Scatter(x=ticks,
                             y=df['highestRentListingPrice'],
                             mode='lines+markers',
                             name="Highest Rent",
                             hovertemplate = '%{x}<br>'+'$%{y}',
                             line_color = 'rgb(249,91,58)')),


    fig.update_layout(
        hoverlabel=dict(
            font_family="Candara",
            font_size=16),
        margin=dict(t=70),
        autosize=True,
        height=380,
        title=f'{dropdown2} Bedroom {prop_type} Rental Trend in {locality[1:-1]}',
        title_x=0.435,
        title_y=0.9,
        titlefont = dict(size=22),
        yaxis_title ='Weekly Rent ($)',
        plot_bgcolor ='rgba(51,61,71,0)',
        font_family ="Candara",
        legend = dict(
            font = dict(size = 16)),
        yaxis = dict(
            tickfont = dict(size=16),
            titlefont = dict(size=18),
            linecolor ='rgba(51,61,71,0.6)',
            gridcolor ='rgba(51,61,71,0.1)',
            griddash='dash',
            showline = True,
            showgrid = True,
            mirror=True,
            linewidth=1,
            gridwidth = 1
            ),
        xaxis = dict(
            linecolor ='rgba(51,61,71,0.6)',
            gridcolor ='rgba(51,61,71,0.1)',
            griddash='dash',
            showline = True,
            showgrid = True,
            mirror=True,
            linewidth=1,
            gridwidth = 1,
            range=[0, 15],
            tickfont = dict(size=16)
            ),
        )

    return fig

@app.callback(
    Output("graph_demo1", "figure"),
    [Input('dropdown1', 'value'),
    Input('dropdown4', 'value')
    ])

def demo_plot1(dropdown1,dropdown4):

    locality = dropdown1[1:-1].upper()
    demo = dropdown4
    conn = sqlite3.connect('Demographic_data.db')
    query = f'SELECT * FROM {demo}'
    df = pd.read_sql(query , conn)
    df = df[df['suburb']==f'{locality}']
    df = df.drop(['suburb'], axis=1).reset_index(drop =
                                                 True).sort_values(by=0,
                                                                   ascending=False,
                                                                   axis=1)
    if demo == "Occupation":
        df.columns = ['Professionals','Labourers','Technicians & Trade Workers',
         'Clerical & Administrative<br>Workers','Community & Personal<br>Service Workers',
         'Sales Workers', 'Managers', 'Machinery Operators<br>& Drivers',
         'Inadequately Described']

    if len(df.columns)>5:
        new_df = df.iloc[:,:5]
        others = list(df.sum(axis=1) - new_df.sum(axis=1))[0]
        new_df.insert(loc=5, column='Other', value=others)
        labels = (list(new_df.columns))
        values = (list(new_df.values[0]))
    else:
        labels = (list(df.columns))
        values = (list(df.values[0]))


    if demo == "Rent":
        labels = ['$450 to $549', '$350 to $449','$550 to $649','$275 to $349',
         '$650 to $749','Other']
    if demo == "Income":
        labels = ['$2000 to $2499','$4000+','$2500 to $2999','$3000 to $3499',
         '$1000 to $1249','Other']

    colors = ['#20a9ca','#1EB6B8','#1bc3a5',
              '#ffb24c','#FF8C40','#ff6633']

    if demo == 'Income':
        name = 'Weekly<br>Household<br>Income'
    elif demo == 'Rent':
        name = 'Weekly<br>Rent'
    elif demo == 'Transport':
        name = 'Mode of<br>Transport<br>to Work'
    else:
        name = f'{demo}'

    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels,
                         values=values,
                         text = [f'({i} %)' for i in (np.around((values/sum(values))*100,decimals=1))],
                         textinfo='none',
                         textposition='outside',
                         name = name,
                         textfont=dict(size=14),
                         hole = 0.4,
                         marker=dict(colors=colors,
                                     line=dict(color='#ffffff', width=3)),
                         sort=False,
                         showlegend=True,
                         hoverinfo="label+text",
                         insidetextorientation='horizontal'
                         )),

    fig.update_layout(
        legend=dict(
            font = dict(size=14),
            orientation="h",
            yanchor="top",
            y=0,
            xanchor="center",
            x=0.5),
        autosize = True,
        hoverlabel=dict(
            font_family="Candara",
            font_size=16),
        margin = {"r":0,"l":0,"t":30, "b":120},
        font_family = "Candara",
        annotations=[dict(text=name,
                          x=0.5,
                          y=0.5,
                          font_size=18,
                          showarrow=False,
                          font_family ="Candara")]
        )


    return fig

@app.callback(
    Output("graph_demo2", "figure"),
    [Input('dropdown1', 'value'),
    Input('dropdown5', 'value')
    ])

def demo_plot2(dropdown1,dropdown5):

    locality = dropdown1[1:-1].upper()
    demo = dropdown5
    conn = sqlite3.connect('Demographic_data.db')
    query = f'SELECT * FROM {demo}'
    df = pd.read_sql(query , conn)
    df = df[df['suburb']==f'{locality}']
    df = df.drop(['suburb'], axis=1).reset_index(drop =
                                                 True).sort_values(by=0,
                                                                   ascending=False,
                                                                   axis=1)
    if demo == "CountryOfBirth":
        country_df = (df[['Australia', 'Nepal', 'China','Northern Macedonia', 'Bangladesh',
           'Philippines', 'India', 'Brazil', 'Lebanon', 'Indonesia', 'Vietnam',
           'Thailand', 'New Zealand', 'Greece', 'England', 'Hong Kong', 'Italy',
           'Egypt', 'Fiji', 'Malaysia', 'Japan', 'Pakistan', 'Poland', 'Chile',
           'Croatia', 'Bosnia & Herzegovina', 'USA', 'Ireland', 'South Korea',
           'Turkey', 'South_Africa', 'Taiwan', 'Germany', 'Iraq', 'France',
           'Sri Lanka', 'Iran', 'Scotland', 'Canada', 'Malta', 'Singapore',
           'Cambodia', 'Netherlands', 'Myanmar', 'Samoa', 'Papua New Guinea',
           'Mauritius', 'Afghanistan', 'Zimbabwe', 'Wales']]).sort_values(by=0,ascending=False, axis=1)
        new_df = country_df.iloc[:,:5]
        others = list(df.sum(axis=1) - new_df.sum(axis=1))[0]
        new_df.insert(loc=5, column='Born Elsewhere', value=others)
        labels = (list(new_df.columns))
        values = (list(new_df.values[0]))

    elif len(df.columns)>5:
        new_df = df.iloc[:,:5]
        others = list(df.sum(axis=1) - new_df.sum(axis=1))[0]
        new_df.insert(loc=5, column='Other', value=others)
        labels = (list(new_df.columns))
        values = (list(new_df.values[0]))
    else:
        labels = (list(df.columns))
        values = (list(df.values[0]))

    colors = ['#20a9ca','#1EB6B8','#1bc3a5',
              '#ffb24c','#FF8C40','#ff6633']

    if demo == 'CountryOfBirth':
        name = 'Country<br>of<br>Birth'
    elif demo == 'MaritalStatus':
        name = 'Marital<br>Status'
    elif demo == 'Occupancy':
        name = 'Type<br>of<br>Occupancy'
    else:
        name = f'{demo}'

    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels,
                         values=values,
                         text = [f'({i} %)' for i in (np.around((values/sum(values))*100,decimals=1))],
                         textinfo='none',
                         textposition='inside',
                         name = name,
                         textfont=dict(size=14),
                         hole = 0.4,
                         marker=dict(colors=colors,
                                     line=dict(color='#ffffff', width=3)),
                         sort=False,
                         showlegend=True,
                         hoverinfo="label+text",
                         insidetextorientation='horizontal'
                         )),

    fig.update_layout(
        legend=dict(
            font = dict(size=14),
            orientation="h",
            yanchor="top",
            y=-0,
            xanchor="center",
            x=0.5),
        autosize = False,
        hoverlabel=dict(
            font_family="Candara",
            font_size=16),
        margin = {"r":0,"l":0,"t":30, "b":120},
        font_family = "Candara",
        annotations=[dict(text=name,
                          x=0.5,
                          y=0.5,
                          font_size=18,
                          showarrow=False,
                          font_family ="Candara")]

        )

    return fig

@app.callback(
    Output("graph_compare", "figure"),
    [Input('dropdown6', 'value'),
    Input('dropdown7', 'value'),
    Input('dropdown2', 'value'),
    Input('dropdown3', 'value')
    ])

def comparison_plot(dropdown6, dropdown7, dropdown2, dropdown3):
    locality = dropdown6
    bedrooms = dropdown2
    param = dropdown7
    prop_type = dropdown3

    if prop_type == 'Unit':
        conn = sqlite3.connect('Unit_data.db')
    else:
        conn = sqlite3.connect('House_data.db')

    query = f'SELECT year,quater,{param} FROM {locality[0]}  WHERE bedrooms IS {bedrooms}'
    df = pd.read_sql(query , conn)
    ticks = df['year'].astype(str)+' (Q'+df['quater'].astype(int).astype(str)+')'
    df.index = ticks
    df.drop(['year', 'quater'], axis = 1, inplace = True)
    df.rename(columns={f'{param[1:-1]}':f'{locality[0]}'}, inplace=True)

    for i in range(1, len(locality)):
        querytemp = f'SELECT {param} FROM {locality[i]}  WHERE bedrooms IS {bedrooms}'
        tempdf = pd.read_sql(querytemp , conn)
        tempdf.index = ticks
        tempdf.rename(columns={f'{param[1:-1]}':f'{locality[i]}'}, inplace=True)
        df = pd.concat([df, tempdf], axis = 1)

    colors = ['#20a9ca','#1bc3a5','#ffb24c','#ff6633','#20a9ca','#1bc3a5',
              '#ffb24c','#ff6633','#20a9ca','#1bc3a5','#ffb24c','#ff6633']
    symbol = ['circle','circle','circle','circle', 'square','square',
              'square','square','diamond','diamond','diamond','diamond']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index,
                             y=df[df.columns[0]],
                             name = df.columns[0][1:-1],
                             mode='lines+markers',
                             hovertemplate = '%{x}<br>'+'$%{y}',
                             marker=dict(size = 8, symbol=symbol[0]),
                             line_color = colors[0]))

    for j in range(1, len(locality)):
        fig.add_trace(go.Scatter(x=df.index,
                                 y=df[df.columns[j]],
                                 name = df.columns[j][1:-1],
                                 mode='lines+markers',
                                 hovertemplate = '%{x}<br>'+'$%{y}',
                                 marker=dict(size = 8, symbol=symbol[j]),
                                 line_color = colors[j]))


    fig.update_layout(
        hoverlabel=dict(
            font_family="Candara",
            font_size=16),
        margin=dict(t=70),
        autosize=True,
        height=450,
        title=f'{dropdown2} Bedroom {prop_type} {list(parameters_dict.keys())[list(parameters_dict.values()).index(param)]} Comparison',
        title_x=0.5,
        title_y=0.9,
        titlefont = dict(size=22),
        yaxis_title =f'{list(parameters_dict.keys())[list(parameters_dict.values()).index(param)]} ($)',
        plot_bgcolor ='rgba(51,61,71,0)',
        font_family ="Candara",
        legend = dict(
            font = dict(size = 16)),
        yaxis = dict(
            tickfont = dict(size=16),
            titlefont = dict(size=18),
            linecolor ='rgba(51,61,71,0.6)',
            gridcolor ='rgba(51,61,71,0.1)',
            griddash='dash',
            showline = True,
            showgrid = True,
            mirror=True,
            linewidth=1,
            gridwidth = 1
            ),
        xaxis = dict(
            linecolor ='rgba(51,61,71,0.6)',
            gridcolor ='rgba(51,61,71,0.1)',
            griddash='dash',
            showline = True,
            showgrid = True,
            mirror=True,
            linewidth=1,
            gridwidth = 1,
            range=[0, 15],
            tickfont = dict(size=16)
            ),
        )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
