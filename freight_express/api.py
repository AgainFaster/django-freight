from django.conf.urls import url
from django.conf import settings
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from tastypie.utils.urls import trailing_slash
from unidecode import unidecode
from freight_express.models import *
import logging

logger = logging.getLogger()


class RateResource(ModelResource):
    class Meta:
        queryset = Rate.objects.all()
        resource_name = "rate"
        allowed_methods = ['get', 'post']
        if not settings.DEBUG:
            authentication = ApiKeyAuthentication()
            authorization = DjangoAuthorization()
        filtering = {
            'to_zone': ['exact', 'iexact'],
            'from_zone': ['exact', 'iexact'],
        }

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/cost_au%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_cost_au'), name="api_get_cost_au"),
            url(r"^(?P<resource_name>%s)/cost_nz%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_cost_nz'), name="api_get_cost_nz"),
            url(r"^(?P<resource_name>%s)/cost_uk%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_cost_uk'), name="api_get_cost_uk"),
            url(r"^(?P<resource_name>%s)/cost_ca%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_cost_ca'), name="api_get_cost_ca"),
            # deprecated
            url(r"^(?P<resource_name>%s)/cost%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_cost_au'), name="api_get_cost"),
        ]

    def get_cost_au(self, request, **kwargs):
        method = self.method_check(request, allowed=['get', 'post'])
        logger.info("Incoming %s request" % (method,))

        self.is_authenticated(request)
        self.throttle_check(request)

        r = request.GET
        if method == "post":
            r = request.POST

        to_code = r.get('to', None)
        weight = float(r.get('weight', 0.0))
        cubic_factor = float(r.get('cubic_factor', 0.0))
        from_code = r.get('from', '4300')

        logger.info(
            "Request Details: To: %s From: %s Weight: %s Cubic Factor: %s" % (to_code, from_code, weight, cubic_factor))
        # get objects
        # valid Postcodes get filtered on the client side.
        to_postcode = AUPostCode.objects.get(postcode=to_code)
        from_postcode = AUPostCode.objects.get(postcode=from_code)

        tier = to_postcode.surcharge

        rate = Rate.objects.get(to_zone=to_postcode.zone, from_zone=from_postcode.zone)

        logger.info("Pulled Rate %s" % (rate,))

        # do math
        base_cost = max(rate.basic_charge + (rate.rate * max(weight, (cubic_factor * rate.cubic_conv))),
                        rate.min_charge)

        logging.info("Base Rate: $%.2f" % (base_cost,))
        additions = []

        # add a surcharge if the destination postcode asks for one
        if tier:
            additions.append(tier.surcharge)
            logger.info("Adding Surcharge: %s ($%.2f)" % (tier.name, tier.surcharge))

        # get additional fees
        fees = AUFee.objects.filter(enabled=True)
        if fees:
            for fee in fees:
                if fee.percentage:
                    fee___ = base_cost / 100.0 * fee.fee
                    additions.append(fee___)
                    logger.info("Adding Fee: %s (%.2f%%): $%.2f" % (fee.name, fee.fee, fee___))
                else:
                    additions.append(fee.fee)
                    logger.info("Adding Fee: %s: $%.2f" % (fee.name, fee.fee))

        # add everything together
        cost = base_cost + sum(additions)
        object_list = {'cost': cost}

        logger.info("Returning cost: $%.2f" % (cost,))

        # send it back to the response
        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    def get_cost_nz(self, request, **kwargs):
        method = self.method_check(request, allowed=['get', 'post'])
        logger.info("Incoming %s request" % (method,))

        self.is_authenticated(request)
        self.throttle_check(request)

        r = request.GET
        if method == "post":
            r = request.POST

        to_code = r.get('to', None)
        weight = float(r.get('weight', 0.0))
        total_weight = float(r.get('total_weight', 0.0))
        cubic_meters = float(r.get('cubic_meters', 0.0))

        logger.info("Request Details: to_code: %s, weight: %s, total_weight: %s, cubic_meters %s" % (
        to_code, weight, total_weight, cubic_meters))

        locations = NZLocation.objects.filter(postcode=to_code)
        if total_weight <= 5:
            method = 'Courier'

            # This is the original shipping calculation, but has been replaced by flat rate (7.50 and 9.00)
            # courier_rate = NZCourierRate.objects.get(distance_factor=locations[0].distance_factor)
            # cost = weight * (courier_rate.cubic_conversion * cubic_factor) * courier_rate.rate

            # flat rates according to weight
            cost = 7.50 if weight <= 2.5 else 9.00
        else:
            method = 'Freight'
            freight_rates = locations[0].nzfreightrate_set.all()
            minimum_cost = locations[0].distance_factor.minimum_freight_cost
            if freight_rates:
                tonne_rate = freight_rates[0].tonne_rate
                cubic_rate = freight_rates[0].cubic_rate
            else:
                tonne_rate = locations[0].distance_factor.default_freight_tonne_rate
                cubic_rate = locations[0].distance_factor.default_freight_cubic_rate

            cost = max((weight / 1000) * tonne_rate,
                       cubic_meters * cubic_rate,
                       minimum_cost)

        object_list = {'cost': cost,
                       'method': method}

        logger.info("Returning cost: %s, Method: %s" % (cost, method))

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    def get_cost_uk(self, request, **kwargs):
        method = self.method_check(request, allowed=['get', 'post'])
        logger.info("Incoming %s request" % (method,))

        self.is_authenticated(request)
        self.throttle_check(request)

        r = request.GET
        if method == "post":
            r = request.POST

        from_country = r.get('from_country', None)
        to_country = r.get('to_country', None)
        to_region = r.get('to_region', None)

        weight = float(r.get('weight', 0.0))

        logger.info("Request Details: from_country: %s to_country: %s to_region: %s weight: %s" % (
        from_country, to_country, to_region, weight))

        # need to order by to_region first so that null regions (default regions) comes first
        rates = UKRate.objects.filter(max_weight__gte=weight,
                                      from_country_code=from_country,
                                      to_country_code=to_country).order_by('to_region', 'max_weight')

        if to_region:
            region_rates = rates.filter(to_region=to_region)
            if region_rates:
                rates = region_rates

        cost = 1
        label = 'Unknown'
        error_message = None

        if rates:
            rate = rates[0]

            cost = rate.initial_rate + (weight - rate.weight_offset) * rate.weight_multiplier_rate
            label = rate.shipping_provider.name

            if cost < 0:
                error_message = 'Shipping calculation error. Please contact us for a shipping quote.'
        else:
            error_message = 'Please contact us for a shipping quote.'

        object_list = {'cost': cost, 'label': label, 'error_message': error_message}

        logger.info("Returning cost: %s, label: %s, error_message: %s" % (cost, label, error_message))

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    def get_cost_ca(self, request, **kwargs):
        method = self.method_check(request, allowed=['get', 'post'])
        logger.info("Incoming %s request" % (method,))

        self.is_authenticated(request)
        self.throttle_check(request)

        r = request.GET
        if method == "post":
            r = request.POST

        from_province = r.get('from_province', None)
        to_city = r.get('to_city', None)
        to_province = r.get('to_province', None)
        sku_list = [sku.strip() for sku in r.get('sku_list', '').split(',')]

        # there should only ever be one settings record
        try:
            rate_settings = CAFreightSettings.objects.get(from_province=from_province)
        except CAFreightSettings.DoesNotExist:
            logger.error('No Freight Settings found for from_province: %s' % from_province)
            raise

        # add at least 50 for skid, min weight should be 640
        # weight = max(float(r.get('weight', 0.0)) + 50.0, 640.0)
        original_weight = float(r.get('weight', 0.0))
        weight = max(original_weight + rate_settings.skid_weight, rate_settings.minimum_weight)

        logger.info(
            "Request Details:\nfrom_province: %s\nto_province: %s\nto_city: %s\nweight (original): %s\nweight (adjusted): %s\nsku_list: %s" % (
            from_province, to_province, to_city, original_weight, weight, sku_list))

        # get default multiplier
        multiplier = rate_settings.default_multiplier

        for multiplier_record in CAFreightMultiplier.objects.filter(from_province=from_province):
            multiplier_sku_list = [sku.strip() for sku in multiplier_record.sku_list.split(',')]
            for sku in sku_list:
                if sku and sku in multiplier_sku_list:
                    multiplier = max(multiplier, multiplier_record.multiplier)

        # need to order by to_city first so that null to_city (default to_city) comes first
        province_records = CAFreightRate.objects.filter(from_province=from_province,
                                                        to_province=to_province).order_by('to_city')

        city_records = province_records.filter(to_city__iexact=to_city)
        city_decoded_records = province_records.filter(to_city__iexact=unidecode(to_city))

        try:
            if city_records.exists():
                city_rate = city_records[0].rate
            elif city_decoded_records.exists():
                city_rate = city_decoded_records[0].rate
                logger.info('City rate not found for %s, using the one for %s instead.' % (to_city, unidecode(to_city)))
            else:
                city_rate = province_records[0].rate
                logger.info('City rate not found for %s, using default rate for province %s as city rate' % (
                to_city, to_province))
        except:
            logger.error('No Freight Rate found for %s, %s' % (to_city, to_province))
            raise

        logger.info("Applying calculation %s (weight) / 100.0 * %s (city_rate) * %s (multiplier) + %s (surcharge)" % (
        weight, city_rate, multiplier, rate_settings.surcharge))
        cost = weight / 100.0 * city_rate * multiplier + rate_settings.surcharge

        response_dict = {'cost': cost, }
        logger.info("Returning cost: %s" % (cost,))

        self.log_throttled_access(request)
        return self.create_response(request, response_dict)
