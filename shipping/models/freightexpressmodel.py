import logging
from django.db import models
from .basemodel import Rate

from decimal import Decimal

import simplejson
import urllib.request
import urllib.parse

logger = logging.getLogger('Shipping')

NZ_CWL_FREIGHT_ADDITIONAL_COST = Decimal('12.50')


class FreightExpressRateRequest(Rate):

    api_user = models.CharField(max_length=255, blank=False, null=False)
    api_key = models.CharField(max_length=255, blank=False, null=False)
    api_url = models.CharField(max_length=255, blank=False, null=False,
                                help_text="The url for the API call. For example: http://internal.againfaster.com/fe/api/v1/rate/cost_ca/")
    send_sku_list = models.BooleanField(default=False, help_text="True if the API expects a list of SKUs")

    class Meta:
        app_label = "shipping"
        verbose_name = "Freight Express Settings"
        verbose_name_plural = "Freight Express Settings"

    def __init__(self, *args, **kwargs):
        super(FreightExpressRateRequest, self).__init__(*args, **kwargs)

    def _freight_express(self, post_data):

        # CA
        # primary_warehouse = TagWarehouse.objects.filter(tag=cart.tag).order_by('weight')[0].warehouse
        # sku_list = ','.join([item.product.product_sku for item in items])
        #
        # post_data = [
        #     ('to_city', shipping_quote.city.encode('utf-8') if shipping_quote.city else None),
        #     ('to_province', shipping_quote.state),
        #     ('weight', sum([i.get_weight(honor_free_shipping=True) for i in items])),
        #     ('from_province', primary_warehouse.address.state),
        #     ('sku_list', sku_list),
        # ]

        # AU
        # post_data = [
        #     ('to', shipping_quote.zip_code),
        #     ('from', '4300'),
        #     ('weight', cart.get_weight(honor_free_shipping=honor_free_shipping)),
        #     ('cubic_factor', _get_cubic_factor(all_items))
        # ]

        # NZ
        # post_data = [
        #     ('to', shipping_quote.zip_code),
        #     ('weight', weight),
        #     ('total_weight', cart.get_weight()),
        #     ('cubic_meters', _get_cubic_factor(all_items))
        # ]

        # UK
        # post_data = [
        #     ('from_country', from_country),
        #     ('to_country', to_country),
        #     ('to_region', to_region),
        #     ('weight', sum(i.get_weight(honor_free_shipping=True) for i in all_items))
        # ]

        logger.info(str(post_data))
        post_data.append(('format', 'json'))
        post_data.append(('username', self.api_user))
        post_data.append(('api_key', self.api_key))

        # url = 'http://%s/fe/api/v1/rate/cost_%s/' % (self.api_url, country_api.lower())

        encoded_post_data = urllib.parse.urlencode(post_data)
        logger.info("Sending: %s", encoded_post_data)
        logger.info("URL: %s" % (self.api_url,))

        req = urllib.request.Request(self.api_url, (encoded_post_data))
        #base64string = base64.encodestring('%s:%s' % ("againfaster", "af123")).replace('\n', '')
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

    def _get_additional_cost(self, items, origin_address, shipping_quote_destination):

        if shipping_quote_destination.country_code == 'NZ' \
                and self.display_label == 'Freight' \
                and origin_address.name =='CWL':
            return NZ_CWL_FREIGHT_ADDITIONAL_COST

        return Decimal(0)

    def get_rate(self, items, origin_address, shipping_quote_destination):

        cubic_factor = self._get_cubic_factor(items)
        post_data = [
            ('total_weight', items[0].cart.get_weight() if items else 0.0),
            ('weight', sum([i.get_weight() for i in items])),
            ('cubic_factor', cubic_factor),
            ('cubic_meters', cubic_factor),

            ('to', shipping_quote_destination.zip_code),
            ('to_city', shipping_quote_destination.city.encode('utf-8') if shipping_quote_destination.city else None),
            ('to_province', shipping_quote_destination.state),
            ('to_region', shipping_quote_destination.state),
            ('to_country', shipping_quote_destination.country_code),

            ('from', '4300'), # only AU needs this, hardcode for now
            ('from_province', origin_address.address.state),
            ('from_country', origin_address.address.country),
        ]

        if self.send_sku_list:
            post_data.append(('sku_list', ','.join([item.product.product_sku for item in items])))

        response_dict = self._freight_express(post_data)
        # set the custom label if there is one
        self.display_label = response_dict.get('label') or response_dict.get('method') or self.display_label
        additional_cost = self._get_additional_cost(items, origin_address, shipping_quote_destination)

        self.rates = {response_dict.get('carrier', 'FREIGHTEXPRESS'): {'rate': Decimal(str(response_dict.get('cost', 0))) + additional_cost}}

        return self.rates
