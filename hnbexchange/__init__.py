import re
from decimal import Decimal
from datetime import date, timedelta, datetime

import requests

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

RATE_FORMAT = re.compile(
    "\d{3}([A-Z]{3})(\d{3})\s+"
    "([0-9]+,[0-9]+)\s+"
    "([0-9]+,[0-9]+)\s+"
    "([0-9]+,[0-9]+)"
)

class RateFrame(object):
    """Rate Frame holds exchange rate data for single point in time."""

    def __init__(self, date=date.today(), base_url='http://www.hnb.hr/tecajn/'):
        self.date = date
        self.base_url = base_url
        self.data = None

    def full_url(self, date):
        """Return full url to exchange rate .dat file for a given date."""
        filename = 'f' + date.strftime("%d%m%y") + '.dat'
        return urljoin(self.base_url, filename)

    def retrieve(self):
        """Retrieve data for date that the class was initialised with.

        If there is no data for a given date iterate backwards until success.
        Return reference to class instance for chaining."""

        date = self.date
        r = requests.get(self.full_url(date))
        while not r.ok:
            date = date - timedelta(1)
            r = requests.get(self.full_url(date))
        self.date = date
        self.data = HNBExtractor(r.text)
        return self

    def get_rate(self, currency_code):
        """Search data for currency code. Return dict with rate data or None."""
        return next(
            (rate for rate in self.data.rates if rate['currency_code'] == currency_code),
            None
        )


class HNBExtractor(object):
    """HNBExtractor validates and extracts data from raw request data.

    Format of retrieved data: http://www.hnb.hr/tecajn/hopiszap.htm"""

    def __init__(self, raw_data):
        data = raw_data.splitlines()
        if len(data) < 2:
            raise ValueError('Insuficient data')
        self.raw_header = self._validate_header(data[0])
        self.raw_rates = self._validate_rates(data[1:])

    def _validate_header(self, header):
        if not re.match("\d{21}", header):
            raise ValueError('Invalid header format')
        return header

    def _validate_rates(self, rates):
        for rate in rates:
            if not RATE_FORMAT.match(rate):
                raise ValueError('Invalid rate format: ' + str(rate))
        return rates

    @property
    def header(self):
        header = self.raw_header
        creation_date = datetime.strptime(header[3:11], "%d%m%Y").date()
        application_date = datetime.strptime(header[11:19], "%d%m%Y").date()
        return {
            'rate_id': int(header[0:3]),
            'creation_date': creation_date,
            'application_date': application_date,
            'items': int(header[19:21]),
        }

    @property
    def rates(self):
        return [self._extract_rate(rate) for rate in self.raw_rates]

    def _extract_rate(self, line):
        match = RATE_FORMAT.match(line)
        assert match is not None

        values = match.groups()
        return {
            'currency_code': values[0],
            'unit_value': int(values[1]),
            'buying_rate': Decimal(values[2].replace(',', '.')),
            'median_rate': Decimal(values[3].replace(',', '.')),
            'selling_rate': Decimal(values[4].replace(',', '.'))
        }
