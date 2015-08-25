from datetime import date
import logging
import urllib.request
import re
from django.db import models
from .basemodel import Rate

from xml.etree.ElementTree import fromstring

from decimal import Decimal

from django.template import loader, Context

from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger('Shipping')


class CanadaPostRateRequest(Rate):
    server = models.URLField(blank=False, null=False, default="http://sellonline.canadapost.ca:30000")
    cpcid = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        app_label = "shipping"
        verbose_name = "Canada Post Settings"
        verbose_name_plural = "Canada Post Settings"

    def __init__(self, *args, **kwargs):
        super(CanadaPostRateRequest, self).__init__(*args, **kwargs)
        self.CANADAPOST_SHIPPING_CHOICES = (
            ('1010', 'Domestic - Regular'),
            ('1020', 'Domestic - Expedited'),
            ('1030', 'Domestic - Xpresspost'),
            ('1040', 'Domestic - Priority Courier'),
            ('2005', 'US - Small Packets Surface'),
            ('2015', 'US - Small Packets Air'),
            ('2020', 'US - Expedited US Business Contract'),
            ('2025', 'US - Expedited US Commercial'),
            ('2030', 'US - Xpress USA'),
            ('2040', 'US - Priority Worldwide USA'),
            ('2050', 'US - Priority Worldwide PAK USA'),
            ('3005', 'Int`l - Small Packets Surface'),
            ('3010', 'Int`l - Surface International'),
            ('3015', 'Int`l - Small Packets Air'),
            ('3020', 'Int`l - Air International'),
            ('3025', 'Int`l - Xpresspost International'),
            ('3040', 'Int`l - Priority Worldwide INTL'),
            ('3050', 'Int`l - Priority Worldwide PAK INTL')
        )

    def _process_request(self, connection, request):
        '''
          Post the data and return the XML response
        '''
        f = urllib.request.urlopen(url=connection, data=request.encode("utf-8"))
        all_results = f.read()
        self.raw = all_results
        logger.info(all_results)
        return fromstring(all_results)

    def get_rate(self, items, origin_location, shipping_quote_destination, **kwargs):


        logger.info("Starting Canada Post calculations")

        self.delivery_days = _('3 - 4')  # Default setting for ground delivery
        self.packaging = ''
        self.is_valid = False
        self.charges = 0

        self.service_type = self.CANADAPOST_SHIPPING_CHOICES[0]
        self.service_type_code = self.service_type[0]
        self.service_type_text = self.service_type[1]

        total_price = sum([i.get_display_pricetag * i.quantity for i in items.all()])

        address = {
            "city": shipping_quote_destination.city,
            "state": shipping_quote_destination.state,
            "country": shipping_quote_destination.country_code,
            "postal_code": shipping_quote_destination.zip_code,
        }

        c = Context({
            'cpcid': self.cpcid,
            'items': items,
            # hardcode this for the time being
            'turn_around_time': "24",
            'warehouse': origin_location,
            'drop_location': address,
            'total_price': float(total_price),
        })

        t = loader.get_template('canadapost_request.xml')
        request = t.render(c)
        logger.info(request)
        self.is_valid = False

        tree = self._process_request(self.server, request)

        try:
            status_code = tree.getiterator('statusCode')
            status_val = status_code[0].text
            logger.info("Canada Post Status Code for cart #%s = %s", int(2), status_val)
        except AttributeError:
            status_val = "-1"

        if status_val == '1':
            self.is_valid = False
            self._calculated = False
            all_rates = tree.getiterator('product')

            for rate in all_rates:
                logger.info("Got product id from cp: %s", rate.attrib['id'])
                if self.service_type_code == rate.attrib['id']:
                    self.charges = Decimal(rate.find('.//rate').text)
                    # YYYY-MM-DD
                    delivery_date = rate.find('.//deliveryDate').text
                    shipping_date = rate.find('.//shippingDate').text
                    #check if deliveryDate is date or message
                    datePattern = re.compile(r'\d{4}-\d{2}-\d{2}')
                    isDate = datePattern.match(delivery_date)
                    if isDate:
                        self.delivery_days = date(
                            int(delivery_date[:4]),
                            int(delivery_date[5:7]),
                            int(delivery_date[8:])) - \
                                             date(
                                                 int(shipping_date[:4]),
                                                 int(shipping_date[5:7]),
                                                 int(shipping_date[8:]))
                        self.delivery_days = self.delivery_days.days
                    else:
                        self.delivery_days = delivery_date
                    self.is_valid = True
                    self._calculated = True

            if not self.is_valid:
                logger.info("Canada Post Cannot find rate for code: %s [%s]", self.service_type_code,
                            self.service_type_text)
        else:
            raise CanadaPostSucksException("Canada Post returned an invalid status code: %s", status_val)

        return Decimal(self.charges)


class CanadaPostSucksException(Exception):
    def __init__(self, error_code, value):
        self.value = value
        self.error_code = error_code

    def __unicode__(self):
        return "Canada Post is literally the worst: (%s) %s" % (self.error_code, repr(self.value))

    def __str__(self):
        return self.__unicode__()