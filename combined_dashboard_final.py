#!pip install plotly
#!pip install panel

import pandas as pd
import numpy as np
import panel as pn
import plotly.express as px
pn.extension('plotly')

df = pd.read_csv("G:/My Drive/M2/T2/Data Viz/Flight Prediction DataSet/Clean_Dataset_lon_lat.csv")
df.head(5)

# Define the interactive widgets
class_filter = pn.widgets.MultiSelect(options=['All'] + df['class'].unique().tolist(), name='Filter by Class', value=['All'])
stops_filter = pn.widgets.MultiSelect(options=['All'] + df['stops'].unique().tolist(), name='Filter by Stops', value=['All'])
days_left_slider = pn.widgets.RangeSlider(start=df['days_left'].min(), end=df['days_left'].max(), value=(df['days_left'].min(), df['days_left'].max()), step=1, name='Days Left Slider')
duration_slider = pn.widgets.FloatSlider(start=df['duration'].min(), end=df['duration'].max(), value=df['duration'].mean(), step=1, name='Duration Slider')

# Define the color map for the airlines
color_map = {
    'SpiceJet': '#bee9e8',
    'AirAsia': '#62b6cb',
    'Vistara': '#1b4965',
    'GO_FIRST': '#cae9ff',
    'Indigo': '#cae9ff',
    'Air_India': '#5fa8d3'
}

color_map2 = {
    'Mumbai': '#bee9e8',
    'Bangalore': '#62b6cb',
    'Kolkata': '#1b4965',
    'Hyderabad': '#cae9ff',
    'Chennai': '#cae9ff',
    'Delhi': '#5fa8d3'
}

# Define the order of the x-axis categories for departure time bar graph
x_order = ['Early_Morning', 'Morning', 'Afternoon', 'Evening', 'Night', 'Late_Night']

# Define the order of the x-axis categories for bubble chart
destinos = ['Mumbai', 'Bangalore', 'Kolkata', 'Hyderabad', 'Chennai', 'Delhi']

# Define the update function for the plot
def update_plot(event):
    # Filter the dataframe based on the selected values of the widgets
    class_options = class_filter.options if 'All' in class_filter.value else class_filter.value
    stops_options = stops_filter.options if 'All' in stops_filter.value else stops_filter.value
    filtered_df = df[(df['class'].isin(class_options)) & (df['stops'].isin(stops_options)) & (df['days_left'] >= days_left_slider.value[0]) & (df['days_left'] <= days_left_slider.value[1]) & (df['duration'] <= duration_slider.value)]
    
    vuelos = filtered_df.groupby(['destination_city', 'latitude_destination', 'longitude_destination']).agg(num_flights=('flight', 'count')).reset_index()
    # Map the airline to the color palette
    color_discrete_map = {destin_city: color_map2[destin_city] for destin_city in vuelos['destination_city'].unique()}
    
    # Create the plotly figure
    fig1 = px.pie(filtered_df, names=filtered_df.groupby('airline')['flight'].nunique().index, values=filtered_df.groupby('airline')['flight'].nunique().values, 
                 color=filtered_df.groupby('airline')['flight'].nunique().index, color_discrete_map=color_map, 
                 hole=0.6, title='Unique flights by Airlines')
    
    fig2 = px.histogram(filtered_df, x='departure_time', y='price', color='airline', 
                        category_orders={'departure_time': x_order}, color_discrete_map=color_map, 
                        title='Flight Prices by Departure Time in Indian Rupee',histfunc='avg')
    fig2.update_layout(xaxis_title='Departure Time', yaxis_title='Price (in INR)')
    
    fig3 = px.box(
    filtered_df,  
             x='airline', y='price', color='airline', category_orders={'airline': x_order}, color_discrete_map=color_map,
              title='Box Plot for Flight Price by Airlines')
    fig3.update_layout(xaxis_title='Airlines', yaxis_title='Price (in INR)')
        
    fig4 = px.scatter_geo(vuelos, lat='latitude_destination', lon='longitude_destination', size='num_flights', color='destination_city',
                     center={'lat': vuelos['latitude_destination'].iloc[0], 'lon': vuelos['longitude_destination'].iloc[0]},
                     scope='asia', color_discrete_map=color_discrete_map, title = 'Count of Flights by Destination City')
    

    # Update the plot
    donut_panel.object = fig1
    bar_panel.object = fig2
    boxplot_panel.object = fig3
    bubblemap_panel.object = fig4

# Create the initial plot
fig1 = px.pie(df, names=df.groupby('airline')['flight'].nunique().index, values=df.groupby('airline')['flight'].nunique().values, 
                 color=df.groupby('airline')['flight'].nunique().index, color_discrete_map=color_map, 
                 hole=0.6, title='Unique flights by Airlines')

fig2 = px.histogram(df, x='departure_time', y='price', color='airline', 
                        category_orders={'departure_time': x_order}, color_discrete_map=color_map, 
                        title='Flight Prices by Departure Time in Indian Rupee',histfunc='avg')
fig2.update_layout(xaxis_title='Departure Time', yaxis_title='Price (in INR)')

fig3 = px.box(df, 
             x='airline', y='price', color='airline', category_orders={'airline': x_order}, color_discrete_map=color_map,
              title='Box Plot for Flight Price by Airlines')
fig3.update_layout(xaxis_title='Airlines', yaxis_title='Price (in INR)')

vuelos = df.groupby(['destination_city', 'latitude_destination', 'longitude_destination']).agg(num_flights=('flight', 'count')).reset_index()
# Map the airline to the color palette
color_discrete_map = {destin_city: color_map2[destin_city] for destin_city in vuelos['destination_city'].unique()}

fig4 = px.scatter_geo(vuelos, lat='latitude_destination', lon='longitude_destination', size='num_flights', color='destination_city',
                  center={'lat': vuelos['latitude_destination'].iloc[0], 'lon': vuelos['longitude_destination'].iloc[0]},
                  scope='asia', color_discrete_map=color_discrete_map, title = 'Count of Flights by Destination City')

donut_panel = pn.pane.Plotly(fig1, config={'displayModeBar': False})
bar_panel = pn.pane.Plotly(fig2, config={'displayModeBar': False})
boxplot_panel = pn.pane.Plotly(fig3, config={'displayModeBar': False})
bubblemap_panel = pn.pane.Plotly(fig4, config={'displayModeBar': False})

# Register the update function to the widgets' events
class_filter.param.watch(update_plot, 'value')
stops_filter.param.watch(update_plot, 'value')
days_left_slider.param.watch(update_plot, 'value')
duration_slider.param.watch(update_plot, 'value')

# Define CSS classes for the dashboard
pn.extension(css_files=['https://fonts.googleapis.com/css2?family=Roboto&display=swap'])
css = """
.header {
    font-size: 30px;
    padding-top: 20px;
    padding-bottom: 20px;
    text-align: center;
    font-family: 'Roboto', sans-serif;
    font-weight: bold;
}

.sidebar {
    background-color: #f5f5f5;
    padding-top: 20px;
    padding-bottom: 20px;
}

.main {
    padding: 10px;
}

.plot {
    padding: 20px;
    background-color: #ffffff;
    box-shadow: 2px 2px 5px 2px rgba(0,0,0,0.2);
    border-radius: 5px;
    margin: 10px;
}

.plotly-graph-svg {
    max-width: 100%;
    height: auto;
}
"""
pn.extension(raw_css=[css])

# Define the size of the dashboard
dashboard_width = 400

# Modify the layout of the dashboard components
header = pn.pane.Markdown("# Flight Price Analysis Dashboard", css_classes=["header"])
sidebar = pn.Column(
    class_filter,
    stops_filter,
    days_left_slider,
    duration_slider,
    sizing_mode='stretch_width'
)

# Create a row of widgets on the top
widgets_row = pn.Row(class_filter, stops_filter, days_left_slider, duration_slider, sizing_mode='stretch_width')

# Create the panel dashboard layout

departure_time = pn.Column(
    pn.Row(header, css_classes=["header"]),
    widgets_row,
    pn.Row(
        pn.Column(
            pn.Row(
                bar_panel,
                css_classes=["plot"],
            ),
            css_classes=["main"]
        ),
        pn.Column(
            pn.Row(
                donut_panel,
                css_classes=["plot"],
            ),
            css_classes=["main"]
        ),
        sizing_mode='stretch_both'
    ),
    pn.Row(
        pn.Column(
            pn.Row(
                boxplot_panel,
                css_classes=["plot"],
            ),
            css_classes=["main"]
        ),
        pn.Column(
            pn.Row(
                bubblemap_panel,
                css_classes=["plot"],
            ),
            css_classes=["main"]
        ),
        sizing_mode='stretch_both'
    ),
)

# Show the dashboard
departure_time.servable()

