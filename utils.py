import datetime
import pytz

class SystemDateTime:
    def __init__(self, date_time: str):
        self.date_time = date_time

def actual_date_time(tz) -> SystemDateTime:
    tz = pytz.timezone(tz)
    now = datetime.datetime.now(tz)
    return SystemDateTime(now.strftime("%Y-%m-%dT%H:%M:%S%z"))
