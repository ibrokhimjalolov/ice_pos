import datetime


def parse_date(date_str, date_format="%Y-%m-%d"):
    if not date_str:
        return None
    return datetime.datetime.strptime(date_str, date_format).date()
