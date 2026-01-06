from flask import Flask, render_template, send_file, jsonify, request
from collections import defaultdict
import pprint
import json
import os
import re
import shutil

from ftc_fetcher import FTCInfoFetcher

app = Flask(__name__)
fetcher = FTCInfoFetcher()
current_dir = os.getcwd()

import re

def normalize(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def filter_events(events, identifier):
    norm_id = normalize(identifier)
    id_tokens = set(norm_id.split())

    result = {}
    for name, code in events.items():
        norm_name = normalize(name)
        name_tokens = set(norm_name.split())

        if id_tokens.issubset(name_tokens):
            result[name] = code

    return result

def make_config():
    with open(current_dir + '/storage/config.json', "r") as f:
        configs = json.loads(f.read())

    teams = configs["teams"]
    base_info = {
        "pit_data": {
            "max-auto": -1,
            "max-teleop": -1,
            "sort": "",
            "turret": "",
            "shoot-speed": -1,
            "endgame": ""
        },
        "stats_data": {
            "shooting-percentage": -1,
            "auto-consistency": -1,
            "teleop-consistency": -1,
            "artifact-per-auto": -1,
            "artifact-per-teleop": -1,
            "foul-average": -1
        }
    }

    for person in configs["people"]:
        os.makedirs(f"{current_dir}/storage/personal_notes/{person.replace(' ', '-')}", exist_ok=True)
        for team_num  in teams:
            with open(f"{current_dir}/storage/personal_notes/{person.replace(' ', '-')}/{team_num}.txt", "w") as f:
                pass

    for event in configs["events"]:
        os.makedirs(f"{current_dir}/storage/team_notes/{event.replace(' ', '-')}", exist_ok=True)
        for team_num  in teams:
            team_info_path = f"{current_dir}/storage/team_notes/{event.replace(' ', '-')}/{team_num}.json"
            if not os.path.exists(team_info_path):
                with open(team_info_path, "w") as f:
                    f.write(json.dumps(base_info))

    people_dirs = [d.replace("-", " ") for d in os.listdir(f"{current_dir}/storage/personal_notes") if os.path.isdir(os.path.join(f"{current_dir}/storage/personal_notes", d))]
    to_delete = [x for x in people_dirs if x not in configs["people"]]
    for delete in to_delete:
        shutil.rmtree(f"{current_dir}/storage/personal_notes/{delete.replace(' ', '-')}")

    events_dirs = [d.replace("-", " ") for d in os.listdir(f"{current_dir}/storage/team_notes") if os.path.isdir(os.path.join(f"{current_dir}/storage/team_notes", d))]
    to_delete = [x for x in events_dirs if x not in configs["events"]]
    for delete in to_delete:
        shutil.rmtree(f"{current_dir}/storage/team_notes/{delete.replace(' ', '-')}")

    first_event = configs["events"][0].replace(" ", "-")
    teams_dirs = [f.replace(".json", "") for f in os.listdir(f"{current_dir}/storage/team_notes/{first_event}") if os.path.isfile(os.path.join(f"{current_dir}/storage/team_notes/{first_event}", f))]
    to_delete = [x for x in teams_dirs if x not in configs["teams"]]
    for event in configs["events"]:
        event = event.replace(" ", "-")
        for delete in to_delete:
            os.remove(f"{current_dir}/storage/team_notes/{event}/{delete}.json")


@app.route('/get-config', methods=['GET'])
def get_config():
    return send_file(current_dir + '/storage/config.json', mimetype='application/json', as_attachment=False)

@app.route('/set-config', methods=['POST'])
def set_config():
    data = request.get_json()

    with open(current_dir + '/storage/config.json', "w") as f:
        f.write(json.dumps(data, indent=4))

    make_config()

    return "", 200    

@app.route('/get-region-info', methods=['POST'])
def get_region_info():
    data = request.get_json()

    region = fetcher.get_team_region(data["config"]["my-team"])
    leagues = fetcher.get_unique(region)

    data["config"]["my-region"] = region
    data["config"]["leagues"] = leagues

    return jsonify(data)

@app.route('/get-teams-list', methods=['POST'])
def get_teams_list():
    data = request.get_json()
    identifier = data["identifier"].replace("FTC", "").replace("NorCal", "")
    region_code = data["region_code"]

    events = fetcher.get_events(region_code)
    events_filtered = filter_events(events, identifier)
    print(events_filtered)
    for key in events_filtered:
        if "Meet 1" in key or "QT" in key:
            code = events_filtered[key]

    teams = fetcher.get_teams(code)
    data["config"]["teams"] = teams
    data["config"]["events"] = list(events_filtered.keys())

    return jsonify(data["config"])

@app.route('/get-notes', methods=['POST'])
def get_notes():
    data = request.get_json()
    notes_dir = current_dir + '/storage/personal_notes/' + data["user"]
    response = defaultdict(int)

    for team_number in data["teams"]:
        with open(notes_dir + f"/{team_number}.txt", "r") as f:
            response[team_number] = f.read()

    return jsonify(response)

@app.route('/team-notes', methods=['POST'])
def team_notes():
    data = request.get_json()
    team = data["team"]

    notes = defaultdict(str)

    path = current_dir + "/storage/personal_notes"

    for entry in os.listdir(path):
        user_notes_path = os.path.join(path, entry)
        user = os.path.basename(user_notes_path)
        with open(user_notes_path + f"/{team}.txt", "r") as f:
            notes[user] = f.read()

    return jsonify(notes)

@app.route('/team-stats', methods=['POST'])
def team_stats():
    data = request.get_json()
    team = data["team"]
    event = data["event"]

    return send_file(current_dir + '/storage/team_notes/' + f"{event}/{team}.json", mimetype='application/json', as_attachment=False)

@app.route('/update-pit-form', methods=['POST'])
def update_pit_form():
    data = request.get_json()
    team = data["team"]
    event = data["event"]

    with open(current_dir + '/storage/team_notes/' + f"{event}/{team}.json", "r") as f:
        current_data = json.loads(f.read())

    with open(current_dir + '/storage/team_notes/' + f"{event}/{team}.json", "w") as f:
        current_data["pit_data"] = data["field"]
        f.write(json.dumps(current_data, indent=4))

    return "", 200

@app.route('/submit-notes', methods=['POST'])
def submit_notes():
    data = request.get_json()
    notes_dir = current_dir + '/storage/personal_notes/' + data["user"]

    for team_number, notes in data.items():
        with open(notes_dir + f"/{team_number}.txt", "w") as f:
            f.write(notes)

    return "", 200

@app.route('/notes/<username>')
def notes(username):
    return render_template('notebook.html', user=username)
@app.route('/team_data/<team>')
def team_data(team):
    return render_template('team_data.html', team=team)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/setup')
def setup():
    return render_template('setup.html')

if __name__ == '__main__':
    app.run(port=8000, debug=True)