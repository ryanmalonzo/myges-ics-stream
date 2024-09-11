import base64
import json
import logging
import os
import time
from urllib.parse import parse_qs, urlparse

import httpx


def get_credentials() -> dict:
    """
    Retrieves the credentials from the myges.json file.
    """
    username = os.environ.get("MYGES_USERNAME")
    password = os.environ.get("MYGES_PASSWORD")

    if username is None or password is None:
        raise ValueError("Missing username or password")

    logging.debug(f"Retrieved username {username} and password {password}")
    return {"username": username, "password": password}


def _b64encode_credentials(username: str, password: str) -> str:
    """
    Encodes credentials to base64 for basic authentication header.
    """
    credentials = bytes(f"{username}:{password}", "utf-8")
    credentials = base64.b64encode(credentials).decode("utf-8")
    return credentials


def login(username, password) -> str:
    """
    Logins to myGES using provided credentials.
    """
    # Check for valid access token in cache
    try:
        with open("token.json", "r") as file:
            data = json.load(file)
            if data["username"] == username:
                expires_in = data["expires_in"]
                timestamp = data["timestamp"]
                access_token = data["access_token"]

                if time.time() - timestamp < expires_in:
                    logging.info(f"Using cached access token {access_token}")
                    return access_token
    except FileNotFoundError:
        pass

    base64_credentials = _b64encode_credentials(username, password)
    headers = {
        "accept-encoding": "gzip",
        "authorization": f"Basic {base64_credentials}",
        "connection": "Keep-Alive",
        "user-agent": "okhttp/3.13.1",
    }

    response = httpx.get(
        "https://authentication.kordis.fr/oauth/authorize?response_type=token&client_id=skolae-app",
        headers=headers,
    )

    if response.status_code != 302:
        raise httpx.HTTPError("Invalid credentials")

    parsed_url = urlparse(response.headers["location"])
    params = parse_qs(parsed_url.fragment)
    access_token = params["access_token"][0]
    expires_in = int(params["expires_in"][0])

    # Cache the access token for future queries
    with open("token.json", "w") as file:
        json.dump(
            {
                "username": username,
                "access_token": access_token,
                "expires_in": expires_in,
                "timestamp": time.time(),
            },
            file,
        )

    logging.debug(f"Received access token {access_token}")
    logging.debug(f"Token expires in {expires_in} seconds")
    return access_token
