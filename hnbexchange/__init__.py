import re
from decimal import Decimal
from datetime import date, timedelta, datetime
from cStringIO import StringIO
import zipfile
import requests


RATE_FORMAT = re.compile(
    "\d{3}([A-Z]{3})(\d{3})\s+"
    "([0-9]+,[0-9]+)\s+"
    "([0-9]+,[0-9]+)\s+"
    "([0-9]+,[0-9]+)"
)

UOA_FORMAT = re.compile(
    "\d{3}([A-Z]{3})(\d{3})\s+"
    "([ ])"
    "([0-9]+,[0-9]+)"
    "([ ]{15})"
)


class RateFrame(object):
    """Rate Frame holds exchange rate data for single point in time."""
    BASE_URL = 'http://www.hnb.hr/web/guest/temeljne-funkcije/monetarna-politika/tecajna-lista/tecajna-lista'
    PARAMS = {
        'p_p_cacheability': 'cacheLevelPage',
        'p_p_col_count': '2',
        'p_p_col_id': 'column-2',
        'p_p_id': 'tecajnalistacontroller_WAR_hnbtecajnalistaportlet',
        'p_p_lifecycle': '2',
        'p_p_mode': 'view',
        'p_p_state': 'normal'
    }

    def __init__(self, dt=None):
        if dt is None:
            dt = date.today()

        self.date = dt
        self.data = None

    @staticmethod
    def _build_payload(dt):
        return {
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_pageNum': '',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateFromMin': '',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateToMax': '',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_yearMin': '',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_yearMax': '',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateMaxDatePicker': dt.strftime('%d.%m.%Y.'),
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_vrstaReport': '1',
            'year': '-1',
            'yearLast': '-1',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_month': '-1',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateOn': dt.strftime('%d.%m.%Y.'),
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateFrom': dt.strftime('%d.%m.%Y.'),
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateTo': dt.strftime('%d.%m.%Y.'),
            '_izborValuta': '1',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_vrstaTecaja': '-1',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_datumVrsta': '2',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_fileTypeForDownload': 'DAT',
        }

    def retrieve(self):
        """Retrieve data for date that the class was initialised with.

        If there is no data for a given date iterate backwards until success.
        Return reference to class instance for chaining."""

        while True:
            r = requests.post(self.BASE_URL, params=self.PARAMS,
                data=self._build_payload(self.date))
            if r.ok:
                break
            self.date = self.date - timedelta(1)

        if self.date.strftime('%d%m%Y') not in r.headers.get('Content-Disposition', ''):
            raise ValueError(
                'Did not retrieve the requested exchange rate for this '
                'date: %s.' % self.date.strftime('%d-%m-%Y')
            )

        zf = zipfile.ZipFile(StringIO(r.content))
        text = zf.open(zf.namelist()[0]).read()
        self.data = HNBExtractor(text)
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
            if not RATE_FORMAT.match(rate) and not UOA_FORMAT.match(rate):
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
        if match is None:
            match = UOA_FORMAT.match(line)
        assert match is not None

        values = map(
            lambda x: '0,000000' if x.isspace() else x, list(match.groups()))
        return {
            'currency_code': values[0],
            'unit_value': int(values[1]),
            'buying_rate': Decimal(values[2].replace(',', '.')),
            'median_rate': Decimal(values[3].replace(',', '.')),
            'selling_rate': Decimal(values[4].replace(',', '.'))
        }
