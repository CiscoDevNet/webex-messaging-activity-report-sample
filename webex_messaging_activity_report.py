# webex-messaging-activity-report-sample

# Copyright (c) 2019 Cisco and/or its affiliates.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sqlite3

import data
import report
from datetime import datetime, timedelta
from uuid import uuid4
import re
from urllib import parse
import requests
from requests.auth import HTTPBasicAuth

# Edit .env file to specify optional configuration
import os
from dotenv import load_dotenv

load_dotenv(override=True)

webexAccessToken = os.getenv("webexAccessToken", "")
if webexAccessToken == "":
    webexClientId = os.getenv("webexClientId")
    webexClientSecret = os.getenv("webexClientSecret")
    webexRedirectUri = os.getenv("webexRedirectUri")

    if webexClientId and webexClientSecret and webexRedirectUri:
        state = str(uuid4())
        oauth2Url = ("https://webexapis.com/v1/authorize?"
            f"client_id={webexClientId}&"
            "response_type=code&"
            f"redirect_uri={parse.quote_plus(webexRedirectUri)}&"
            "scope=spark%3Akms%20spark%3Apeople_read%20spark%3Arooms_read%20spark%3Amessages_read&"
            f"state={state}"
        )
        code = ""
        while code == "":
            print(f"\nOAuth2 login URL: {oauth2Url}")
            codeUrl = input("\nEnter full response URL from the browser: ")
            match = re.search(r"\?.*code=(.*)\&", codeUrl)
            if match is None:
                print("\nURL provided does not include '?code='")
                exit(1)
            else:
                code = match.group(1)
        match = re.search(r".*?state=(.*)", codeUrl)
        if (match is None) or (match.group(1) != state) :
            print("\nRequest/response 'state' value mismatch")
            exit(1)
        try:
            resp = requests.post(
                "https://webexapis.com/v1/access_token",
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                auth = ( webexClientId, webexClientSecret),
                data = {
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": webexRedirectUri
                }
            )
            resp.raise_for_status()
            webexAccessToken = resp.json()["access_token"]
        except Exception as e:
                print(f"Error requesting access token: {e}\nExiting...")
                exit(1)
    else:            
        while webexAccessToken == "":
            webexAccessToken = input("Enter your Webex access token: ")

startDate = os.getenv("startDate", "")
date_valid = False
while not date_valid:
    while startDate == "":
        startDate = input("Enter report start date (YYY/MM/DD): ")
    try:
        datetime.strptime(startDate, "%Y/%m/%d")
        date_valid = True
    except:
        startDate = ""
        pass

endDate = os.getenv("endDate", "")
date_valid = False
while not date_valid:
    try:
        datetime.strptime(endDate, "%Y/%m/%d")
        date_valid = True
    except:
        endDate = input(f"Enter report end date (YYYY/MM/DD). *Enter* to use [{ startDate }]: ")
        endDate = startDate if endDate == "" else endDate

database = "messages.db" if (os.getenv("persistDatabase") != "") else ":memory:"

conn = sqlite3.connect(database)

conn.row_factory = sqlite3.Row

if database == ":memory:" or os.getenv("skipDownload") == "False":
    data.importData(conn, webexAccessToken, startDate, endDate)

criteria = {
    "mentioningMe": os.getenv("mentioningMe"),
    "mentioningAll": os.getenv("mentioningAll"),
    "directMessage": os.getenv("directMessage"),
}

report.generate(conn, webexAccessToken, startDate, endDate, criteria)
