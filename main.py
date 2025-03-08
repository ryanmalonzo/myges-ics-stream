import logging
import os
import signal
import sys
import threading

import managers.auth as auth_manager
import managers.calendar as calendar_manager
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, Response
from waitress.server import create_server

FETCH_INTERVAL_MINUTES = int(os.environ.get("FETCH_INTERVAL_MINUTES", 60))

logging.basicConfig(
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)

scheduler = BackgroundScheduler()

app = Flask(__name__)

server = None
shutdown_event = threading.Event()


def signal_handler(signum, frame):
    """
    Handle interruption signals.
    """
    logging.info(f"Received signal {signum}. Shutting down gracefully...")

    # Shut down the scheduler
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logging.info("Scheduler shut down")

    # Signal the server to stop
    if server:
        shutdown_event.set()
        logging.info("Server shutdown requested")


@scheduler.scheduled_job("interval", minutes=FETCH_INTERVAL_MINUTES)
def _fetch_calendar() -> bytes:
    """
    Fetches the calendar from Skolae and returns it as an ICS file.
    """
    username, password = auth_manager.get_credentials().values()
    access_token = auth_manager.login(username, password)

    # Get timestamps for the current date and the date 1 month from now
    first_day_ms, last_day_ms = calendar_manager.get_date_range()

    # Fetch the calendar events
    calendar_json = calendar_manager.fetch_calendar(
        access_token, first_day_ms, last_day_ms
    )
    event_list = calendar_json["result"]

    # Create the ICS file
    calendar_ics = calendar_manager.convert_to_ical(event_list)

    with open("calendar.ics", "wb") as file:
        file.write(calendar_ics)
        logging.info("Updated calendar.ics")

    return calendar_ics


@app.get("/calendar")
def calendar():
    try:
        with open("calendar.ics", "r") as file:
            calendar_ics = calendar_manager.from_ical(file.read())
    except FileNotFoundError:
        calendar_ics = _fetch_calendar()

    response = Response(
        calendar_ics.decode("utf-8").strip(),
        mimetype="text/calendar",
    )

    logging.info("Served calendar.ics")
    return response


def run_server():
    """Run the server in a way that can be gracefully shut down."""
    global server
    server = create_server(app, host="0.0.0.0", port=8080)

    # Start the server
    logging.info("Starting server on port 8080")
    threading.Thread(target=server.run).start()

    # Wait for shutdown event
    shutdown_event.wait()

    # Close server
    server.close()
    logging.info("Server has been shut down")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    scheduler.start()
    logging.info("Scheduler started")

    # Run the server
    run_server()

    logging.info("Exiting application")
    sys.exit(0)
