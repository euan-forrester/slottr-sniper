#!/usr/bin/env python3

import datetime
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

desired_signup_year = config.getint(environment, 'desired-year')
desired_signup_month = config.getint(environment, 'desired-month')
desired_signup_day = config.getint(environment, 'desired-day')
desired_signup_hour = config.getint(environment, 'desired-hour')

desired_datetime = datetime.datetime(desired_signup_year, desired_signup_month, desired_signup_day, desired_signup_hour)

desired_signup_info = slottr.SignupInfo(desired_signup_name, desired_signup_email, desired_signup_phone, desired_signup_condo, desired_signup_building, desired_signup_notes)

#
# Try and get our slot
#

slottr_instance = slottr.Slottr(desired_slottr_url)

try:
    slottr_instance.try_to_get_slot(desired_datetime, desired_signup_info)

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

except Exception as e:
    print(f'Encounted unexpected exception: {e}')
    sys.exit(1)

print('Success!')