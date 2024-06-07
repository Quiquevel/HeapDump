from pytz import timezone, utc
from datetime import datetime
import logging.config
import logging
import os

log_level = 20
if(os.environ['LOGLEVEL'].upper()=='ERROR'):
  log_level = 40
if(os.environ['LOGLEVEL'].upper()=='WARNING'):
  log_level = 30
if(os.environ['LOGLEVEL'].upper()=='INFO'):
  log_level = 20
if(os.environ['LOGLEVEL'].upper()=='DEBUG'):
  log_level = 10
if(os.environ['LOGLEVEL'].upper()=='NOTSET'):
  log_level = 0

def customTime(*args):
    utc_dt = utc.localize(datetime.utcnow())
    my_tz = timezone(os.environ['TIMEZONE'])
    converted = utc_dt.astimezone(my_tz)
    return converted.timetuple()

def getLogger():
  return logger

logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s (%(filename)s:%(lineno)d)",datefmt="%Y-%m-%d %H:%M:%S")

logging.Formatter.converter = customTime
logger = logging.getLogger()
logger.setLevel(log_level)