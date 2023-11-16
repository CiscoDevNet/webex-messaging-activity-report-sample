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

# Edit .env file to specify optional configuration
import os
from dotenv import load_dotenv

load_dotenv(override=True)

webexAccessToken = os.getenv("webexAccessToken")

if webexAccessToken == "":
    webexAccessToken = input("Enter your Webex access token: ")

    while webexAccessToken == "":
        webexAccessToken = input("Enter your Webex access token: ")

startDate = os.getenv("startDate")

if startDate == "":
    startDate = input("Enter report start date (YYY/MM/DD): ")

    invalid = True

    while invalid:
        try:
            test = datetime.strptime(startDate, "%Y/%m/%d")

            invalid = False

        except:
            startDate = input("Enter report start date (YYY/MM/DD): ")

endDate = os.getenv("endDate")

if endDate == "":
    endDate = input(
        f"Enter report end date (YYYY/MM/DD). *Enter* to use [{ startDate }]"
    )

    invalid = True

    while invalid:
        if endDate == "":
            endDate = startDate

            invalid = False

        else:
            try:
                test = datetime.strptime(endDate, "%Y/%m/%d")

                invalid = False

            except:
                endDate = input(
                    f"Enter report end date (YYYY/MM/DD). *Enter* to use [{ startDate }]"
                )

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
