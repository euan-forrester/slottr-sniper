#!/usr/bin/env python3

import requests
from requests.exceptions import HTTPError
import logging
from bs4 import BeautifulSoup
import datetime
import sys
from urllib.parse import urlparse

BASE_SHEET_URL = 'https://www.slottr.com/sheets/18257847'

DESIRED_SIGNUP_YEAR = 2020
DESIRED_SIGNUP_MONTH = 12
DESIRED_SIGNUP_DAY = 30
DESIRED_SIGNUP_HOUR = 11
DESIRED_SIGNUP_NAME = 'Euan test from script'
DESIRED_SIGNUP_EMAIL = 'a@b.com'
DESIRED_SIGNUP_PHONE = '1234567890'
DESIRED_SIGNUP_NOTES = 'Made from script! Yay!'

# TODO: Make sure we're not trying to signup more than 48 hours in advance. Is this actually checked?

#
# Step 1: Download the initial list of available slots
#

soup = None

try:
    response = requests.get(BASE_SHEET_URL)

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

desired_date = datetime.datetime(DESIRED_SIGNUP_YEAR, DESIRED_SIGNUP_MONTH, DESIRED_SIGNUP_DAY, DESIRED_SIGNUP_HOUR)

# TODO: Are single-digit month numbers padded with spaces as well?
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
    print(f'Could not find a signup for date {desired_date_formatted}')
    sys.exit(1)

print(f"Found time range: '{time_range}' for our desired date")

#
# Step 4: Make a request to fill the slot
#

post_url = f'{BASE_SHEET_URL}/ranges/{time_range}/entry_results'

parsed_post_url = urlparse(post_url)

post_data = {
    csrf_param: csrf_token,
    'result': {
        'name': DESIRED_SIGNUP_NAME,
        'emails': [ DESIRED_SIGNUP_EMAIL ],
        'phone': DESIRED_SIGNUP_PHONE,
        'notes': DESIRED_SIGNUP_NOTES
    }
}

post_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',    
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
#    'Content-Length': '242',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': parsed_post_url.hostname,
    'Origin': f'origin: {parsed_post_url.scheme}://{parsed_post_url.hostname}',
    'Referer': f'{post_url}/new',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

try:
    response = requests.post(post_url, data=post_data, headers=post_headers)

    response.raise_for_status()

    response.encoding = 'utf-8'

    print(f'Received HTTP response {response.status}')

except HTTPError as http_err:
    print(f'Encountered HTTP error trying to post request for a slot: {http_err}')
    sys.exit(1)

print('Success!')