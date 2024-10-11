# myges-ics-stream

Serving my class schedule over HTTP as iCalendar for easy importing.  

## Why?

It often takes several minutes to load one's timetable from my school's offical website.  
This small Python program provides an HTTP endpoint that will serve the provided user's schedule in iCalendar format, and that can be subscribed to using one's favorite calendar app.  

<img width="1047" alt="image" src="https://github.com/user-attachments/assets/7b5c60ab-4605-45b9-90c9-3732e706b98e">

## How to run

Clone the repository, set the required environment variables in `.env`, then run  

```sh
docker compose up -d
```

Alternatively, use the Docker image available on [Docker Hub](https://hub.docker.com/r/ryanmalonzo/myges-ics-stream), like so:  

```yml
services:
  myges-ics-stream:
    image: ryanmalonzo/myges-ics-stream:latest
    container_name: myges
    environment:
      MYGES_USERNAME: ${MYGES_USERNAME}
      MYGES_PASSWORD: ${MYGES_PASSWORD}
    restart: unless-stopped
```

## Environment variables

| Environment variable | Description | Example value | Required? |
|---|---|---|---|
| MYGES_USERNAME | Your MyGES username. | rmalonzo | True |
| MYGES_PASSWORD | Your MyGES password. | mypassword123 | True |
| FETCH_INTERVAL_MINUTES | The time until each refresh of the calendar. Defaults to 60 minutes. | 120 | False |
| TIMEZONE | The TZ identifier for the calendar as described [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). Defaults to Europe/Paris. | Asia/Tokyo | False |

## Acknowledgements

- [UnBonWhisky/myges-to-icalendar](https://github.com/UnBonWhisky/myges-to-icalendar) for the API endpoints.
