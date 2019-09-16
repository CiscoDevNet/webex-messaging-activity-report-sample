# webex-teams-activity-report-sample 

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
import config
from datetime import datetime, timedelta

teamsAccessToken = config.teamsAccessToken

if teamsAccessToken in ( 'changeme', '' ):

    teamsAccessToken = input( 'Enter your Webex Teams access token: ' )

    while teamsAccessToken == '':

        teamsAccessToken = input( 'Enter your Webex Teams access token: ' )
else:

    teamsAccessToken = config.teamsAccessToken

startDate = config.startDate

if startDate in ( 'changeme', '' ):

    startDate = input( 'Enter report start date (YYY-MM-DD): ' )

    invalid = True

    while invalid:

        try:

            test = datetime.strptime( startDate, '%Y-%m-%d' )

            invalid = False

        except:

            startDate = input( 'Enter report start date (YYY-MM-DD): ' )

endDate = config.endDate

if endDate in ( 'changeme', '' ):

    endDate = input( f'Enter report end date (YYYY-MM-DD). *Enter* to use [{ startDate }]' )

    invalid = True
    
    while invalid:

        if endDate == '':

            endDate = startDate

            invalid = False

        else:

            try:

                test = datetime.strptime( endDate, '%Y-%m-%d' )

                invalid = False

            except:

                endDate = input( f'Enter report end date (YYYY-MM-DD). *Enter* to use [{ startDate }]' )

database = 'messages.db' if config.persistDatabase else ':memory:'

conn = sqlite3.connect( database )

if ( config.persistDatabase == False ) or ( config.persistDatabase and config.skipDownload == False ):

    data.importData( conn, teamsAccessToken, startDate, endDate )

criteria = {
    'mentioningMe': config.mentioningMe,
    'mentioningAll': config.mentioningAll,
    'directMessage': config.directMessage
}

report.generate( conn, teamsAccessToken, startDate, endDate, criteria )