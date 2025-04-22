import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

# Load the CSV file from the GitHub raw URL
csv_url = "https://raw.githubusercontent.com/hydrospheric0/BIGYEAR/refs/heads/main/big_year_pace.csv"
data = pd.read_csv(csv_url)

# Extract series names (all columns except Date)
series_names = data.columns[1:]

# Use the more reliable date parsing approach
# Function to parse dates in MM/DD format and add current year
def parse_month_day(date_str):
    try:
        parts = date_str.split('/')
        if len(parts) == 2:
            month, day = map(int, parts)
            current_year = datetime.now().year
            return pd.Timestamp(year=current_year, month=month, day=day)
        else:
            return pd.NaT
    except:
        return pd.NaT

# Try to parse dates
data["Date"] = data["Date"].apply(parse_month_day)

# Drop rows with invalid dates
data = data.dropna(subset=["Date"])

# Get all dates and first of month dates for ticks
dates = data["Date"]
first_of_month_indices = dates.dt.is_month_start
first_of_month_dates = dates[first_of_month_indices]

# Build the Dash app
app = dash.Dash(__name__)
app.title = "Big Year Pace Plot"

# App layout
app.layout = html.Div([
    html.H2("Big Year Pace Plot"),
    dcc.Graph(id="line-plot"),
    html.Div([
        dcc.Checklist(
            id="series-selector",
            options=[{"label": name, "value": name} for name in series_names],
            value=list(series_names),  # Default to showing all series
            inline=True,
            style={"display": "inline-block"},
            inputStyle={"margin-right": "5px", "margin-left": "10px"}
        )
    ], style={"position": "relative", "bottom": "10px", "right": "10px", "text-align": "center"})
])


# Update the plot based on the selected series
@app.callback(
    Output("line-plot", "figure"),
    Input("series-selector", "value")
)
def update_plot(selected_series):
    # Create the figure
    fig = go.Figure()

    # Add a trace for each selected series
    for series in selected_series:
        # Convert string values to floats where possible
        y_values = pd.to_numeric(data[series], errors='coerce')
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=y_values,
            mode="lines",
            name=series
        ))

    # Get tick values for first of each month
    if len(first_of_month_dates) > 0:
        tick_vals = first_of_month_dates
    else:
        # If no first-of-month dates, use evenly spaced ticks
        tick_vals = dates.iloc[::max(1, len(dates)//6)]
    
    # Create custom tick text to format as "Jan 1" instead of "Jan 01"
    tick_text = [d.strftime("%b") + " " + str(d.day) for d in tick_vals]

    # Layout configuration
    fig.update_layout(
        title="Big Year Pace Plot",
        xaxis=dict(
            title=None,  # Remove the "Date" label
            tickvals=tick_vals,
            ticktext=tick_text,  # Use custom formatted tick text
            tickfont=dict(
                family="Arial, sans-serif",
                size=12,
                color="black"
            ),
            showline=True,
            linewidth=2,
            linecolor='black',
            mirror=True  # Add the frame around the plot
        ),
        yaxis=dict(
            title=dict(
                text="Species Count",
                font=dict(
                    family="Arial, sans-serif",
                    size=14,
                    color="black" 
                )
            ),
            range=[0, 300],  # Y-axis range from 0 to 300
            tickfont=dict(
                family="Arial, sans-serif",
                size=12,
                color="black"
            ),
            showline=True,
            linewidth=2,
            linecolor='black',
            mirror=True  # Add the frame around the plot
        ),
        legend_title="Series",
        template="plotly_white",
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=80, r=80, t=100, b=80),
        showlegend=True,
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="black"
        )
    )

    return fig


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
