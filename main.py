import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = "HardCodedToken"
RSA_API_KEY = ""

app = Flask(__name__)


def generate_weather(city: str, date: str):
    url = "https://visual-crossing-weather.p.rapidapi.com/history"

    querystring = {"startDateTime": date, "aggregateHours": "24", "location": city,
                   "endDateTime": date, "unitGroup": "metric", "contentType": "json",
                   "shortColumnNames": "0"}

    headers = {
        "X-RapidAPI-Key": RSA_API_KEY,
        "X-RapidAPI-Host": "visual-crossing-weather.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def weather_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)


    if json_data.get("requester_name") is None:
        raise InvalidUsage("requester_name is required", status_code=400)

    requester_name = json_data.get("requester_name")


    if json_data.get("location") is None:
        raise InvalidUsage("location is required", status_code=400)

    location = json_data.get("location")


    if json_data.get("date") is None:
        raise InvalidUsage("date is required", status_code=400)

    date = json_data.get("date")

    date = date + "T00:00:00"
    weather = generate_weather(location, date)

    end_dt = dt.datetime.now(dt.timezone.utc)
    res = weather["locations"][next(iter(weather["locations"].keys()))]["values"][0]
    res.pop('datetime')
    res.pop('datetimeStr')
    res.pop('info')
    res.pop('wgust')
    result = {
        "requester_name": requester_name,
        "timestamp": end_dt.isoformat(),
        "location": next(iter(weather["locations"].keys())),
        "date": date,
        "weather": res
    }

    return result