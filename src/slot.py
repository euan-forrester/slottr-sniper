#!/usr/bin/env python3

import requests
from requests.exceptions import HTTPError
import logging
from bs4 import BeautifulSoup
import datetime
import sys
import configparser
import os

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

#
# Now get info from Slottr
#

session = requests.Session()

#
# Step 1: Download the initial list of available slots
#

soup = None

try:
    response = session.get(desired_slottr_url)

    response.raise_for_status()

    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')

except HTTPError as http_err:
    print(f'Encountered HTTP error trying to retrieve initial list of available slots: {http_err}')
    sys.exit(1)

#
# Step 2: Get CSRF token
#

csrf_param = None
csrf_token = None

try:
    csrf_param = soup.find('meta', attrs={'name': 'csrf-param'}).get('content')
    csrf_token = soup.find('meta', attrs={'name': 'csrf-token'}).get('content')

except AttributeError as attr_err:
    print(f'Could not find CSRF info in initial sheet')
    sys.exit(1)

print(f'Found CSRF param name "{csrf_param}" and token "{csrf_token}"')

#
# Step 3: Get the time range for the desired slot
#

time_range = None

desired_date = datetime.datetime(desired_signup_year, desired_signup_month, desired_signup_day, desired_signup_hour)

desired_date_formatted = f'{desired_date: %a, %b %d @ %I:00 %p}'.lstrip().replace(" 0", "  ") # https://stackoverflow.com/questions/9525944/python-datetime-formatting-without-zero-padding

print(f'Trying to find desired date "{desired_date_formatted}"')

try:
    """
    This HTML snippit looks like the following below.
    We're going to find our date, and then move around the tree until we can extract the URL portion that corresponds to this slot

    <div class="slot" id="sheet_">
        <div class="info">
        <div class="what">11AM</div>
        <div class="when">Wed, Dec 30 @ 11:00 AM</div>
    </div>
    <div class="who">
        <a class="signup" href="/sheets/18257847/ranges/17588-1100/entry_results/new">Slot me in</a><br/></div>
    </div>
    """

    desired_date_node = soup.find(text=desired_date_formatted)
    time_range = desired_date_node.parent.parent.parent.find('a').get('href').split('/')[4]

except AttributeError as attr_err:
    print(f'Could not find a signup for date "{desired_date_formatted}"')
    sys.exit(1)

print(f"Found time range: '{time_range}' for our desired date")

#
# Step 4: Make a request to fill the slot
#

post_url = f'{desired_slottr_url}/entries/{time_range}/results'

post_data = {
    csrf_param: csrf_token,
    'result[name]': desired_signup_name,
    'result[emails][]': desired_signup_email,
    'result[phone]': desired_signup_phone,
    'result[notes]': desired_signup_notes
}

try:
    response = session.post(post_url, data=post_data)

    response.raise_for_status()

    response.encoding = 'utf-8'

    print(f'Received HTTP response {response.status_code}')

except HTTPError as http_err:
    print(f'Encountered HTTP error trying to post request for a slot: {http_err}')
    sys.exit(1)

print('Success!')