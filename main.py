import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, make_response

import managers.auth as auth_manager
import managers.calendar as calendar_manager

FETCH_INTERVAL_MINUTES = int(os.environ.get("FETCH_INTERVAL_MINUTES", 60))

scheduler = BackgroundScheduler()

app = Flask(__name__)


@scheduler.scheduled_job("interval", minutes=FETCH_INTERVAL_MINUTES)
def _fetch_calendar() -> str:
    """
    Fetches the calendar from Skolae and returns it as an ICS file.
    """
    username, password = auth_manager.get_credentials().values()
    access_token = auth_manager.login(username, password)

    # Get timestamps for the first and last day of the current month
    first_day_ms, last_day_ms = calendar_manager.get_date_range()

    # Fetch the calendar events
    calendar_json = calendar_manager.fetch_calendar(
        access_token, first_day_ms, last_day_ms
    )
    event_list = calendar_json["result"]

    # Create the ICS file
    calendar_ics = calendar_manager.convert_to_ics(event_list)

    with open("calendar.ics", "w") as file:
        file.write(calendar_ics)

    return calendar_ics


@app.get("/calendar")
def calendar():
    try:
        with open("calendar.ics", "r") as file:
            calendar_ics = file.read()
    except FileNotFoundError:
        calendar_ics = _fetch_calendar()

    response = make_response(calendar_ics)
    response.headers["Content-Type"] = "text/calendar"
    response.headers["Content-Disposition"] = "attachment; filename=calendar.ics"

    return response


if __name__ == "__main__":
    from waitress import serve

    scheduler.start()
    serve(app, host="127.0.0.1", port=8080)
