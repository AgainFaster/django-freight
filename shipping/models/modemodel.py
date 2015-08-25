from datetime import datetime, timedelta
import time
from urllib.error import HTTPError, URLError
from django.db import models
from xml.etree import ElementTree as ET
import logging
from .basemodel import Rate

from decimal import Decimal
import urllib.request
import urllib.parse

from django.template.loader import render_to_string


logger = logging.getLogger('Shipping')


class ModeRateRequest(Rate):
    userid = models.CharField(max_length=255, blank=False, null=False)
    password = models.CharField(max_length=255, blank=False, null=False)
    url = models.URLField()

    class Meta:
        app_label = "shipping"
        verbose_name = "Mode Tritan Settings"
        verbose_name_plural = "Mode Tritan Settings"

    def __init__(self, *args, **kwargs):
        super(ModeRateRequest, self).__init__(*args, **kwargs)

    def get_rate(self, items, origin_location, shipping_quote_destination):
        """
        Returns a ShippingQuote object containing the cost and duration of shipping requested goods.
        """

        address = {
            "city": shipping_quote_destination.city,
            "state": shipping_quote_destination.state,
            "country": 'USA',
            "postal_code": shipping_quote_destination.zip_code,
        }

        pickup_datetime = datetime.now()
        drop_datetime = pickup_datetime + timedelta(2)
        if origin_location.address.country == "US":
            origin_location.address.country = "USA"
        request = render_to_string("post_request.xml",
                                   {
                                       'warehouse': origin_location,
                                       'cart_items': items,
                                       'pickup_date': pickup_datetime.strftime("%m/%d/%Y %H:%M"),
                                       'drop_date': drop_datetime.strftime("%m/%d/%Y %H:%M"),
                                       'drop_location': address
                                   })
        # logger.info(request)

        rates = self._post_request(request)

        return rates

    # posts the XML request to the specified URL
    def _post_request(self, request):

        # print request
        #formulate POST request
        logger.info(request)
        values = {'userid': self.userid,
                  'password': self.password,
                  'request': request}

        data = urllib.parse.urlencode(values)
        request = urllib.request.Request(self.url, data)
        response = ""
        num_tries = 3
        while num_tries:
            try:
                response = urllib.request.urlopen(request, timeout=10)
                break
            except HTTPError as e:
                logger.info(e.code)
                logger.info(e.read)
                return
            except URLError as e:
                logger.info(e.reason)
                num_tries -= 1
                if not num_tries:
                    return
                time.sleep(1)
                logger.info("Retrying shipping estimate")

        response_xml = response.read()
        logger.info("Received Freight Rate Response: ")
        logger.info(response_xml)
        self.rates = self._parse_response(response_xml)
        # print rates
        return self.rates

    def _parse_response(self, raw):
        root = ET.fromstring(raw)
        return_dict = {}
        for pricesheet in root.findall('PriceSheets/PriceSheet'):
            carrier_name = pricesheet.find('CarrierName').text
            scac = pricesheet.find('SCAC').text
            is_selected = bool(pricesheet.get('isSelected') == "true")
            pricesheet_type = pricesheet.get('type')
            service_days = float(pricesheet.find('ServiceDays').text)
            total = Decimal(pricesheet.find('Total').text)
            return_dict.update({scac: {"rate": total,
                                       "is_selected": is_selected,
                                       "service_days": service_days}})
            logger.info("%s\t%s\t%s\t%s\t%.2f\t$%.2f" % (
                pricesheet_type, carrier_name, scac, bool(is_selected == "true"), service_days, float(str(total))))
        return return_dict
