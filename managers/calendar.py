import datetime

import httpx
from dateutil.relativedelta import relativedelta
from ics import Calendar, Event


def get_date_range(months_offset=0):
    """
    Calculate the first and last millisecond timestamps of a month.

    Args:
        months_offset (int): Number of months to offset from the current month. Default is 0.

    Returns:
        tuple: Two millisecond timestamps (first_day, last_day) of the month.
    """
    # Get the first day of the target month
    first_day = datetime.datetime.today().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    first_day += relativedelta(months=months_offset)

    # Calculate the last day of the target month
    next_month = first_day + relativedelta(months=1)
    last_day = next_month - datetime.timedelta(days=1)
    last_day = last_day.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Convert to millisecond timestamps
    first_day_ms = int(first_day.timestamp() * 1000)
    last_day_ms = int(last_day.timestamp() * 1000)

    return first_day_ms, last_day_ms


def fetch_calendar(access_token: str, first_day_ms: int, last_day_ms: int):
    """
    Fetches the calendar events from Skolae.

    Args:
        access_token (str): Access token to authenticate with Skolae.
        first_day_ms (int): Millisecond timestamp of the first day of the month.
        last_day_ms (int): Millisecond timestamp of the last day of the month.

    Returns:
        list: List of calendar events.
    """
    headers = {
        "accept-encoding": "gzip",
        "authorization": f"Bearer {access_token}",
        "connection": "Keep-Alive",
        "user-agent": "okhttp/3.13.1",
    }

    response = httpx.get(
        f"https://api.kordis.fr/me/agenda?start={first_day_ms}&end={last_day_ms}",
        headers=headers,
    )

    response.raise_for_status()

    return response.json()


def convert_to_ics(event_list: list) -> str:
    """
    Converts the calendar events to an ICS file.

    Args:
        event_list (list): List of calendar events.

    Returns:
        str: ICS file content.
    """
    calendar = Calendar()

    for event in event_list:
        campuses = (
            ", ".join(
                set(room["campus"] for room in event["rooms"] if "campus" in room)
            )
            if event["rooms"]
            else "No campus"
        )
        rooms = (
            ", ".join(set(room["name"] for room in event["rooms"] if "name" in room))
            if event["rooms"]
            else "No room"
        )
        description = f"{campuses}\n" f"{rooms}\n" f"{event['teacher']}\n"

        begin = datetime.datetime.fromtimestamp(event["start_date"] / 1000)
        end = datetime.datetime.fromtimestamp(event["end_date"] / 1000)

        event = Event(name=event["name"], description=description, begin=begin, end=end)
        calendar.events.add(event)

    return calendar.serialize()
