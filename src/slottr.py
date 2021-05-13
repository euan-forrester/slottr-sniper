import requests
from requests.exceptions import HTTPError
import logging
from bs4 import BeautifulSoup
import datetime
import logging

class SignupInfo:
    def __init__(self, name, email, phone, condo, building, notes):
        self.name = name
        self.email = email
        self.phone = phone
        self.condo = condo
        self.building = building
        self.notes = notes

# Raised when encountering an error communicating with Slottr
class HttpException(Exception):
    def __init__(self, message, http_code):
        self.message = message
        self.http_code = http_code

# Raised when unable to find expected static content within the Slottr page
class PageFormatException(Exception):
    def __init__(self, message):
        self.message = message

# Raised when the specified timeslot does not exist
class DesiredDatetimeDoesNotExistException(Exception):
    def __init__(self, message):
        self.message = message

# Raised when the specified timeslot has been filled by someone
class DesiredDatetimeFullException(Exception):
    def __init__(self, message):
        self.message = message

class Slottr:

    def __init__(self, sheet_url, post_url_type):
        self.sheet_url = sheet_url
        self.post_url_type = post_url_type

    def _get_sheet(self, session):

        soup = None

        try:
            response = session.get(self.sheet_url)

            response.raise_for_status()

            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

        except HTTPError as http_err:
            raise HttpException(f'Encountered HTTP error trying to retrieve initial list of available slots: {http_err}', response.status_code) from http_err

        return soup

    def get_sheet_name(self):

        session = requests.Session()

        soup = self._get_sheet(session)

        sheet_name = None

        try:
            sheet_name = soup.find('h1').string

        except AttributeError as attr_err:
            raise PageFormatException('Could not find title in initial sheet') from attr_err

        return sheet_name

    def try_to_get_slot(self, desired_datetime, signup_info):

        session = requests.Session()

        #
        # Step 1: Download the initial list of available slots
        #

        soup = self._get_sheet(session)

        #
        # Step 2: Get CSRF token
        #

        csrf_param = None
        csrf_token = None

        try:
            csrf_param = soup.find('meta', attrs={'name': 'csrf-param'}).get('content')
            csrf_token = soup.find('meta', attrs={'name': 'csrf-token'}).get('content')

        except AttributeError as attr_err:
            raise PageFormatException('Could not find CSRF info in initial sheet') from attr_err

        logging.debug(f'Found CSRF param name "{csrf_param}" and token "{csrf_token}"')

        #
        # Step 3: Get the time range for the desired slot
        #

        time_range = None

        desired_datetime_formatted = f'{desired_datetime: %a, %b %d @ %I:00 %p}'.lstrip().replace(" 0", "  ") # The hour needs to be padded with a space (e.g. " 9:00" and not "09:00"). https://stackoverflow.com/questions/9525944/python-datetime-formatting-without-zero-padding

        logging.debug(f'Trying to find desired date "{desired_datetime_formatted}"')

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

        desired_date_node = soup.find(text=desired_datetime_formatted)

        if desired_date_node is None:
            raise DesiredDatetimeDoesNotExistException(f'Could not find an entry for date "{desired_datetime_formatted}". It might not be released yet.')

        try:
            time_range = desired_date_node.parent.parent.parent.find('a').get('href').split('/')[4]

        except AttributeError as attr_err:
            raise DesiredDatetimeFullException(f'Could not find a signup link for date "{desired_datetime_formatted}". It must be full already.') from attr_err

        logging.debug(f"Found time range: '{time_range}' for our desired date")

        #
        # Step 4: Make a request to fill the slot
        #

        # No idea why some Slottr sheets have a POST url in one format or the other, but some have one and some have the other
        if self.post_url_type == 1:
            post_url = f'{self.sheet_url}/entries/{time_range}/results'
        elif self.post_url_type == 2:
            post_url = f'{self.sheet_url}/ranges/{time_range}/entry_results'

        post_data = {
            csrf_param: csrf_token,
            'result[name]': signup_info.name,
            'result[emails][]': signup_info.email,
            'result[phone]': signup_info.phone,
            'result[questions][117]': signup_info.condo,
            'result[questions][122]': signup_info.building,
            'result[notes]': signup_info.notes
        }

        try:
            response = session.post(post_url, data=post_data)

            response.raise_for_status()

            response.encoding = 'utf-8'

            logging.debug(f'Received HTTP response {response.status_code}')

        except HTTPError as http_err:
            raise HttpException(f'Encountered HTTP error trying to post request for a slot: {http_err}', response.status_code) from http_err
