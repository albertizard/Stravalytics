# main.py
from stravalytics import strava_api
from stravalytics.weather_api import WeatherApiClient, WeatherEmojis

import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta

import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def main():
    # Set up the client to the Strava API
    strava_client = strava_api.StravaApiClient()

    # Get data for recent activities
    strava_client.get_activities(max_pages=1)

    # Transform to a clean DataFrame. Select running activities
    strava_client.create_df_activities(activity_type_filter="Run")

    print(f"Fetched {len(strava_client.df_activities)} activities")
    print(strava_client.df_activities.head())

    # Add weather to recent activities from the last days
    strava_client.add_weather_to_recent_activities(n_days_ago = 10, dry_run=False)




if __name__ == "__main__":
    main()
