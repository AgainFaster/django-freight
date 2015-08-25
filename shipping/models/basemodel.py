from decimal import Decimal
from django.conf import settings
from django.db import models
import logging
from .carriermodel import Carrier

logger = logging.getLogger('Shipping')

class Rate(models.Model):
    """
    Base class for Rate API's
    """
    nickname = models.CharField(max_length=255, blank=False, null=False,
                                help_text="Human readable name to identify account")
    display_label = models.CharField(max_length=255, blank=False, null=False,
                                help_text="The default label displayed to customer if the API does not dynamically determine it.")
    enabled = models.BooleanField(default=False)
    debug = models.BooleanField(default=False, help_text="Indicates if these settings are for a test server")

    class Meta:
        app_label = "shipping"
        verbose_name_plural = "ALL RATE SETTINGS"  # clarify things a bit in the admin

    def __init__(self, *args, **kwargs):
        super(Rate, self).__init__(*args, **kwargs)
        self.rates = {}

    def get_rate(self, shipment, items, origin_address, shipping_quote_destination):
        raise NotImplementedError("This method must be overwritten in child class.")

    def update_rate(self, carrier, rate):
        self.rates[carrier]['rate'] = rate

    def _lowest_rate_data(self):
        """
        Returns a tuple, e.g.:
        {'FDX': {'rate': 16.0}, 'UPSM': {'rate': 12.0}, 'USPS': {'rate': 14.0}}
        Becomes:
        ('UPSM', {'rate': 12.0})
        """
        enabled_carriers = [carrier.get_carrier_service_code for carrier in Carrier.objects.filter(enabled=True)]
        rate_items = [rate for rate in self.rates.items() if rate[0] in enabled_carriers]

        if not rate_items:
            logger.info('No rates found for enabled carriers. Trying any rate from any carrier.')
            rate_items = self.rates.items()

        return min(rate_items, key=lambda x: x[1].get('rate'))

    @property
    def lowest_rate(self):
        return self._lowest_rate_data()[1].get('rate')

    @property
    def lowest_rate_carrier_code(self):
        return self._lowest_rate_data()[0].split('-')[0]  # split

    @property
    def lowest_rate_service_code(self):
        scac_code = self._lowest_rate_data()[0]
        if '-' in scac_code:
            return scac_code.split('-')[1]
        else:
            return ''

    @property
    def get_surcharges(self):
        total_surcharge = Decimal('0.0')
        for surcharge in self.surcharge_set.filter(active=True):
            if surcharge.percentage:
                surcharge_amount = surcharge.amount * ((self.lowest_rate + total_surcharge) / Decimal('100.0'))
            else:
                surcharge_amount = surcharge.amount
            logger.info("applying surcharge %s (%s)" % (surcharge.description, surcharge_amount))
            total_surcharge += surcharge_amount

        return Decimal(str(total_surcharge))


    def in_range(self, weight, items):
        # at least one rule must pass for this rate to be in range
        for rule in self.rule_set.all():
            in_weight = rule.in_weight(weight)
            in_dimension = rule.in_dimensions(items)
            rule_result = in_weight and in_dimension
            logger.info("Checking rule: %s, %s. In Weight: %s, In Dimensions: %s" % (
            rule.nickname, rule_result, in_weight, in_dimension))
            if rule_result:
                # found a rule that passes
                return True

        # no passing rules found
        return False


class Surcharge(models.Model):
    rate = models.ForeignKey(Rate)
    description = models.CharField(max_length=255, blank=False, null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    percentage = models.BooleanField(verbose_name="Is Percentage", help_text="Apply amount as a percentage", default=False)
    order = models.IntegerField(help_text="Order in which to apply surcharges (0 is applied first, then 1, etc.)", default=0)

    def __str__(self):
        return self.description

    class Meta:
        app_label = "shipping"
        ordering = ['order', 'id']


class Rule(models.Model):
    rate = models.ForeignKey(Rate)

    nickname = models.CharField(max_length=255, blank=True, null=True,
                                help_text="Human readable name to identify rate")

    min_value = models.DecimalField(max_digits=10, decimal_places=2,
                                    help_text="Minimum weight of Cart.", verbose_name='Minimum weight')
    max_value = models.DecimalField(max_digits=10, decimal_places=2,
                                    help_text="Maximum weight of Cart. Set to '0' to denote no max weight.", verbose_name='Maximum weight')

    min_length = models.DecimalField(max_digits=10, decimal_places=2, default="0.0",
                                     help_text="Minimum length of shippable package..")
    max_length = models.DecimalField(max_digits=10, decimal_places=2, default="108.0",
                                     help_text="Maximum length of shippable package. Set to '0' to denote no max length.")
    min_package_size = models.DecimalField(max_digits=10, decimal_places=2, default="0.0",
                                           help_text="Minimum Package Size. Length + Girth (2 x length + 2 x height).")
    max_package_size = models.DecimalField(max_digits=10, decimal_places=2, default="165.0",
                                           help_text="Maximum Package Size. Length + Girth (2 x length + 2 x height). Set to '0' to denote no max package weight.")

    class Meta:
        app_label = "shipping"

    def __unicode__(self):
        return "Rule: %s" % (self.nickname or '(unnamed)')

    def in_weight(self, weight):
        #if no max_value is set, there is no upper limit
        if self.max_value:
            return self.min_value <= weight < self.max_value
        else:
            return self.min_value <= weight


    def in_dimensions(self, items):
        for item in items:
            # determine if the length is less than the max
            # if rule.max_length is 0 (False), there is no max length, so skip
            # the check and keep it True
            in_length = True
            if self.max_length:
                in_length = item.length <= self.max_length

            if self.min_length:
                in_length = in_length and self.min_length < item.length

            # determine if the package size is less than the max
            # if rule.max_length is 0 (False), there is no max length, so skip
            # the check and keep it True
            in_size = True
            package_size = (2 * item.height) + (2 * item.width)

            if self.max_package_size:
                in_size = package_size + item.length <= self.max_package_size

            if self.min_package_size:
                in_size = in_size and self.min_package_size < package_size + item.length

            # if either of these is True, this package, and thus shipment cannot go
            # with this carrier
            if not in_length or not in_size:
                return False
        # if we get here, all items fit and we can ship
        return True
