from pytz import timezone, utc
from datetime import datetime
import os
from time import sleep, time, gmtime, strftime




def customTime(*args):
    utc_dt = utc.localize(datetime.utcnow())
    my_tz = timezone(os.environ['TIMEZONE'])
    converted = utc_dt.astimezone(my_tz)
    date = converted.strftime("%m/%d/%Y %H:%M:%S")
    return date