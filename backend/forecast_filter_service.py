from datetime import datetime, timedelta


def _parse_datetime(value):

    if not value:
        return None

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f"
    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                value,
                fmt
            )

        except ValueError:
            continue

    return None


def filter_forecast(
    forecast_data,
    time_period
):

    if (
        not forecast_data
        or "forecast" not in forecast_data
    ):
        return forecast_data

    forecast_list = forecast_data.get(
        "forecast",
        []
    )

    if not forecast_list:
        return {
            "location": forecast_data.get(
                "location"
            ),
            "forecast": []
        }

    parsed_items = []

    for item in forecast_list:

        forecast_datetime = _parse_datetime(
            item.get("datetime")
        )

        if forecast_datetime is not None:

            parsed_items.append(
                (
                    forecast_datetime,
                    item
                )
            )

    if not parsed_items:

        return {
            "location": forecast_data.get(
                "location"
            ),
            "forecast": []
        }

    # The forecast timestamps from OpenWeather's
    # 5-day/3-hour forecast are already formatted
    # as local city forecast times by the API.
    #
    # Therefore we use the dates represented by
    # those timestamps rather than trying to convert
    # them using the computer's timezone.

    today = datetime.now().date()

    # -----------------------------------------------------
    # NOW
    # -----------------------------------------------------

    if time_period == "NOW":

        now_item = min(
            parsed_items,
            key=lambda pair: abs(
                (pair[0] - datetime.now()).total_seconds()
            )
        )

        filtered = [now_item[1]]

    # -----------------------------------------------------
    # TODAY
    # -----------------------------------------------------

    elif time_period == "TODAY":

        filtered = [
            item
            for dt, item in parsed_items
            if dt.date() == today
        ]

    # -----------------------------------------------------
    # TOMORROW
    # -----------------------------------------------------

    elif time_period == "TOMORROW":

        tomorrow = today + timedelta(days=1)

        filtered = [
            item
            for dt, item in parsed_items
            if dt.date() == tomorrow
        ]

    # -----------------------------------------------------
    # THIS WEEK
    # -----------------------------------------------------

    elif time_period == "THIS_WEEK":

        end_date = today + timedelta(days=6)

        filtered = [
            item
            for dt, item in parsed_items
            if today <= dt.date() <= end_date
        ]

    # -----------------------------------------------------
    # THIS WEEKEND
    # -----------------------------------------------------

    elif time_period == "THIS_WEEKEND":

        days_until_saturday = (
            5 - today.weekday()
        ) % 7

        saturday = (
            today
            + timedelta(
                days=days_until_saturday
            )
        )

        sunday = saturday + timedelta(
            days=1
        )

        filtered = [
            item
            for dt, item in parsed_items
            if saturday <= dt.date() <= sunday
        ]

    # -----------------------------------------------------
    # FUTURE
    # -----------------------------------------------------

    elif time_period == "FUTURE":

        filtered = [
            item
            for dt, item in parsed_items
            if dt.date() > today
        ]

    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------

    else:

        filtered = [
            item
            for _, item in parsed_items
        ]

    return {
        "location": forecast_data.get(
            "location"
        ),
        "forecast": filtered
    }