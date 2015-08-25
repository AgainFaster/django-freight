import json
import logging
from django.db.models import Q
# from pyshipping.binpack import binpack
# from pyshipping.package import Package
from shipping.exceptions import ShippingException
from shipping.models import FedExRateRequest, UPSRateRequest, USPSRateRequest, ModeRateRequest, CanadaPostRateRequest, \
    FreightExpressRateRequest, AustraliaPostRateRequest
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger('Shipping')


def get_full_shipping_cost(cart, return_quote=False, items=None):
    if not items:
        items = cart.items.all()
    # split AgainFasterProducts and EvolveSubscriptions g
    afp_items = items.filter(product__againfasterproduct__isnull=False)
    evolve_items = items.filter(product__in=EvolveSubscription.objects.all())
    # Only get shipping on AgainFasterProducts
    temp_shipping_quote = _get_rates(afp_items,
                                     cart.shipping_quote,
                                     all_evolve=bool(not afp_items and evolve_items),
                                     full=True,
                                     commit=False)
    if return_quote:
        return temp_shipping_quote
    return temp_shipping_quote.get_selected_shipping()


def get_shipping_rates(shipment, destination):
    logger.info("Requesting new Shipping Rate (%s, %s)" % (shipment.id, destination.get('postal_code'),))
    _get_rates(shipment, destination)
    return True, "", {}


def _get_shipping_rate_requestors(debug=settings.DEBUG):
    # pull all request objects one by one
    args = {
        'enabled': True,
        'debug': debug
    }
    rate_requestors = [FedExRateRequest,
                       FreightExpressRateRequest,
                       AustraliaPostRateRequest,
                       CanadaPostRateRequest,
                       UPSRateRequest,
                       USPSRateRequest,
                       ModeRateRequest]
    rate_objects = []

    for rate_type in rate_requestors:
        applicable_rate_objects = rate_type.objects.filter(**args).filter()

        if applicable_rate_objects:
            rate_objects.append(applicable_rate_objects)

    if not rate_objects:
        raise ShippingException("No Rate Requestors Enabled for Debug: %s" % (debug))

    return rate_objects


def _get_choices(locations, default_carrier_code=None, default_service_code=None):
    primary_warehouse_pk = TagWarehouse.objects.all().order_by('weight')[0].warehouse.pk  # hardcode for now

    shipping_methods_counts = {}
    free_count = 0

    for location_pk, rates_dict in locations.items():
        # determine the number of locations for each shipping method
        if rates_dict.get('Free'):
            free_count += 1
        else:
            for method in rates_dict:
                shipping_methods_counts[method] = shipping_methods_counts.get(method, 0) + 1

    available_shipping_methods = []
    for method, count in shipping_methods_counts.items():
        # in order for a shipping method to be an available choice, it must be available at all the non-free locations
        if count + free_count == len(locations):
            available_shipping_methods.append(method)

    choices = {}  # shipping_methods

    for location_pk, rates_dict in locations.items():

        for rate_label, rate_values in rates_dict.items():
            if not rate_label in available_shipping_methods:
                continue

            choices[rate_label] = choices.get(rate_label, {'value': Decimal(0), 'label': rate_label})
            choices[rate_label]['value'] += rate_values['lowest_rate']

            if location_pk == primary_warehouse_pk:
                choices[rate_label]['carrier_code'] = rate_values.get('lowest_rate_carrier_code')
                choices[rate_label]['service_code'] = rate_values.get('lowest_rate_service_code')

    combo_cost = Decimal(0)
    combo_shippers = set()
    combo_carrier = ''
    combo_service = ''

    if len(locations) > 1 and len(shipping_methods_counts) > 1:
        # Try to see if we can provide a combo shipping rate
        for location_pk, rates_dict in locations.items():
            if not rates_dict or rates_dict.get('Free'):
                continue

            # find the lowest lowest_rate for this location
            lowest_rate_method, lowest_rate_dict = min(rates_dict.iteritems(), key=lambda x: x[1]['lowest_rate'])

            combo_shippers.add(lowest_rate_method)
            combo_cost += lowest_rate_dict.get('lowest_rate')

            if location_pk == primary_warehouse_pk:
                combo_carrier = lowest_rate_dict.get('lowest_rate_carrier_code')
                combo_service = lowest_rate_dict.get('lowest_rate_service_code')

                # get lowest rate and add to combo cost

    if len(combo_shippers) > 1:
        # there are multiple shippers, add the combo shipping option
        choices['Combo'] = {'value': combo_cost, 'label': 'Multiple Shippers',
                            'carrier_code': combo_carrier, 'service_code': combo_service}

    lowest_total_rate_method = None
    if choices:
        # find the lowest 'non-free' total rate
        lowest_total_rate_method = min(choices.iteritems(), key=lambda x: x[1]['value'])[0]
        if not default_carrier_code:
            default_carrier_code = choices[lowest_total_rate_method].get('carrier_code')
            default_service_code = choices[lowest_total_rate_method].get('service_code')

    choices.update(get_initial_shipping_methods())
    if default_carrier_code:
        # set any missing carrier codes to the default
        for choice, choice_dict in choices.items():
            if not choice_dict.get('carrier_code'):
                choice_dict['carrier_code'] = default_carrier_code
                choice_dict['service_code'] = default_service_code

    return lowest_total_rate_method, choices


def _get_rates(shipment, destination, all_evolve=False, full=False):
    if getattr(settings, "LOCATION", "US") == 'US':
        eligible_free_shipping_destination = destination.get('state') and destination.get('state') not in ["HI", "AK",
                                                                                                           "GU"]
        logger.info("Continental: %s (%s) " % (eligible_free_shipping_destination, destination.get('state')))
    else:
        eligible_free_shipping_destination = True

    free_items = shipment.items.filter(ships_free=True)

    logger.info("Free Shipping Items: %s", free_items)

    cutoff_enabled = False
    subsidized = False
    flat_cart_cost = 0
    ships_for_free = False

    default_carrier_code = None
    default_service_code = None

    if eligible_free_shipping_destination:
        if len(shipment.items.all()) == len(free_items):
            ships_for_free = True
        elif getattr(settings, "LOCATION", "US") in ('US', 'CA'):
            cutoff_enabled = getattr(settings, "US_SHIPPING_ENABLE_CUTOFF", False)
            cutoff = Decimal(str(getattr(settings, "US_SHIPPING_CUTOFF", 0)))
            flat_cart_cost = Decimal(str(getattr(settings, "US_SHIPPING_CUTOFF_COST", 0)))

            paid_weight = sum([i.get_weight()
                               for i in shipment.items.exclude(ships_free=True)])
            logger.info("Weight to be paid for: %s", paid_weight)

            meets_low_weight_free_criteria = len(free_items) and paid_weight <= Decimal('3.0')
            subsidized = (cutoff_enabled and paid_weight <= cutoff)

            ships_for_free = meets_low_weight_free_criteria or (subsidized and flat_cart_cost == 0)

    # this needs to be done after the carrier_rate has been retrieved.
    # if not full and ships_for_free:
    #     logger.info("This cart ships for free (subsidized: %(sub)s)" % {'sub': subsidized})
    #
    # elif not full and subsidized and flat_cart_cost:
    #     logger.info("This cart is subsidized and ships for $%s", flat_cart_cost)
    #
    #     for location_pk, rates_dict in locations.items():
    #         locations[location_pk] = {'USPS': {'lowest_rate': flat_cart_cost}}
    #
    #     if primary_warehouse_pk in locations:
    #         default_carrier_code = 'USPM'
    #         default_service_code = 'PFRB'

    at_least_one_rate_returned = False
    # get the warehouse object
    shipping_rate_requestors = _get_shipping_rate_requestors()
    # get all the items originating from this location
    all_items_at_location = shipment.items.all()

    # only split off free_shipping items if we're shipping to the continental US
    # grab items that require payment
    if eligible_free_shipping_destination and not full:
        # filter
        rateable_items = all_items_at_location.exclude(ships_free=True).exclude(
            flat_rate__gt=0)
        flat_rate_items = all_items_at_location.exclude(ships_free=True).filter(
            flat_rate__gt=0)
    else:
        rateable_items = all_items_at_location
        flat_rate_items = []

    rateable_weight = sum([i.get_weight() for i in rateable_items])
    flat_rate_weight = sum([i.get_weight() for i in flat_rate_items])

    all_items_weight = sum([i.get_weight() for i in all_items_at_location])

    # if the order includes an item that ships for free, and the remainder of the order is
    # less than 3 pounds, ship the whole thing for free.

    logger.info("Shipping from location: %s" % (shipment.warehouse))

    logger.info("All Items: %s" % (all_items_at_location,))
    logger.info("Weight of all items: %s" % (all_items_weight,))
    logger.info("Ratable Items: %s" % (rateable_items,))
    logger.info("Weight of ratable items: %s" % (rateable_weight,))
    logger.info("Flat Rate Shipping Items: %s" % (flat_rate_items,))
    logger.info("Weight of Flat Rate Shipping Items: %s" % (flat_rate_weight,))

    subsidy = Decimal('0')
    if cutoff_enabled:
        subsidized_weight = min(rateable_weight,
                                Decimal(str(getattr(settings, "US_SHIPPING_SUBSIDY_CUTOFF", 99999999))))
        subsidy = subsidized_weight * Decimal(str(getattr(settings, "US_SHIPPING_SUBSIDY_PER_POUND", 0))) if \
            rateable_weight >= Decimal(
                str(getattr(settings, "US_SHIPPING_SUBSIDY_LIMIT", 99999999))) else Decimal("0")
        subsidy = Decimal(str(subsidy))

    items_to_rate = rateable_items if rateable_items else flat_rate_items

    # bin stuff here
    # logger.info("Start bin stuff")
    # packages = []
    # for item in items_to_rate:
    #     packages += [Package("%dx%dx%d" % (item.product.get_height(), item.product.get_width(), item.product.get_length()))] * sum([x[0] for x in item.number_of_boxes()])
    # bins = binpack(packages, bin=Package("70x80x119"))
    #
    # logger.info(bins)
    # logger.info("End bin stuff")

    if not items_to_rate:
        # locations[location_pk]['Free'] = True
        at_least_one_rate_returned = True

        # if primary_warehouse_pk == location_pk:
        #     temp_shipping_quote = get_full_shipping_cost(cart, return_quote=True, items=all_items_at_location)
        #     default_carrier_code = temp_shipping_quote.get_selected_carrier_code
        #     default_service_code = temp_shipping_quote.get_selected_service_code
    else:

        # the meat and potatoes
        # where the donuts get made
        # where the bacon is slung
        # where we don't want any of that salami!

        flat_cost = sum([item.flat_rate * item.quantity for item in flat_rate_items])

        for rate_requestor in shipping_rate_requestors:
            for rate_object in rate_requestor:
                if rate_object.in_range(rateable_weight + flat_rate_weight, items_to_rate):
                    # try:
                    return_rates = rate_object.get_rate(shipment,
                                                        items_to_rate,
                                                        json.loads(shipment.origin),
                                                        destination)
                    # except Exception as e:
                    #     logger.error('%s, Exception Type: %s, Exception: %s' % (type(rate_object), type(e), e),
                    #                  extra={})
                    #
                    #     continue

                    # total_rate = flat_cost + subsidy
                    #
                    # if rateable_items:
                    #     total_rate += rate_object.lowest_rate + rate_object.get_surcharges
                    #
                    at_least_one_rate_returned = True

    if not at_least_one_rate_returned:
        raise ShippingException("No rates returned for location!", {'location': shipment.warehouse})

    return {}