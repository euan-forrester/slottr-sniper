#!/usr/bin/env python3

from datetime import datetime, timedelta
import pytz
import time
import sys
import configparser
import os
import slottr

CONFIG_FILE = '../config/config.ini'

# TODO: Make sure we're not trying to signup more than 48 hours in advance. Is this actually checked?

#
# Get our config
#

environment = 'dev'

if 'ENVIRONMENT' in os.environ:
    environment = os.environ.get('ENVIRONMENT')

print(f'Running in {environment} mode')

config = configparser.ConfigParser()

config.read(CONFIG_FILE)

desired_slottr_url = config.get(environment, 'slottr-url')
desired_signup_name = config.get(environment, 'signup-name')
desired_signup_email = config.get(environment, 'signup-email')
desired_signup_phone = config.get(environment, 'signup-phone')
desired_signup_condo = config.get(environment, 'signup-condo')
desired_signup_building = config.get(environment, 'signup-building-initial')
desired_signup_notes = config.get(environment, 'signup-notes')

timezone_name = config.get(environment, 'timezone-name')
time_slots_added_hour = config.getint(environment, 'time-slots-added-hour')
time_slots_added_minute = config.getint(environment, 'time-slots-added-minute')
minutes_early_to_begin = config.getint(environment, 'minutes-early-to-begin')
minutes_later_to_end = config.getint(environment, 'minutes-later-to-end')
seconds_between_attempts = config.getint(environment, 'seconds-between-attempts')

desired_signup_year = config.getint(environment, 'desired-year')
desired_signup_month = config.getint(environment, 'desired-month')
desired_signup_day = config.getint(environment, 'desired-day')
desired_signup_hour = config.getint(environment, 'desired-hour')

desired_datetime = datetime(desired_signup_year, desired_signup_month, desired_signup_day, desired_signup_hour)

desired_signup_info = slottr.SignupInfo(desired_signup_name, desired_signup_email, desired_signup_phone, desired_signup_condo, desired_signup_building, desired_signup_notes)

def get_current_time_in_timezone(timezone_name):
    return lambda : datetime.now(pytz.timezone(timezone_name))

get_current_time = get_current_time_in_timezone(timezone_name)

#
# Wait until we're the desired number of minutes before slots are going to be added
#

current_time = get_current_time()

time_slots_added = current_time.replace(hour=time_slots_added_hour, minute=time_slots_added_minute, second=0, microsecond=0)
time_begin_checking = time_slots_added - timedelta(minutes=minutes_early_to_begin)
time_finish_checking = time_slots_added + timedelta(minutes=minutes_later_to_end)

while current_time > time_finish_checking:
    time_slots_added = time_slots_added + timedelta(days=1)
    time_begin_checking = time_begin_checking + timedelta(days=1)
    time_finish_checking = time_finish_checking + timedelta(days=1)

print(f'Current time is {current_time}')
print(f'Time slots are added is {time_slots_added}')
print(f'Time to begin checking: {time_begin_checking}')
print(f'Time to finish checking: {time_finish_checking}')

if current_time < time_begin_checking:
    how_long_to_wait_until_begin_checking_seconds = (time_begin_checking - current_time).seconds

    print(f'Sleeping for {how_long_to_wait_until_begin_checking_seconds} seconds until we can begin checking')
    time.sleep(how_long_to_wait_until_begin_checking_seconds)

#
# Try and get our slot
#

slottr_instance = slottr.Slottr(desired_slottr_url)

current_time = get_current_time()

while current_time < time_finish_checking:

    try:
        slottr_instance.try_to_get_slot(desired_datetime, desired_signup_info)

        print('Success!')
        sys.exit(0)

    except slottr.HttpException as http_exception:
        print(f'Encountered HTTP exception talking to Slottr: {http_exception.message}')
        sys.exit(1)

    except slottr.PageFormatException as page_format_exception:
        print(f'Slottr page in unexpected format. Unable to proceed. {page_format_exception.message}')
        sys.exit(1)

    except slottr.DesiredDatetimeFullException as desired_datetime_full_exception:
        print(f'Desired datetime is full: {desired_datetime_full_exception.message}')
        sys.exit(1)

    except slottr.DesiredDatetimeDoesNotExistException as desired_datetime_does_not_exist_exception:
        print(f'Desired datetime does not exist yet: {desired_datetime_does_not_exist_exception.message}')
        print(f'Sleeping for {seconds_between_attempts} seconds')
        time.sleep(seconds_between_attempts)

    except Exception as e:
        print(f'Encounted unexpected exception: {e}')
        sys.exit(1)

    current_time = get_current_time()

print(f'Current time is {current_time} which is past our time to finish checking of {time_finish_checking}. Aborting.')