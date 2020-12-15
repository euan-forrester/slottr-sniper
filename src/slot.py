#!/usr/bin/env python3

import requests
from requests.exceptions import HTTPError
import logging
from bs4 import BeautifulSoup

BASE_SHEET_URL = 'https://www.slottr.com/sheets/18257847'

# Step 1: Get CSRF token

csrf_param = None
csrf_token = None

try:
    response = requests.get(BASE_SHEET_URL)

    response.raise_for_status()

    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')

    csrf_param = soup.find('meta', attrs={'name': 'csrf-param'}).get('content')
    csrf_token = soup.find('meta', attrs={'name': 'csrf-token'}).get('content')

except HTTPError as http_err:
    print(f'Encountered HTTP error: {http_err}')

except AttributeError as attr_err:
    print(f'Could not find CSRF info in initial sheet')

print(f'Found csrf param name "{csrf_param}" and token "{csrf_token}"')