from flask import Blueprint, render_template, jsonify
import plotly.graph_objs as go
from app.utils import fetch_and_store_earthquake_data, get_earthquake_data
import pandas as pd
import numpy as np


main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Homepage that displays a visualization."""
    df = get_earthquake_data()  # Fetch data from MongoDB

    # Example Visualization: Bubble Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['geometry.coordinates'].apply(lambda x: x[2]),  # Depth
        y=df['properties.mag'],  # Magnitude
        mode='markers',
        marker=dict(
            size=df['properties.mag'] * 10,  # Bubble size
            color=df['properties.mag'],  # Color by magnitude
            colorscale='Viridis',
            showscale=True
        )
    ))
    fig.update_layout(
        title="Earthquake Magnitude vs. Depth",
        xaxis_title="Depth (km)",
        yaxis_title="Magnitude"
    )
    graph = fig.to_html(full_html=False)

    return render_template('index.html', graph=graph)

@main.route('/api/data')
def api_data():
    """API endpoint to fetch earthquake data."""
    df = get_earthquake_data()  # Fetch data from MongoDB
    return jsonify(df.to_dict(orient='records'))

@main.route('/scatter')
def scatter_plot():
    """Scatter plot of earthquake locations and magnitudes."""
    df = get_earthquake_data()  # Fetch data from MongoDB

    # Extract longitude, latitude, and magnitude
    longitudes = df['geometry.coordinates'].apply(lambda x: x[0])
    latitudes = df['geometry.coordinates'].apply(lambda x: x[1])
    magnitudes = df['properties.mag']

    # Create a scatter plot with Plotly
    fig = go.Figure(data=go.Scatter(
        x=longitudes,  # Longitude
        y=latitudes,   # Latitude
        mode='markers',
        marker=dict(
            size=10,  # Marker size
            color=magnitudes,  # Color by magnitude
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Magnitude")
        )
    ))
    fig.update_layout(
        title="Earthquake Locations and Magnitudes",
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        height=600,
        width=800
    )

    # Convert Plotly plot to HTML
    graph = fig.to_html(full_html=False)

    return render_template('index.html', graph=graph)

@main.route('/time-series')
def time_series():
    """Time series plot of earthquake magnitudes over time."""
    df = get_earthquake_data()  # Fetch data from MongoDB

    # Convert time to pandas datetime
    df['time'] = pd.to_datetime(df['properties.time'], unit='ms')

    # Create a line plot with Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['time'],  # Time
        y=df['properties.mag'],  # Magnitude
        mode='lines',
        line=dict(color='blue')
    ))
    fig.update_layout(
        title="Earthquake Magnitudes Over Time",
        xaxis_title="Time",
        yaxis_title="Magnitude",
        height=600,
        width=800
    )

    # Convert Plotly plot to HTML
    graph = fig.to_html(full_html=False)

    return render_template('index.html', graph=graph)

@main.route('/histogram')
def histogram():
    """Histogram of earthquake magnitudes."""
    df = get_earthquake_data()  # Fetch data from MongoDB

    # Create a histogram with Plotly
    fig = go.Figure(data=[go.Histogram(
        x=df['properties.mag'],  # Magnitude
        xbins=dict(
            start=df['properties.mag'].min(),  # Minimum magnitude
            end=df['properties.mag'].max(),    # Maximum magnitude
            size=0.1                           # Bin size
        ),
        marker_color='green',
        opacity=0.75
    )])
    fig.update_layout(
        title="Distribution of Earthquake Magnitudes",
        xaxis_title="Magnitude",
        yaxis_title="Frequency",
        height=600,
        width=800
    )

    # Convert Plotly plot to HTML
    graph = fig.to_html(full_html=False)

    return render_template('index.html', graph=graph)

@main.route('/heatmap')
def heatmap():
    """Smooth heatmap of earthquake locations."""
    df = get_earthquake_data()  # Fetch data from MongoDB

    # Extract longitude and latitude
    longitudes = df['geometry.coordinates'].apply(lambda x: x[0])
    latitudes = df['geometry.coordinates'].apply(lambda x: x[1])

    # Create a 2D density plot with Plotly
    fig = go.Figure(data=go.Densitymapbox(
        lon=longitudes,  # Longitude
        lat=latitudes,   # Latitude
        z=None,          # Use density by default
        radius=10,       # Smoothing radius (adjust to control smoothness)
        colorscale="Viridis",  # Color scale
        colorbar=dict(title="Density"),
    ))

    # Update layout for the map
    fig.update_layout(
        title="Heatmap of Earthquake Locations",
        mapbox=dict(
            style="carto-positron",  # Use a base map style
            center=dict(lat=latitudes.mean(), lon=longitudes.mean()),  # Center map
            zoom=3  # Adjust zoom level
        ),
        height=600,
        width=800
    )

    # Convert Plotly plot to HTML
    graph = fig.to_html(full_html=False)

    return render_template('index.html', graph=graph)

@main.route('/boxplot')
def boxplot():
    """Box plot of earthquake magnitudes by region."""
    df = get_earthquake_data()  # Fetch data from MongoDB

    # Categorize earthquakes by region based on latitude
    df['region'] = np.where(df['geometry.coordinates'].apply(lambda x: x[1]) > 0,
                            'Northern Hemisphere', 'Southern Hemisphere')

    # Create a box plot with Plotly
    fig = go.Figure()
    for region in df['region'].unique():
        region_data = df[df['region'] == region]
        fig.add_trace(go.Box(
            y=region_data['properties.mag'],  # Magnitude
            name=region,  # Region (Northern/Southern Hemisphere)
            boxmean=True  # Display mean
        ))

    fig.update_layout(
        title="Earthquake Magnitudes by Region",
        xaxis_title="Region",
        yaxis_title="Magnitude",
        height=600,
        width=800
    )

    # Convert Plotly plot to HTML
    graph = fig.to_html(full_html=False)

    return render_template('index.html', graph=graph)

@main.route('/depth-vs-magnitude')
def depth_vs_magnitude():
    """Scatter plot of earthquake depth vs. magnitude."""
    df = get_earthquake_data()  # Fetch data from MongoDB

    # Extract depth and magnitude
    depths = df['geometry.coordinates'].apply(lambda x: x[2])  # Depth (3rd coordinate)
    magnitudes = df['properties.mag']  # Magnitude

    # Create a scatter plot with Plotly
    fig = go.Figure(data=go.Scatter(
        x=depths,  # Depth
        y=magnitudes,  # Magnitude
        mode='markers',
        marker=dict(
            size=8,  # Marker size
            color=magnitudes,  # Color by magnitude
            colorscale='Viridis',
            opacity=0.6,
            showscale=True,
            colorbar=dict(title="Magnitude")
        )
    ))
    fig.update_layout(
        title="Scatter Plot of Depth vs. Magnitude",
        xaxis_title="Depth (km)",
        yaxis_title="Magnitude",
        height=600,
        width=800
    )

    # Convert Plotly plot to HTML
    graph = fig.to_html(full_html=False)

    return render_template('index.html', graph=graph)

@main.route('/hourly-frequency')
def hourly_frequency():
    """Bar chart of earthquake frequency by hour of the day."""
    df = get_earthquake_data()  # Fetch data from MongoDB

    # Extract and group data by hour
    df['time'] = pd.to_datetime(df['properties.time'], unit='ms')  # Convert time to datetime
    df['hour'] = df['time'].dt.hour  # Extract hour of the day
    hourly_counts = df.groupby('hour').size()  # Count earthquakes by hour

    # Create a bar chart with Plotly
    fig = go.Figure(data=go.Bar(
        x=hourly_counts.index,  # Hours (0–23)
        y=hourly_counts.values,  # Frequency
        marker_color='teal'
    ))
    fig.update_layout(
        title="Earthquake Frequency by Hour of the Day",
        xaxis_title="Hour of Day",
        yaxis_title="Frequency",
        height=600,
        width=800
    )

    # Convert Plotly plot to HTML
    graph = fig.to_html(full_html=False)

    return render_template('index.html', graph=graph)

@main.route('/daily-frequency')
def daily_frequency():
    """Line chart of daily earthquake frequency."""
    df = get_earthquake_data()
    df['time'] = pd.to_datetime(df['properties.time'], unit='ms')
    df['date'] = df['time'].dt.date
    daily_counts = df.groupby('date').size()

    fig = go.Figure(data=go.Scatter(
        x=daily_counts.index,  # Dates
        y=daily_counts.values,  # Frequency
        mode='lines',
        line=dict(color='blue')
    ))
    fig.update_layout(
        title="Earthquake Frequency Over Time (Daily)",
        xaxis_title="Date",
        yaxis_title="Frequency",
        height=600,
        width=800
    )

    graph = fig.to_html(full_html=False)
    return render_template('index.html', graph=graph)

@main.route('/monthly-frequency')
def monthly_frequency():
    """Bar chart of monthly earthquake frequency."""
    df = get_earthquake_data()
    df['time'] = pd.to_datetime(df['properties.time'], unit='ms')
    df['month'] = df['time'].dt.month
    monthly_counts = df.groupby('month').size()

    fig = go.Figure(data=go.Bar(
        x=monthly_counts.index,  # Months (1–12)
        y=monthly_counts.values,  # Frequency
        marker_color='orange'
    ))
    fig.update_layout(
        title="Earthquake Frequency by Month",
        xaxis_title="Month",
        yaxis_title="Frequency",
        height=600,
        width=800
    )

    graph = fig.to_html(full_html=False)
    return render_template('index.html', graph=graph)

@main.route('/depth-histogram')
def depth_histogram():
    """Histogram of earthquake depths."""
    df = get_earthquake_data()
    depths = df['geometry.coordinates'].apply(lambda x: x[2])  # Depth

    fig = go.Figure(data=go.Histogram(
        x=depths,
        nbinsx=30,  # Number of bins
        marker=dict(color='lightcoral', line=dict(color='black', width=1))
    ))
    fig.update_layout(
        title="Distribution of Earthquake Depths",
        xaxis_title="Depth (km)",
        yaxis_title="Frequency",
        height=600,
        width=800
    )

    graph = fig.to_html(full_html=False)
    return render_template('index.html', graph=graph)

@main.route('/bubble-depth-magnitude')
def bubble_depth_magnitude():
    """Bubble chart of depth vs. magnitude."""
    df = get_earthquake_data()
    depths = df['geometry.coordinates'].apply(lambda x: x[2])
    magnitudes = df['properties.mag']

    fig = go.Figure(data=go.Scatter(
        x=depths,  # Depth
        y=magnitudes,  # Magnitude
        mode='markers',
        marker=dict(
            size=magnitudes * 5,  # Bubble size proportional to magnitude
            color=magnitudes,  # Color by magnitude
            colorscale='Viridis',
            showscale=True,
            opacity=0.5
        )
    ))
    fig.update_layout(
        title="Earthquake Magnitude vs. Depth (Bubble Chart)",
        xaxis_title="Depth (km)",
        yaxis_title="Magnitude",
        height=600,
        width=800
    )

    graph = fig.to_html(full_html=False)
    return render_template('index.html', graph=graph)

@main.route('/region-distribution')
def region_distribution():
    """Pie chart of earthquake distribution by region."""
    df = get_earthquake_data()
    df['region'] = np.where(df['geometry.coordinates'].apply(lambda x: x[1]) > 0,
                            'Northern Hemisphere', 'Southern Hemisphere')
    region_counts = df['region'].value_counts()

    fig = go.Figure(data=go.Pie(
        labels=region_counts.index,
        values=region_counts.values,
        hole=0.3,
        marker=dict(colors=['lightgreen', 'lightblue'])
    ))
    fig.update_layout(
        title="Earthquake Distribution by Region",
        height=600,
        width=800
    )

    graph = fig.to_html(full_html=False)
    return render_template('index.html', graph=graph)
