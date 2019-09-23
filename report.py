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

from jinja2 import Environment, FileSystemLoader
import sqlite3
import webbrowser
from datetime import datetime, timedelta, timezone
from tzlocal import get_localzone
from webexteamssdk import WebexTeamsAPI

def generate( conn, teamsAccessToken, startDate, endDate, criteria ):

    c = conn.cursor()

    api = WebexTeamsAPI( access_token = teamsAccessToken )

    teamsId = api.people.me().id

    localTimeZone = get_localzone()

    def renderName( id, displayName ):

        return '<b>Me</b>' if id == teamsId else displayName

    def renderText( id, text, html):

        text = text if text is not None else ''

        text = html if html is not None else text

        return f'<b>{ text }</b>' if id == teamsId else text

    def renderShortDate( timeStr ):

        testDate = datetime.strptime( timeStr, '%Y-%m-%dT%H:%M:%S.%f%z' )

        return testDate.astimezone( localTimeZone ).strftime( '%m/%d %H:%M' )

    resp = c.execute( 'SELECT COUNT(*) FROM sqlite_master WHERE type="table" AND name="people"' )

    if resp.fetchone()[0] == 0:

        resp = c.execute(
            '''CREATE TABLE people (
                id text, 
                displayName text)'''
            )

        conn.commit

    startTime = localTimeZone.localize( datetime.strptime( startDate, '%Y-%m-%d' ) ).strftime( '%Y-%m-%dT%H:%M:%S.%f%z' )
    endTime = localTimeZone.localize( datetime.strptime( endDate, '%Y-%m-%d' ) + timedelta( days = 1 ) ).strftime( '%Y-%m-%dT%H:%M:%S.%f%z' )

    sqlMentioningMe = f'mentionedPeople like "%{ teamsId }" OR' if criteria[ 'mentioningMe' ] else ''
    sqlMentioningAll = 'mentionedGroups = \'["all"]\' OR' if criteria[ 'mentioningAll' ] else ''
    sqlDirectMessage = 'roomType = "direct" OR' if criteria[ 'directMessage' ] else ''
    sqlPersonId = f'personId = "{ teamsId }"'

    query = f'''
        SELECT DISTINCT messages.personId
        FROM messages LEFT OUTER JOIN people
        ON messages.personId = people.id
        WHERE
        people.id IS NULL AND 
        messages.created > "{ startTime }" AND
        messages.created < "{ endTime }" AND
        roomId IN
            ( SELECT roomId FROM messages WHERE
                { sqlMentioningMe }
                { sqlMentioningAll }
                { sqlDirectMessage }
                { sqlPersonId }
            )'''
        
    rows = c.execute( query )

    data = []

    for row in rows:

        personId = row[ 0 ]
        personName = '(Unknown)'

        try:
            person = api.people.get( personId )
            personName = person.displayName
        except:
            pass

        data.append( (
            personId,
            personName
        ) )

    c.executemany( 'INSERT INTO people VALUES (?,?)', data )

    conn.commit()

    query = f'''
    SELECT messages.*, people.displayName
    FROM messages LEFT OUTER JOIN people
    ON messages.personId = people.id
    WHERE
    messages.created > "{ startTime }" AND
    messages.created < "{ endTime }" AND
    roomId IN
        ( SELECT roomId FROM messages WHERE
            { sqlMentioningMe }
            { sqlMentioningAll }
            { sqlDirectMessage }
            { sqlPersonId }
        )
    ORDER BY messages.roomId, messages.created
    '''

    rows = c.execute( query )

    file_loader = FileSystemLoader( '.' )

    env = Environment( loader = file_loader, line_statement_prefix = '#' )

    html = env.get_template('template.html').render(
            startDate = startDate,
            endDate = endDate,
            rows = rows,
            renderShortDate = renderShortDate,
            renderName = renderName,
            renderText = renderText
        )

    with open( 'report.html', 'w', encoding = 'utf-8' ) as outfile:

        outfile.write( html )

    webbrowser.open( 'report.html' )
