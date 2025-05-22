from dotenv import load_dotenv
import os
import requests
import pandas as pd
from stravalytics import weather_api
from stravalytics.api_utils import ApiUtils 


class StravaApiClient(ApiUtils):
    """
    Strava API Client. Allows to pull data from strava and to modify activities.
    """

    auth_url = 'https://www.strava.com/oauth/token'
    strava_api = 'https://www.strava.com/api/v3'
    activities_url = strava_api + '/athlete/activities'
    activity_url   = strava_api + '/activities'


    def __init__(self):
        """
        Get API credentials from .env.
        Prepare variables to store data
        """
        
        # Data
        self.activities_data = None
        self.df_activities = None
        
        # Load .env file with Strava API credentials
        load_dotenv()

        # Read environment variables
        refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
        client_id     = os.getenv('STRAVA_CLIENT_ID')
        client_secret = os.getenv('STRAVA_CLIENT_SECRET')

        # Get an access token. Authorize with payload
        payload = {
            'client_id': f'{client_id}',
            'client_secret': f'{client_secret}',
            'refresh_token': f'{refresh_token}',
            'grant_type': "refresh_token",
            'f': 'json'
        }

        print('Requesting Token...')
        res = requests.post(self.auth_url, data=payload, verify=False)
        access_token = res.json()['access_token']
        print('Access token retrieved')
        
        # Define an http authorization header, needed for the API calls
        self.header = {'Authorization': 'Bearer ' + access_token}

    
    def get_activities(self, page_initial=1, max_pages=99, **kwargs):
        """
        Pull activities data from Strava API.
        Activities are bundled in pages of up to 200 activities,
        so we may need to do multiple API calls.
        The first page contains the most recent activities.
        Returns a list of activities in JSON.
        [TODO: REVISE] kwargs: after_epoch_timestamp. 
            Note that this puts older activities in the first page
        """
        
        activities_data = []
        current_page = page_initial
        new_data = True
        
        while new_data and current_page <= max_pages:
            print(f'Retrieving data for page {current_page} of activities...')
            # Request 200 results per page, which is the API limit
            new_data = self.api_call('GET',
                                     self.activities_url,
                                     headers=self.header,
                                     params={'per_page': 200,
                                             'page': f'{current_page}',
                                             # 'after': f'{after_epoch_timestamp}'
                                            }
                                    )
            activities_data.extend(new_data)
            current_page += 1
    
        print(len(activities_data), ' activities loaded!')
        
        self.activities_data = activities_data


    def create_df_activities(self, activity_type_filter='Run'):
        """
        Transform:
            activities_data (list of activities in JSON from get_activities())
        to:
            df_activities (DataFrame)

        Select activities of type given by activity_type_filter
        
        Select relevant columns:
            'id', 'name', 'distance', 'moving_time', 'elapsed_time',
            'total_elevation_gain', 'type', 'start_date_local',
            'end_lat', 'end_lon', 'average_cadence', 'average_heartrate'
            
        Fix data types, use kms and minutes.
        """
    
        df_activities = pd.json_normalize(self.activities_data)
    
        df_activities = df_activities[df_activities['type']==activity_type_filter]

        # End coordinates may be more reliable that start coordinates
        df_activities[['end_lat', 'end_lon']] = df_activities['end_latlng'].apply(pd.Series)
        cols = ['id',
                'name',
                'distance',
                'moving_time',
                'elapsed_time',
                'total_elevation_gain',
                'type',
                'start_date_local',
                'end_lat',
                'end_lon',
                'average_cadence',
                'average_heartrate'
               ]
        df_activities = df_activities[cols]

        # Calculate activity mid time
        start = pd.to_datetime(df_activities['start_date_local'])
        duration = pd.to_timedelta(df_activities['elapsed_time'], unit='s')
        df_activities['mid_time'] = start + duration/2
        
        df_activities['start_date_local'] = pd.to_datetime(df_activities['start_date_local']).dt.date
        
        # distances in kms
        df_activities['distance'] = df_activities['distance']/1000
        
        # duration in minutes
        df_activities['moving_time'] = df_activities['moving_time']/60
        df_activities['elapsed_time'] = df_activities['elapsed_time']/60
        
        self.df_activities = df_activities
    
    
    
    def get_activity(self, activity_id):
        """
        Pull data for one activity using the APU.
        Returns a JSON.
        """
        
        url = self.activity_url + '/' + str(activity_id)
        activity_data = self.api_call('GET', url, headers=self.header)
        return activity_data
    
    
    def update_activity_description(self, activity_id, new_description, append_new_description=True):
        """
        Change the description of an activity with a new description.
        Replace or append the new description to the current one. 
        """

    
        if append_new_description:
            old_description = self.get_activity(activity_id).get('description')
            if old_description is not None:
                new_description = old_description + "\n\n" + new_description

        print("updating activity description. \n>>> From: \n",
              old_description,
              "\n>>> to: \n",
              new_description
             )
        url = self.activity_url + '/' + str(activity_id)
        status = self.api_call('PUT', url, headers=self.header, params={'description': new_description})
    
        return status
    
    
    def update_activity_name(self, activity_id, new_name, prepend_new_name=True):
        """
        Change an activity name.
        Replace or prepend the new name to the current one.
        """
        
        old_name = self.get_activity(activity_id).get('name')

        if prepend_new_name and old_name is not None:
            new_name = new_name + " " + old_name
    
        print("updating activity name. \n>>> From: \n",
              old_name,
              "\n>>> to: \n",
              new_name
             )
        url = self.activity_url + '/' + str(activity_id)
        status = self.api_call('PUT', url, headers=self.header, params={'name': new_name})
    
        return status


    def add_weather_to_activities(self, activity_ids, dry_run=True):
        """
        Get weather information for the activities ids provided
        and modify their name and description to add the weather summary and emoji.
        Activities data needs to already be present in self.df_activities (this
        means we need to run get_activities() and create_df_activities() before).
        Before adding the weather to each activity it checks if it is already present
        in the description.
        """

        count_activities_updated = 0
        count_activities_had_weather = 0
        count_activities_weather_error = 0
        
        for _id in activity_ids:

            # Check if the activity already has weather information
            old_description = self.get_activity(_id).get('description')
            if 'albertizard' in old_description:
                print(f"Activity id={_id} already had weather information. Skipping it.")
                count_activities_had_weather += 1
                continue

            # Extract coordinates and time to request weather info
            activity = self.df_activities[self.df_activities['id']==_id]
            
            # Get the hour closest to the mid activity time. Add 30 min to mid time and extract hour
            closest_hour = activity['mid_time'] + pd.to_timedelta(1800, unit='s') # datetime object
            date = str(closest_hour.dt.date.values[0])
            hour = str(closest_hour.dt.hour.values[0])
    
            lat = str(activity['end_lat'].to_numpy()[0])
            lon = str(activity['end_lon'].to_numpy()[0])

            print(f"Getting weather information for activity id={_id}")
            weather = weather_api.WeatherApiClient(lat, lon, date, hour)
            weather.get_weather_data()
            weather.format_weather_summary()

            if weather.weather_data is None:
                count_activities_weather_error += 1
                continue
            
            new_description = old_description \
                            + "\n\n" \
                            + weather.weather_summary \
                            + ' - by albertizard dot com'
            new_name = weather.weather_emoji
    
            if dry_run == True:
                print("This is a dry run. Weather summary:\n",
                      weather.weather_summary, 
                      "\nWeather emoji: \n",
                      weather.weather_emoji)
            else:
                print(f"Adding weather information to activity id={_id}")
                status = update_activity_description(_id, new_description, append_new_description=False)
                status = update_activity_name(_id, new_name=new_name, prepend_new_name=True)

            count_activities_updated += 1

        print("Weather added to: ",
              count_activities_updated, "/", len(activity_ids),
             "activities.\n",
             "\t", count_activities_had_weather, " already had weather info.\n",
             "\t", count_activities_weather_error, " weather could not be retrieved.")

    
    def add_weather_to_recent_activities(self, n_days_ago=7, dry_run=True):
        """
        Add weather information to recent the activities from the last days.
        """
        
        one_week_ago = (pd.Timestamp.today() - pd.Timedelta(days=n_days_ago)).date()
        print("Adding weather information to activities since ", one_week_ago)
        
        is_last_week = self.df_activities["start_date_local"] >= one_week_ago
        ids_last_week = self.df_activities[is_last_week].id.to_list()

        self.add_weather_to_activities(ids_last_week, dry_run=dry_run)

        
        
        
    
            