# HNB Exchange Rate

Get exchange rate from Croatian National Bank (HNB).

## Quickstart

Install the package from GitHub:

    pip install git+http://github.com/dobarkod/hnb-exchange-rate.git#egg=HNB-Exchange-Rate

Get the current exchange rates:

    >>> from hnbexchange import RateFrame
    >>> r = RateFrame().retrieve()

Note that HNB defines the exchange rate for one day in advance, so the rate
defined today is applicable to tomorrow and onwards (until the new rate
superseeds it).

Get the current exchange rate between Croatian Kuna (HRK) and Euro (EUR):

    >>> rate = r.get_rate('EUR')

Use the rate to convert the values:

    >>> from decimal import Decimal
    >>> amount_hrk = Decimal('42')
    >>> amount_eur = amount_hrk * rate['median_rate'] / rate['unit_value']

Buying rate (`buying_rate`) and selling rate (`selling_rate`) are also
supported.

Getting the exchange rate at some time in the past is also supported:

    >>> from datetime import date, timedelta
    >>> yesterday = date.today() - timedelta(days=1)
    >>> r = RateFrame(yesterday).retrieve()

To get the detailed information about the retrieved rates:

    >>> r.data.header
    {'application_date': datetime.date(2013, 8, 1),
     'creation_date': datetime.date(2013, 7, 31),
     'items': 13,
     'rate_id': 148}

    >>> r.data.rates[0]
    {'buying_rate': Decimal('5.086255'),
     'currency_code': u'AUD',
     'median_rate': Decimal('5.101560'),
     'selling_rate': Decimal('5.116865'),
     'unit_value': 1}

    >>> r.get_rate('EUR')
    {'buying_rate': Decimal('7.474760'),
     'currency_code': u'EUR',
     'median_rate': Decimal('7.497252'),
     'selling_rate': Decimal('7.519744'),
     'unit_value': 1}

## Bug reporting and contributing

We're using GitHub issue tracker for bug reporting. If you found a problem,
please report it at http://github.com/dobarkod/hnb-exchange-rate/issues/ .

If you've fixed a bug or implemented a feature you'd like to see in this
package, awesome! Pull requests are welcome! When submitting a pull request,
please make sure to follow the coding style (PEP8) and provide automated
test for your bugfix or feature implementation.

## Authors and Copyright

Copyright (C) 2013 by Dobar Kod and contributors. See the AUTHORS file
for the list of contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
