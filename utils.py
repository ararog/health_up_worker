import datetime
import pytz

class SystemDateTime:
    def __init__(self, date: str, time: str):
        self.date = date
        self.time = time

def actual_date_time() -> SystemDateTime:
    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.datetime.now(tz)
    return SystemDateTime(now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))
