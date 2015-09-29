import html
import logging
from django.db import models
import math
from .basemodel import Rate

from usps.api.ratecalculator import DomesticRateCalculator
from usps.errors import USPSXMLError

from decimal import Decimal
from shipping.models.carriermodel import Carrier
from shipping.models.apimodels import ResponseRate

logger = logging.getLogger('Shipping')

class USPSRateRequest(Rate):
    userid = models.CharField(max_length=255, blank=False, null=False)
    password = models.CharField(max_length=255, blank=False, null=False)
    server = models.URLField(blank=False, null=False, default="http://production.shippingapis.com/ShippingAPI.dll")

    class Meta:
        app_label = "shipping"
        verbose_name = "USPS Settings"
        verbose_name_plural = "USPS Settings"

    def __init__(self, *args, **kwargs):
        super(USPSRateRequest, self).__init__(*args, **kwargs)
        # self.USPS_SCAC_LOOKUP_DICT = {
    #     # '0': {'scac': '',
    #     #       'service': 'First-Class Mail&amp;lt;sup&amp;gt;&amp;#174;&amp;lt;/sup&amp;gt; Large Envelope'},
    #     # '0': {'scac': '',
    #     #       'service': 'First-Class Mail&amp;lt;sup&amp;gt;&amp;#174;&amp;lt;/sup&amp;gt; Letter'},
    #     # '0': {'scac': '',
    #     #       'service': 'First-Class Mail&amp;lt;sup&amp;gt;&amp;#174;&amp;lt;/sup&amp;gt; Parcel'},
    #     '0': {'scac': '',
    #           'service': 'First-Class Mail&amp;lt;sup&amp;gt;&amp;#174;&amp;lt;/sup&amp;gt; Postcards'},
    #     '1': {'scac': '',
    #           'service': 'Priority Mail  {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt;'},
    #     '2': {'scac': '',
    #           'service': 'Priority Mail Express  {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Hold For Pickup'},
    #     '3': {'scac': '',
    #           'service': 'Priority Mail Express  {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt;'},
    #     '4': {'scac': '',
    #           'service': 'Standard Post&amp;lt;sup&amp;gt;&amp;#174;&amp;lt;/sup&amp;gt;'},
    #     '6': {'scac': '',
    #           'service': 'Media Mail&amp;lt;sup&amp;gt;&amp;#174;&amp;lt;/sup&amp;gt;'},
    #     '7': {'scac': '',
    #           'service': 'Library Mail'},
    #     '13': {'scac': '',
    #            'service': 'Priority Mail Express  {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Flat Rate Envelope'},
    #     '15': {'scac': '',
    #            'service': 'First-Class Mail&amp;lt;sup&amp;gt;&amp;#174;&amp;lt;/sup&amp;gt; Large Postcards'},
    #     '16': {'scac': '',
    #            'service': 'Priority Mail  {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Flat Rate Envelope'},
    #     '17': {'scac': '',
    #            'service': 'Priority Mail  {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Medium Flat Rate Box'},
    #     '22': {'scac': '',
    #            'service': 'Priority Mail  {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Large Flat Rate Box'},
    #     '23': {'scac': '',
    #            'service': 'Priority Mail Express  {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Sunday/Holiday Delivery'},
    #     '25': {'scac': '',
    #            'service': 'Priority Mail Express {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Sunday/Holiday Delivery Flat Rate Envelope'},
    #     '27': {'scac': '',
    #            'service': 'Priority Mail Express {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Flat Rate Envelope Hold For Pickup'},
    #     '28': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Small Flat Rate Box'},
    #     '29': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Padded Flat Rate Envelope'},
    #     '30': {'scac': '',
    #            'service': 'Priority Mail Express {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Legal Flat Rate Envelope'},
    #     '31': {'scac': '',
    #            'service': 'Priority Mail Express {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Legal Flat Rate Envelope Hold For Pickup'},
    #     '32': {'scac': '',
    #            'service': 'Priority Mail Express {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Sunday/Holiday Delivery Legal Flat Rate Envelope'},
    #     '33': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Hold For Pickup'},
    #     '34': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Large Flat Rate Box Hold For Pickup'},
    #     '35': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Medium Flat Rate Box Hold For Pickup'},
    #     '36': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Small Flat Rate Box Hold For Pickup'},
    #     '37': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Flat Rate Envelope Hold For Pickup'},
    #     '38': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Gift Card Flat Rate Envelope'},
    #     '39': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Gift Card Flat Rate Envelope Hold For Pickup'},
    #     '40': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Window Flat Rate Envelope'},
    #     '41': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Window Flat Rate Envelope Hold For Pickup'},
    #     '42': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Small Flat Rate Envelope'},
    #     '43': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Small Flat Rate Envelope Hold For Pickup'},
    #     '44': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Legal Flat Rate Envelope'},
    #     '45': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Legal Flat Rate Envelope Hold For Pickup'},
    #     '46': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Padded Flat Rate Envelope Hold For Pickup'},
    #     '47': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Regional Rate Box A'},
    #     '48': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Regional Rate Box A Hold For Pickup'},
    #     '49': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Regional Rate Box B'},
    #     '50': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Regional Rate Box B Hold For Pickup'},
    #     '53': {'scac': '',
    #            'service': 'First-Class&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Package Service Hold For Pickup'},
    #     '55': {'scac': '',
    #            'service': 'Priority Mail Express {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Flat Rate Boxes'},
    #     '56': {'scac': '',
    #            'service': 'Priority Mail Express {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Flat Rate Boxes Hold For Pickup'},
    #     '57': {'scac': '',
    #            'service': 'Priority Mail Express {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Sunday/Holiday Delivery Flat Rate Boxes'},
    #     '58': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Regional Rate Box C'},
    #     '59': {'scac': '',
    #            'service': 'Priority Mail {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Regional Rate Box C Hold For Pickup'},
    #     '61': {'scac': '',
    #            'service': 'First-Class&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Package Service'},
    #     '62': {'scac': '',
    #            'service': 'Priority Mail Express {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Padded Flat Rate Envelope'},
    #     '63': {'scac': '',
    #            'service': 'Priority Mail Express {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Padded Flat Rate Envelope Hold For Pickup'},
    #     '64': {'scac': '',
    #            'service': 'Priority Mail Express {0}&amp;lt;sup&amp;gt;&amp;#8482;&amp;lt;/sup&amp;gt; Sunday/Holiday Delivery Padded Flat Rate Envelope'},
    # }

    def get_rate(self, shipment, items, origin, destination, **kwargs):
        self.shipment = shipment
        logger.info("Retrieving USPS Shipping Rate from %s. USPSRateRequestor %s (ID: %s)" % (self.server,
                                                                                              self.nickname,
                                                                                              self.pk))
        connector = DomesticRateCalculator(self.server, self.userid)

        request = self._create_request(items, origin, destination, **kwargs)

        logger.debug(request)

        self.shipment.carrier_request = request

        response = None

        try:
            response = connector.execute(request)
            self.shipment.carrier_response = response
            logger.info("USPS Rate Response")
            logger.info(response)
        except USPSXMLError as e:
            self.shipment.carrier_response = e

        self.shipment.save()
        if response:
            self.rates = self._parse_response(response)
            return self.rates

        return None

    def _create_request(self, items, origin, destination, service="ALL"):
        destination_postal_code = destination.get('postal_code').split('-')[0]
        request = []
        for item in items:
            for box in item.get_boxes():
                box_quantity = box[0]
                box_weight = box[1]
                box_length = box[2]('length')
                box_width = box[2]('width')
                box_height = box[2]('height')
                ir = {'Service': service,
                      'ZipOrigination': origin.get('postal_code'),
                      'ZipDestination': destination_postal_code,
                      'Pounds': "%(pounds)i" % {'pounds': box_weight},
                      'Ounces': "%(ounces)i" % {'ounces': box_weight * 16 % 16}}
                if box_width >= 12 or box_height >= 12 or box_length >= 12:
                    ir['Container'] = 'RECTANGULAR'
                    ir['Size'] = 'LARGE'
                    ir['Width'] = str(box_width)
                    ir['Length'] = str(box_length)
                    ir['Height'] = str(box_height)
                    # if item.product.container == 'NONRECTANGULAR':
                    #     ir['Girth'] = "%.2f" % (math.pi * float(max(box_width, box_height)))
                else:
                    ir['Container'] = None
                    ir['Size'] = 'REGULAR'

                ir['Machinable'] = 'True'
                for i in range(0, box_quantity):
                    request.append(ir)
        return request

    def _parse_response(self, response):
        return_rates = []
        for package in response:
            for postage in package['Postage']:
                classid = postage['CLASSID']
                carrier_code = 'USPM'

                try:
                    carrier = Carrier.objects.get(carrier_code=carrier_code,
                                                  service_code=classid)
                except Carrier.DoesNotExist:
                    logger.info("%s not found in Carrier Dictionary" % "-".join([carrier_code, classid]))
                    carrier = Carrier.objects.create(carrier_code=carrier_code,
                                                     carrier_name=self.display_label,
                                                     service_code_description=html.unescape(postage['MailService']),
                                                     service_code=classid)
                response_rate = ResponseRate.objects.create(shipment=self.shipment,
                                                            carrier=carrier,
                                                            time_in_transit=0,
                                                            rate=Decimal(postage['Rate']))
                response_rate.add_surcharges(self)
                return_rates.append(response_rate)

        return return_rates
