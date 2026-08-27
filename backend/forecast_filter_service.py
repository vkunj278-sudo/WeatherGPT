from datetime import datetime, timedelta


def filter_forecast(forecast_data, time_period):

    if not forecast_data or "forecast" not in forecast_data:
        return forecast_data

    forecast_list = forecast_data["forecast"]

    today = datetime.now().date()

    if time_period == "NOW":
        return {
            "location": forecast_data.get("location"),
            "forecast": forecast_list[:1]
        }

    elif time_period == "TODAY":
        target_date = today

    elif time_period == "TOMORROW":
        target_date = today + timedelta(days=1)

    else:
        return forecast_data

    filtered = []

    for item in forecast_list:

        try:
            forecast_datetime = datetime.strptime(
                item["datetime"],
                "%Y-%m-%d %H:%M:%S"
            )

            if forecast_datetime.date() == target_date:
                filtered.append(item)

        except (ValueError, TypeError):
            continue

    return {
        "location": forecast_data.get("location"),
        "forecast": filtered
    }