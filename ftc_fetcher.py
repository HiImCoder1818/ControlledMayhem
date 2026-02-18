import requests
from requests.auth import HTTPBasicAuth
import pprint
import json
from collections import defaultdict
import re
import dotenv
import os

dotenv.load_dotenv()

FTC_USERNAME = "danielyang"
FTC_TOKEN = "580CEA6C-A352-4802-A68A-065EB76CE7ED"
"""
FTC-USERNAME = danielyang
FTC-TOKEN = 580CEA6C-A352-4802-A68A-065EB76CE7ED
"""

class FTCInfoFetcher:
    def __init__(self, season=2025):
        self.base_url = f"https://ftc-api.firstinspires.org/v2.0/{season}/"

    def get_team_region(self, team_number):
        url = self.base_url + "teams"
        r = requests.get(url, params={"teamNumber": team_number}, auth=HTTPBasicAuth(FTC_USERNAME, FTC_TOKEN))
        r.raise_for_status()

        team_info = r.json()

        return team_info["teams"][0]["homeRegion"]
    
    def get_leagues_in_region(self, region):
        url = self.base_url + "leagues"
        r = requests.get(url, auth=HTTPBasicAuth(FTC_USERNAME, FTC_TOKEN))
        leagues = r.json()
        leagues_in_region = defaultdict(str)

        for league in leagues["leagues"]:
            if league["region"] == region:
                leagues_in_region[league["name"]] = league["code"]

        return leagues_in_region
    
    def get_qualifiers(self, region_code):
        url = self.base_url + "events"
        r = requests.get(url, auth=HTTPBasicAuth(FTC_USERNAME, FTC_TOKEN))
        r.raise_for_status()

        events = r.json()["events"]
        qualifiers = defaultdict(str)

        for event in events:
            if event["regionCode"] == region_code and event["typeName"] == "Qualifier":
                qualifiers[event["name"]] = event["code"]

        return qualifiers
    
    def get_teams(self, event_code):
        url = self.base_url + "teams"
        r = requests.get(url, params={"eventCode": event_code}, auth=HTTPBasicAuth(FTC_USERNAME, FTC_TOKEN))
        r.raise_for_status()
        teams = r.json()
        full_teams = defaultdict(int)

        for team in teams["teams"]:
            full_teams[team["teamNumber"]] = team["nameShort"]

        return full_teams
    
    def get_events(self, region_code, league_code=None, use_league=True):
        url = self.base_url + "events"
        r = requests.get(url, auth=HTTPBasicAuth(FTC_USERNAME, FTC_TOKEN))
        r.raise_for_status()

        if league_code is not None:
            use_league = False

        events = r.json()["events"]
        filtered_events = defaultdict(str)
        filter_list = ["League Meet", "Qualifier", "Scrimmage", "League Tournament"]

        for event in events:
            if (event["leagueCode"] == league_code or use_league) and event["regionCode"] == region_code:
                if event["typeName"] in filter_list:
                    filtered_events[event["name"]] = event["code"]

        return filtered_events
    
    def get_unique(self, region_code):
        unique_events = set()
        events = self.get_events(region_code, use_league=False)
        leagues = self.get_leagues_in_region(region_code)

        for name in events.keys():
            base_name = re.sub(r'( )? #\d+$', '', name)
            unique_events.add(base_name)
        for league in leagues.keys():
            unique_events.add(league)

        unique_events = sorted(unique_events)

        return unique_events

if __name__ == '__main__':
    fetcher = FTCInfoFetcher()

    region = fetcher.get_team_region(15385)
    leagues = fetcher.get_leagues_in_region(region)
    teams = fetcher.get_teams("USCANOSBM1")

    events = fetcher.get_events(region, use_league=False)

    pprint.pprint(events)
    pprint.pprint(fetcher.get_unique(region))

"""
ENTER: team number
SELECT: League

EVENTS
- get events
TEAMS
- start with teams

CONFIGURE REGIONALS
CONFIGURE WORLDS

HIDE
- hide teams

"""