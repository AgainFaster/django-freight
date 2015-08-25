import logging
from .basemodel import Rate

from decimal import Decimal

import simplejson
import urllib.request
import urllib.parse

logger = logging.getLogger('Shipping')

class AustraliaPostRateRequest(Rate):

    class Meta:
        app_label = "shipping"
        verbose_name = "Australia Post Settings"
        verbose_name_plural = "Australia Post Settings"

    def __init__(self, *args, **kwargs):
        super(AustraliaPostRateRequest, self).__init__(*args, **kwargs)

    def _freight_express(self, post_data):

        logger.info(str(post_data))
        post_data.append(('format', 'json'))
        post_data.append(('username', self.api_user))
        post_data.append(('api_key', self.api_key))

        encoded_post_data = urllib.parse.urlencode(post_data)
        logger.info("Sending: %s", encoded_post_data)
        logger.info("URL: %s" % (self.api_url,))

        req = urllib.request.Request(self.api_url, (encoded_post_data))
        #base64string = base64.encodestring('%s:%s' % ("username", "password")).replace('\n', '')
        #req.add_header("Authorization", "Basic %s" % base64string)
        response = urllib.request.urlopen(req)
        content = response.read()

        dict = simplejson.loads(content)

        logger.info("Return: %s" % (dict,))

        return dict


    def _get_cubic_factor(self, items):
        sums = []
        for i in items:
            prod = i.product

            height = prod.height * 0.01
            length = prod.length * 0.01
            width = prod.width * 0.01

            factor = height * length * width

            logger.info(
                "%s: Height: %s, Length: %s, Width: %s: Cubic Factor: %s" % (i.product, height, length, width, factor))

            # figure out the number of boxes
            number_of_boxes = sum(box[0] for box in i.number_of_boxes())
            logger.info("Shipping %s items in %s boxes." % (i.quantity, number_of_boxes))
            sums.append(factor * number_of_boxes)
        cubic_factor = sum(sums)
        logger.info("Sum of all cubic factors: %s" % (cubic_factor,))
        return cubic_factor


    def get_rate(self, items, origin_address, shipping_quote_destination):

        weight = sum([i.get_weight() for i in items])

        if float(weight) < 0.5:
            rate = Decimal(7)
        elif float(weight) < 3:
            rate = Decimal(11)
        else:
            rate = Decimal(14)

        self.rates = {'AUP-XXX': {'rate': rate}}
        return self.rates
