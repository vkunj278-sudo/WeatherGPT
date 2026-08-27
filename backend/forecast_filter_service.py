from datetime import datetime, timedelta


def filter_forecast(forecast_data, time_period):

    if not forecast_data or "forecast" not in forecast_data:
        return forecast_data

    forecast_list = forecast_data["forecast"]

    today = datetime.now().date()

    filtered = []

    for item in forecast_list:

        try:
            forecast_datetime = datetime.strptime(
                item["datetime"],
                "%Y-%m-%d %H:%M:%S"
            )

            forecast_date = forecast_datetime.date()

        except (ValueError, TypeError, KeyError):
            continue

        # NOW
        if time_period == "NOW":

            if forecast_datetime >= datetime.now():
                filtered.append(item)
                break

        # TODAY
        elif time_period == "TODAY":

            if forecast_date == today:
                filtered.append(item)

        # TOMORROW
        elif time_period == "TOMORROW":

            tomorrow = today + timedelta(days=1)

            if forecast_date == tomorrow:
                filtered.append(item)

        # THIS WEEK
        elif time_period == "THIS_WEEK":

            if today <= forecast_date <= today + timedelta(days=6):
                filtered.append(item)

        # THIS WEEKEND
        elif time_period == "THIS_WEEKEND":

            days_until_saturday = (5 - today.weekday()) % 7

            saturday = today + timedelta(days=days_until_saturday)
            sunday = saturday + timedelta(days=1)

            if saturday <= forecast_date <= sunday:
                filtered.append(item)

        # FUTURE
        elif time_period == "FUTURE":

            if forecast_date > today:
                filtered.append(item)

        # UNKNOWN
        else:

            filtered.append(item)

    return {
        "location": forecast_data.get("location"),
        "forecast": filtered
    }