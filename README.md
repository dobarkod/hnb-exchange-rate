hnb-exchange-rate
=================

Downloads the HBN exchange rate for a given date


    from hnbexchange import RateFrame
    r = RateFrame().retrieve()
    r.data.header
    {'application_date': datetime.date(2013, 8, 1),
     'creation_date': datetime.date(2013, 7, 31),
     'items': 13,
     'rate_id': 148}

    r.data.rates[0]
    {'buying_rate': Decimal('5.086255'),
     'currency_code': u'AUD',
     'median_rate': Decimal('5.101560'),
     'selling_rate': Decimal('5.116865'),
     'unit_value': 1}

    r.get_rate('EUR')
    {'buying_rate': Decimal('7.474760'),
     'currency_code': u'EUR',
     'median_rate': Decimal('7.497252'),
     'selling_rate': Decimal('7.519744'),
     'unit_value': 1}
