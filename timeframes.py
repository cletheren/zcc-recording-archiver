"""Functions to return various timeframes"""

from datetime import datetime, timedelta
import calendar


def last_month() -> dict[str, str]:
    """Return a tuple containing the start and end times of the previous month in iso format"""
    one_month_ago = datetime.now() - timedelta(weeks=4)
    days_in_month = calendar.monthrange(one_month_ago.year, one_month_ago.month)[-1]
    start_date = datetime(one_month_ago.year, one_month_ago.month, 1).isoformat(timespec="seconds")
    end_date = datetime(one_month_ago.year, one_month_ago.month, days_in_month, 23, 59, 59).isoformat(timespec="seconds")
    return {"from": start_date, "to": end_date}


def last_week():
    """Return a tuple containing the start and end times of the previous week in iso format"""
    date_today = datetime.now()
    beginning_last_week = date_today - timedelta(days=6 + date_today.day)
    end_last_week = date_today - timedelta(days=date_today.day)
    start_date_components = [int(x) for x in str(beginning_last_week.date()).split("-")]
    end_date_components = [int(x) for x in str(end_last_week.date()).split("-")]
    start_date = datetime(*start_date_components, 0, 0, 0).isoformat(timespec="seconds")
    end_date = datetime(*end_date_components, 23, 59, 59).isoformat(timespec="seconds")
    return {"from": start_date, "to": end_date}


def last_seven_days() -> dict[str, str]:
    """Return a tuple containing the start and end times of the previous month in iso format"""
    date_today = datetime.now()
    one_week_ago = date_today - timedelta(weeks=1)
    start_date_components = [int(x) for x in str(one_week_ago.date()).split("-")]
    end_date_components = [int(x) for x in str(date_today.date()).split("-")]
    start_date = datetime(*start_date_components, 0, 0, 0).isoformat(timespec="seconds")
    end_date = datetime(*end_date_components, 23, 59, 59).isoformat(timespec="seconds")
    return {"from": start_date, "to": end_date}


def today() -> dict[str, str]:
    """Return a tuple containing the start and end times of the current day in iso format"""
    date_components = [int(x) for x in str(datetime.now().date()).split("-")]
    start_date = datetime(*date_components, 0, 0, 0).isoformat(timespec="seconds")
    end_date = datetime(*date_components, 23, 59, 59).isoformat(timespec="seconds")
    return {"from": start_date, "to": end_date}


def yesterday() -> dict[str, str]:
    """Return a tuple containing the start and end times of yesterday in iso format"""
    date_yesterday = datetime.now() - timedelta(days=1)
    date_components = [int(x) for x in str(date_yesterday.date()).split("-")]
    start_date = datetime(*date_components, 0, 0, 0).isoformat(timespec="seconds")
    end_date = datetime(*date_components, 23, 59, 59).isoformat(timespec="seconds")
    return {"from": start_date, "to": end_date}
