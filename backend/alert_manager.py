from datetime import datetime


alerts = []


def create_alert(
    city,
    severity,
    warning,
    conditions
):

    # Check for duplicate active alert
    for existing_alert in alerts:

        same_city = (
            existing_alert["city"].lower()
            == city.lower()
        )

        same_severity = (
            existing_alert["severity"]
            == severity
        )

        same_warning = (
            existing_alert["warning"]
            == warning
        )

        same_conditions = (
            existing_alert["conditions"]
            == conditions
        )

        is_active = (
            existing_alert["status"]
            == "active"
        )

        if (
            same_city
            and same_severity
            and same_warning
            and same_conditions
            and is_active
        ):
            return existing_alert

    now = datetime.now().isoformat()

    alert = {
        "id": len(alerts) + 1,
        "city": city,
        "severity": severity,
        "warning": warning,
        "conditions": conditions,
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "resolved_at": None
    }

    alerts.append(alert)

    return alert


def get_alerts(city=None, status=None):

    result = alerts

    if city:

        result = [
            alert
            for alert in result
            if alert["city"].lower()
            == city.lower()
        ]

    if status:

        result = [
            alert
            for alert in result
            if alert["status"].lower()
            == status.lower()
        ]

    return result


def resolve_alert(alert_id):

    for alert in alerts:

        if alert["id"] == alert_id:

            now = datetime.now().isoformat()

            alert["status"] = "resolved"
            alert["updated_at"] = now
            alert["resolved_at"] = now

            return alert

    return None


def clear_alerts():

    alerts.clear()

    return {
        "message": "All alerts cleared."
    }