from typing import Self

import re
from datetime import datetime, date, time, timedelta
from dateutil.parser import parse
from dateutil.rrule import (
    rrule, rruleset, 
    DAILY, WEEKLY, MONTHLY, YEARLY, 
    MO, TU, WE, TH, FR, SA, SU, 
    )


def generateDT(*args) -> datetime:
    D = datetime.today()        # default to today
    if len(args) > 3:
        YY = int(args[0])
        MM = int(args[1])
        DD = int(args[2])
        hh = int(args[3])
        mm = int(args[4]) if len(args) > 4 else 0
        ss = int(args[5]) if len(args) > 5 else 0
        us = int(args[6]) if len(args) > 6 else 0
        D = datetime(YY,MM,DD,hh,mm,ss,us)
    elif len(args) == 3:  # year, month, day was passed in
        YY, MM, DD = map(int, args)
        D = datetime(YY,MM,DD)
    elif len(args) == 2:    # month, day passed in , year should be current year
        YY = date.today().year
        MM, DD = map(int, args)
        D = datetime(YY,MM,DD)
    elif len(args) == 1:    # either a date string or date object passed in
        if isinstance(args[0],(date, datetime)):
            D = datetime.combine(args[0], datetime.min.time()) \
                if isinstance(args[0], date) and not isinstance(args[0], datetime) else args[0]
        else:
            try:
                D = parse(str(args[0]))
            except Exception:
                D = datetime.today()                
    else:
        # invalid number of args.  Do nothing; let the default stand
        pass
    return D
# generateDT

def daysfrom(in_date:date, delta:int) -> date:
    R_dt = in_date + timedelta(days=delta)
    return R_dt
def tomorrow(in_date:date) -> date:
    return daysfrom(in_date, 1)
def yesterday(in_date:date) -> date:
    return daysfrom(in_date, -1)

def nextWorkdayAfter(in_date:date, nonWorkdays={SA,SU}, extraNonWorkdayList={}, include_afterdate=False):
    in_datetime = datetime.combine(in_date, time.min)
    
    excRule = rrule(WEEKLY,dtstart=in_datetime,byweekday=nonWorkdays)
    afterdaysRule = rrule(DAILY,dtstart=in_datetime)

    exclSet = rruleset()
    exclSet.rrule(afterdaysRule)
    exclSet.exrule(excRule)
    # loop extraNonWorkdays into exclSet.exdate
    for xDate in extraNonWorkdayList:
        exclSet.exdate(xDate)

    return exclSet.after(in_datetime,include_afterdate)

def IsDateString(datestr) -> bool:
    try:
        D = parse(datestr)
        return True
    except:
        return False
# IsDateString
    
def parse_relative_time(time_string, reference_time=None) -> datetime:
    """
    Convert relative time strings to datetime objects.
    
    Examples: "2 hours ago", "3 days ago", "1 week ago"
    """
    if reference_time is None:
        reference_time = datetime.now()
    
    # Normalize the string
    time_string = time_string.lower().strip()
    
    # Pattern: number + time unit + "ago"
    pattern = r'(\d+)\s*(second|minute|hour|day|week|month|year)s?\s*ago'
    match = re.match(pattern, time_string)
    
    if not match:
        raise ValueError(f"Cannot parse: {time_string}")
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    # Map units to timedelta kwargs
    unit_mapping = {
        'second': 'seconds',
        'minute': 'minutes',
        'hour': 'hours',
        'day': 'days',
        'week': 'weeks',
    }
    
    if unit in unit_mapping:
        delta_kwargs = {unit_mapping[unit]: amount}
        return reference_time - timedelta(**delta_kwargs)
    elif unit == 'month':
        # Approximate: 30 days per month
        return reference_time - timedelta(days=amount * 30)
    elif unit == 'year':
        # Approximate: 365 days per year
        return reference_time - timedelta(days=amount * 365)
    else:
        return reference_time
    # endif unit
# parse_relative_time

def extract_date_from_text(text, current_year=None) -> datetime|None:
    """
    Extract dates from natural language text.
    
    Handles formats like:
    - "January 15th, 2024"
    - "March 3rd"
    - "Dec 25th, 2023"
    """
    if current_year is None:
        current_year = datetime.now().year
    
    # Month names (full and abbreviated)
    months = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12
    }
    
    # Pattern: Month Day(st/nd/rd/th), Year (year optional)
    pattern = r'(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|sept|october|oct|november|nov|december|dec)\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?'
    
    matches = re.findall(pattern, text.lower())
    
    if not matches:
        return None
    
    # Take the first match
    month_str, day_str, year_str = matches[0]
    
    month = months[month_str]
    day = int(day_str)
    year = int(year_str) if year_str else current_year
    
    return datetime(year, month, day)
# extract_date_from_text


def parse_flexible_date(date_string) -> datetime:
    """
    Parse dates in multiple common formats.
    
    Tries various formats and returns the first match.
    """
    date_string = date_string.strip()
    
    # List of common date formats
    formats = [
        '%Y-%m-%d',           
        '%Y/%m/%d',           
        '%d-%m-%Y',           
        '%d/%m/%Y',         
        '%m/%d/%Y',           
        '%d.%m.%Y',          
        '%Y%m%d',            
        '%B %d, %Y',      
        '%b %d, %Y',         
        '%d %B %Y',          
        '%d %b %Y',           
    ]
    
    # Try each format
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    # If nothing worked, raise an error
    raise ValueError(f"Unable to parse date: {date_string}")
    # consider return None - change fn signature if you do that
# parse_flexible_date


def parse_duration(duration_string) -> timedelta:
    """
    Parse duration strings into timedelta objects.
    
    Handles formats like:
    - "1h 30m 45s"
    - "2:45:30" (H:M:S)
    - "90 minutes"
    - "1.5 hours"
    """
    duration_string = duration_string.strip().lower()
    
    # Try colon format first (H:M:S or M:S)
    if ':' in duration_string:
        parts = duration_string.split(':')
        if len(parts) == 2:
            # M:S format
            minutes, seconds = map(int, parts)
            return timedelta(minutes=minutes, seconds=seconds)
        elif len(parts) == 3:
            # H:M:S format
            hours, minutes, seconds = map(int, parts)
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        # end if colon format
    
    # Try unit-based format (1h 30m 45s)
    total_seconds = 0
    
    # Find hours
    hours_match = re.search(r'(\d+(?:\.\d+)?)\s*h(?:ours?)?', duration_string)
    if hours_match:
        total_seconds += float(hours_match.group(1)) * 3600
    
    # Find minutes
    minutes_match = re.search(r'(\d+(?:\.\d+)?)\s*m(?:in(?:ute)?s?)?', duration_string)
    if minutes_match:
        total_seconds += float(minutes_match.group(1)) * 60
    
    # Find seconds
    seconds_match = re.search(r'(\d+(?:\.\d+)?)\s*s(?:ec(?:ond)?s?)?', duration_string)
    if seconds_match:
        total_seconds += float(seconds_match.group(1))
    
    if total_seconds > 0:
        return timedelta(seconds=total_seconds)
    
    raise ValueError(f"Unable to parse duration: {duration_string}")
    # consider return timedelta() - change fn signature if you do that
# parse_duration


def parse_iso_week_date(iso_week_string) -> datetime:
    """
    Parse ISO week date format: YYYY-Www-D
    
    Example: "2024-W03-2" = Week 3 of 2024, Tuesday
    
    ISO week numbering:
    - Week 1 is the week with the first Thursday of the year
    - Days are numbered 1 (Monday) through 7 (Sunday)
    """
    # Parse the format: YYYY-Www-D
    parts = iso_week_string.split('-')
    
    if len(parts) != 3 or not parts[1].startswith('W'):
        raise ValueError(f"Invalid ISO week format: {iso_week_string}")
    
    year = int(parts[0])
    week = int(parts[1][1:])  # Remove 'W' prefix
    day = int(parts[2])
    
    if not (1 <= week <= 53):
        raise ValueError(f"Week must be between 1 and 53: {week}")
    
    if not (1 <= day <= 7):
        raise ValueError(f"Day must be between 1 and 7: {day}")
    
    # Find January 4th (always in week 1)
    jan_4 = datetime(year, 1, 4)
    
    # Find Monday of week 1
    week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
    
    # Calculate the target date
    target_date = week_1_monday + timedelta(weeks=week - 1, days=day - 1)
    
    return target_date
# parse_iso_week_date
