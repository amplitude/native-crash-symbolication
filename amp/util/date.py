import datetime
import calendar

def start_of_week(d):
  return d - datetime.timedelta(days=d.weekday())

def end_of_week(d):
  return d + datetime.timedelta(days=6 - d.weekday())

def start_of_month(d):
  return d.replace(day=1)

def end_of_month(d):
  return d.replace(day=calendar.monthrange(d.year, d.month)[1])

def millisfromepoch(dt):
  epoch = datetime.datetime.utcfromtimestamp(0)
  delta = dt - epoch
  return int(delta.total_seconds() * 1000.0)

def utcfrommillis(timestamp):
  return datetime.datetime.utcfromtimestamp(timestamp / 1000.0)

def drange(start_date, end_date, step=1):
  cur_date = start_date
  while cur_date <= end_date:
    yield cur_date
    cur_date += datetime.timedelta(step)

def wrange(start_date, end_date):
  for d in drange(start_of_week(start_date), start_of_week(end_date), step=7):
    yield d

def mrange(start_date, end_date):
  start_month = start_of_month(start_date)
  end_month = start_of_month(end_date)
  ym_start = 12 * start_month.year + start_month.month - 1
  ym_end = 12 * end_month.year + end_month.month
  as_datetime = (isinstance(start_date, datetime.datetime) or
                 isinstance(end_date, datetime.datetime))
  for ym in range(ym_start, ym_end):
    y, m = divmod(ym, 12)
    if as_datetime:
      yield datetime.datetime(y, m + 1, 1)
    else:
      yield datetime.date(y, m+1, 1)
  

    
def isoformat(date):
  if date.tzinfo is None:
    return date.isoformat() + 'Z'
  else:
    return date.isoformat()
