# webex-messaging-activity-report-sample

## Overview

Produces a HTML report detailing user-related activity in Webex messaging for a given date range.

The user can input a Webex access token, start-, and end-dates.  The application will download messages from all rooms where the user was active - based on sent messages, @mentions, @all mentions or direct messages - then compile
an HTML report providing a readout of the rooms and their messages for the requested period.

Features:

* Message and user data can optionally be persisted (via SQLite)
* Message formatting/CSS is similar to the Webex web client
* Configurable room/message selection criteria
* Time zone aware

Uses the following components/technologies:

* [WebexTeamsSDK Python library](https://github.com/WebexCommunity/WebexPythonSDK) for messaging data retrieval.

* [Jinja2](https://jinja.palletsprojects.com/en/2.10.x/) for HTML report templating

* [SQLite](https://www.sqlite.org/index.html) for data storage/analysis

* [tzlocal](https://github.com/regebro/tzlocal) for local time zone discovery

Tested using:

* OS: Ubuntu Linux 19.04
* Python: 3.7.3
* Firefox: 69

[Webex for Developers Site](https://developer.webex.com/)

## Getting started

* Install Python 3.7+

    On Windows, choose the option to add to PATH environment variable

* The project was built/tested using [Visual Studio Code](https://code.visualstudio.com/)

    On first launch of VS Code, [install the Python plugin](https://code.visualstudio.com/docs/languages/python)

* Clone this repo to a directory on your PC:

    ```bash
    git clone https://github.com/CiscoDevNet/webex-messaging-activity-report-sample.git
    ```

* Dependency Installation:

    ```bash
    cd webex-messaging-activity-report-sample
    pip3 install -r requirements.txt
    ```
  
* Open the project in VS Code:

    ```bash
    code .
    ```

* Visit [http://developer.webex.com](https://developer.webex.com/docs/api/getting-started), login, navigate to **Documentation** / **Getting Started** and copy your personal access token

* In Visual Studio Code:

    * **OPTIONAL** - edit `config.py` to set credentials and preferences (be sure to save)

    * Press **F5** to run the application

    * Enter your access token and start/end dates
