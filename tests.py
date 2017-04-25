import sys
import unittest
import datetime
from decimal import Decimal
from hnbexchange import RateFrame, HNBExtractor

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


sample_raw_data = """147300720133107201313
036AUD001       5,101517       5,116868       5,132219
124CAD001       5,477994       5,494477      15,510960
203CZK001       0,288837       0,289706       0,290575
208DKK001       1,001785       1,004799       1,007813
348HUF100       2,498361       2,505879       2,513397
392JPY100       5,742983      15,760264       5,777545
578NOK001       0,947629       0,950480       0,953331
752SEK001       0,860322       0,862911       0,865500
756CHF001       6,053503       6,071718       6,089933
826GBP001      10,613150       8,639067       8,664984
840USD001       5,628279       5,645215       5,662151
978EUR001       7,467601       7,490071       7,512541
985PLN001     111,767438       1,772756       1,778074"""


class TestHNBExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = HNBExtractor(sample_raw_data)

    def test_header_data(self):
        header = self.extractor.header
        self.assertEqual(header['rate_id'], 147)
        self.assertEqual(header['creation_date'], datetime.date(2013, 7, 30))
        self.assertEqual(header['application_date'], datetime.date(2013, 7, 31))
        self.assertEqual(header['items'], 13)

    def test_rates_data(self):
        rates = self.extractor.rates
        rate = rates[0]
        self.assertEqual(len(rates), self.extractor.header['items'])
        self.assertEqual(rate['currency_code'], 'AUD')
        self.assertEqual(rate['unit_value'], 1)
        self.assertEqual(rate['buying_rate'], Decimal('5.101517'))
        self.assertEqual(rate['median_rate'], Decimal('5.116868'))
        self.assertEqual(rate['selling_rate'], Decimal('5.132219'))
        self.assertEqual(rates[12]['buying_rate'], Decimal('111.767438'))

    def test_insufficient_data(self):
        data = ""
        self.assertRaises(ValueError, HNBExtractor, data)

    def test_invalid_header_format(self):
        data = """......\n................"""
        self.assertRaises(ValueError, HNBExtractor, data)

    def test_valid_header_but_invalid_rates(self):
        # Generally incorrect rate format.
        data = """147300720133107201313\nxxx123xxx     1       2       3"""
        self.assertRaises(ValueError, HNBExtractor, data)

        # Invalid rate format but valid unit of account format.
        data = (
            '147300720133107201313\r\n036AUD001       5,203531       '
            '5,219189       5,234847\r\n960XDR001                      '
            '8,551284               '
        )
        HNBExtractor(raw_data=data)

        # Valid rate format
        data = (
            '147300720133107201313\r\n036AUD001       5,203531       '
            '5,219189       5,234847'
        )
        HNBExtractor(raw_data=data)

    def test_extract_rate_rate_format(self):
        # Invalid rate format.
        rate_str = '036AUD001       5,203531       5,219189               '
        self.assertRaises(AssertionError, self.extractor._extract_rate, rate_str)

        # Valid rate format.
        rate_str = '036AUD001       5,203531       5,219189       5,234847'
        rate = self.extractor._extract_rate(rate_str)
        expected_rate = {
            'currency_code': 'AUD',
            'unit_value': 1,
            'buying_rate': Decimal('5.203531 '),
            'median_rate': Decimal('5.219189'),
            'selling_rate': Decimal('5.234847')
        }
        self.assertEqual(rate, expected_rate)

    def test_extract_rate_uoa_format(self):
        # Invalid uoa format.
        rate_str = '036AUD001                      5,219189'
        self.assertRaises(AssertionError, self.extractor._extract_rate, rate_str)

        # Valid uoa format.
        rate_str = '036AUD001                      5,219189               '
        rate = self.extractor._extract_rate(rate_str)
        expected_rate = {
            'currency_code': 'AUD',
            'unit_value': 1,
            'buying_rate': Decimal('0.000000'),
            'median_rate': Decimal('5.219189'),
            'selling_rate': Decimal('0.000000')
        }
        self.assertEqual(rate, expected_rate)


class FakeRequest(object):

    def __init__(self, url, **kwargs):
        date = kwargs[
            'data']['_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateOn']

        if date == '30.07.2013.':
            self.ok = True
            self.text = sample_raw_data
            self.headers = {
                'Content-Disposition': (
                    'attachment; filename="DnevnaTecajnaLista_'
                    '30072013-30072013.zip"'
                )
            }
            self.content = (
                'PK\x03\x04\x14\x00\x08\x08\x08\x00\x15\xa9\x98J\x00\x00\x00'
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00(\x00\x00\x00DnevnaTecaj'
                'naLista_30072013-30072013.dat]\x92In\xc2@\x10E\xf7\x96|\x87'
                '\x1c\xc0\x8b\x9a\x87%a\x08\n\x11AAHI\xee\x7f\x90\x14B\xa1'
                '\x0bzc=\xb7_w\x95\xeb\xa3\x18%8\x012\xc3\xed\x892O\xc0\xb6'
                '\xbal\x00\xf0\xe5\xb6t!`\xe5\x86\x98\x189\x90%\xc4\xe7\tI'
                '\xd6\xab\x07O<\xd3a`\x9a\xe8\xf0\x14)%\xe6\xa9N_\xff\x1e\x86'
                '\x07\x0bEdv\xcc\xb0\x86U3\xe3\xd5\x8b\xcd\xa1y\xb8\x000\x1044'
                '\xe0h\x98\xa06OU\xee\xfe\xb2C\xf8\xff\x90\xaa\x12$\xd5\x86'
                '\x11\x88\x03\xc9\xd8\xaa?Nz?\xfd\x0cO\x17\xd7d\x19\r\xb9\x9by'
                '\xc3\x94\xbar\x9e\xd4\xe3\xf8\xf9\xd0_*\x81FCI\xe2\x86\xeeQ'
                '\xff\xc5\x95\xce\xdb\x07/\x1cT\xad!\xa3wTO\xbbz\xb6\xde\xef'
                '\x86g\x0bX\xed\xd0\xc0\x10\x10\xb9#\x02\xd1\xd5\x0b\xb2\xb7'
                '\xd7\xd3\xf0b1\xab+h`\x8d\x0b\xed\x8e\x15\x98\x04(O\xe0r~\x98'
                '\xbbQ\x88\xe8@Q\x8e\xb6kTu\xcfS\x1a|o\xbe\x86\xf7\xb4b\xd1JH'
                '\xc8\xd3\xeb\xf2<\xb6\x97\xe6y\xe5,\x14\xf5\x8e\n\x08\x18\x03'
                '\x89\x95*/\x19z\xfa8\xf6\xbc\xb8Upy\xa0s\xcd\xaca"\xea\x1fPK'
                '\x07\x08\x17\x0f\xa2\x0b,\x01\x00\x00%\x03\x00\x00PK\x01\x02'
                '\x14\x00\x14\x00\x08\x08\x08\x00\x15\xa9\x98J\x17\x0f\xa2'
                '\x0b,\x01\x00\x00%\x03\x00\x00(\x00\x00\x00\x00\x00\x00\x00'
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00DnevnaTecajnaLista_3'
                '0072013-30072013.datPK\x05\x06\x00\x00\x00\x00\x01\x00\x01'
                '\x00V\x00\x00\x00\x82\x01\x00\x00\x00\x00'
            )
            if sys.version_info[0] == 3:
                self.content = bytes(self.content, 'latin1')
        else:
            self.ok = False
            self.text = ""


class TestRateFrame(unittest.TestCase):

    def setUp(self):
        self.ref_date = datetime.date(2013, 7, 30)

    def test_init_date(self):
        rf = RateFrame(self.ref_date)
        self.assertEqual(rf.date, self.ref_date)

        # If no date is specified, date will default to today.
        rf = RateFrame()
        self.assertEqual(rf.date, datetime.date.today())

    def test_retrieve_date_fallback(self):
        # we mock requests.get to test condition when data for requested date is
        # not available (404, r.ok==False). If that happens RateFrame object
        # then iterates backwards throught dates until it successfully
        # retrieves some data (which for this test is faked as 2 days before
        # requested date)

        date = self.ref_date + datetime.timedelta(2)
        rf = RateFrame(date)
        with patch('requests.post', FakeRequest):
            rf.retrieve()
            rates = rf.data.rates
            rate = rates[0]
            self.assertEqual(len(rates), rf.data.header['items'])
            self.assertEqual(rf.date, self.ref_date)
            self.assertEqual(rate['currency_code'], 'AUD')
            self.assertEqual(rate['unit_value'], 1)
            self.assertEqual(rate['buying_rate'], Decimal('5.203531'))

    def test_get_rate(self):
        rf = RateFrame(self.ref_date)
        rf.retrieve()
        rate = rf.get_rate('EUR')
        self.assertEqual(rate['currency_code'], 'EUR')
        self.assertEqual(rate['unit_value'], 1)
        self.assertEqual(rate['buying_rate'], Decimal('7.478515 '))

    @patch('hnbexchange.RateFrame._build_payload')
    def test_wrong_exchange_rate(self, payload):
        date = self.ref_date - datetime.timedelta(1)
        payload.return_value = {
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_pageNum': '',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateFromMin': '',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateToMax': '',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_yearMin': '',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_yearMax': '',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateMaxDatePicker': date.strftime('%d.%m.%Y.'),
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_vrstaReport': '1',
            'year': '-1',
            'yearLast': '-1',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_month': '-1',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateOn': date.strftime('%d.%m.%Y.'),
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateFrom': date.strftime('%d.%m.%Y.'),
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_dateTo': date.strftime('%d.%m.%Y.'),
            '_izborValuta': '1',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_vrstaTecaja': '-1',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_datumVrsta': '2',
            '_tecajnalistacontroller_WAR_hnbtecajnalistaportlet_fileTypeForDownload': 'DAT',
        }

        rf = RateFrame(self.ref_date)
        self.assertRaises(ValueError, rf.retrieve)

if __name__ == '__main__':
    unittest.main()
