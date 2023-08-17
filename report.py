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
from datetime import datetime, timedelta
import zoneinfo
from webexteamssdk import WebexTeamsAPI

def generate( conn, teamsAccessToken, startDate, endDate, criteria ):

    cursor = conn.cursor()

    api = WebexTeamsAPI( access_token = teamsAccessToken )

    teamsId = api.people.me().id

    def renderName( id, displayName ):

        return '<b>You</b>' if id == teamsId else displayName

    def renderRow( id ):

        return '<tr class="mention-row">' if id == teamsId else '<tr>'

    def renderText( id, text, html, parentId ):

        cssClass = 'activity-item--message'

        cssClass = cssClass if parentId is None else 'activity-item activity-threading-reply ' + cssClass

        cssClass = cssClass if id != teamsId else cssClass + ' message-mine'

        text = text if text is not None else ''

        text = html if html is not None else text

        return f'<td class="{ cssClass}"><div class="message-cell">{ text }</div></td>'

    def renderShortDate( timeStr ):

        testDate = datetime.strptime( timeStr, '%Y-%m-%dT%H:%M:%S.%f%z' )

        return testDate.astimezone().strftime( '%m/%d %H:%M' )

    resp = cursor.execute( 'SELECT COUNT(*) FROM sqlite_master WHERE type="table" AND name="people"' )

    if resp.fetchone()[0] == 0:

        resp = cursor.execute(
            '''CREATE TABLE people (
                id text, 
                displayName text,
                avatar text)'''
            )

        conn.commit

    print('Retrieving people...', end = '' )

    startTime = ( datetime.strptime( startDate, '%Y/%m/%d' ) ).astimezone( zoneinfo.ZoneInfo( 'UTC' ) )
    startTime = startTime.strftime( '%Y-%m-%dT%H:%M:%S.%f%z' )
    endTime = ( datetime.strptime( endDate, '%Y/%m/%d' ) + timedelta( days = 1 ) ).astimezone( zoneinfo.ZoneInfo( 'UTC' ) )
    endTime = endTime.strftime( '%Y-%m-%dT%H:%M:%S.%f%z' )
    
    sqlMentioningMe = f'mentionedPeople like "%{ teamsId }%" OR' if criteria[ 'mentioningMe' ] else ''
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
        
    rows = cursor.execute( query )

    data = []

    peopleCount = 0

    for row in rows:

        peopleCount += 1

        print( f'\rRetrieving people: {peopleCount}', end='')        

        personId = row[ 0 ]

        try:
            person = api.people.get( personId )
            data.append( ( person.id,
                person.displayName if bool(person.displayName) else 'Unknown',
                person.avatar if bool(person.avatar) else None ) )
        except:
            data.append( ( personId, 'Unknown', None ) )
            pass

    cursor.executemany( 'INSERT INTO people VALUES (?,?,?)', data )

    conn.commit()

    print('\nGenerating report...', end = '' )

    query = f'''
    SELECT messages.*, people.displayName, people.avatar
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
    ORDER BY messages.roomId, messages.threadCreated, messages.created
    '''

    rows = cursor.execute( query )

    file_loader = FileSystemLoader( '.' )

    env = Environment( loader = file_loader, line_statement_prefix = '#' )

    html = env.get_template('template.html').render(
            startDate = startDate,
            endDate = endDate,
            rows = rows,
            renderShortDate = renderShortDate,
            renderName = renderName,
            renderText = renderText,
            renderRow = renderRow
        )

    with open( 'www/report.html', 'w', encoding = 'utf-8' ) as outfile:

        outfile.write( html )

    webbrowser.open( 'www/report.html' )

    print('\rReport complete     ')

