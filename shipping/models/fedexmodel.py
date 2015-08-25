import json
import logging
from django.db import models
import itertools
from .basemodel import Rate

from decimal import Decimal

from django.conf import settings

from fedex.config import FedexConfig
from fedex.services.rate_service import FedexRateServiceRequest
from fedex.base_service import FedexError
from shipping.models.carriermodel import Carrier
from shipping.models.apimodels import ResponseRate

logger = logging.getLogger('Shipping')

HUBIDS = [
    ("5185", "ALPA Allentown"),
    ("5303", "ATGA Atlanta"),
    ("5281", "CHNC Charlotte"),
    ("5602", "CIIL Chicago"),
    ("5929", "COCA Chino"),
    ("5751", "DLTX Dallas"),
    ("5802", "DNCO Denver"),
    ("5481", "DTMI Detroit"),
    ("5087", "EDNJ Edison"),
    ("5431", "GCOH Grove City"),
    ("5771", "HOTX Houston"),
    ("5465", "ININ Indianapolis"),
    ("5648", "KCKS Kansas City"),
    ("5902", "LACA Los Angeles"),
    ("5254", "MAWV Martinsburg"),
    ("5379", "METN Memphis"),
    ("5552", "MPMN Minneapolis"),
    ("5531", "NBWI New Berlin"),
    ("5110", "NENY Newburgh"),
    ("5015", "NOMA Northborough"),
    ("5327", "ORFL Orlando"),
    ("5194", "PHPA Philadelphia"),
    ("5854", "PHAZ Phoenix"),
    ("5150", "PTPA Pittsburgh"),
    ("5958", "SACA Sacramento"),
    ("5843", "SCUT Salt Lake City"),
    ("5983", "SEWA Seattle"),
    ("5631", "STMO St. Louis"),
]


class FedExRateRequest(Rate):
    auth_key = models.CharField(verbose_name="Authentication Key", max_length=255, blank=False, null=False)
    password = models.CharField(verbose_name="API Password", max_length=255, blank=False, null=False)
    account_number = models.CharField(verbose_name="FedEx Account Number", max_length=255, blank=False, null=False)
    billing_contact_and_address = models.TextField()
    meter_number = models.CharField(verbose_name="Meter Number", max_length=255, blank=False, null=False)
    smart_post_hub_id = models.CharField(verbose_name="FedEx SmartPost HubID", max_length=4, blank=True, null=True,
                                         choices=HUBIDS)
    smart_post_enable = models.BooleanField(verbose_name="Enable FedEx SmartPost", default=False)
    smart_post_cutoff = models.IntegerField(verbose_name="FedEx SmartPost Cutoff",
                                            help_text="Only request FedEx SmartPost rates when cart total weighs less than this amount",
                                            default=9)
    lbs_per_pallet = models.IntegerField(verbose_name="LBS to ship per pallet",
                                         default=1500)

    class Meta:
        app_label = "shipping"
        verbose_name = "FedEx Settings"
        verbose_name_plural = "FedEx Settings"

    def __init__(self, *args, **kwargs):
        super(FedExRateRequest, self).__init__(*args, **kwargs)
        self.FEDEX__SCAC_LOOKUP_DICT = {
            "FIRST_OVERNIGHT": "FDX-NGT",  # VERIFY
            "PRIORITY_OVERNIGHT": "FDX-PRT",
            "STANDARD_OVERNIGHT": "FDX-STD",
            "FEDEX_2_DAY_AM": "FDX-2AM",  # VERIFY
            "FEDEX_2_DAY": "FDX-ECO",
            "FEDEX_EXPRESS_SAVER": "FDX-XSV",
            "FEDEX_GROUND": "FDX-GND",
            "FEDEX_1_DAY_FREIGHT": "FDX-1DY",
            "SMART_POST": "FDX-95",
            "GROUND_HOME_DELIVERY": "FDX-HOM",
            "FEDEX_FREIGHT_ECONOMY": "FXNL",
            "FEDEX_FREIGHT_PRIORITY": "FXFE"
        }
        self.contact = json.loads(self.billing_contact_and_address)
        self.rates = []

    def _create_config(self):
        self.CONFIG_OBJ = FedexConfig(key=str(self.auth_key),
                                      password=str(self.password),
                                      account_number=str(self.account_number),
                                      meter_number=str(self.meter_number),
                                      use_test_server=False  # self.debug,
                                      )

        return self.CONFIG_OBJ

    def get_rate(self, shipment, items, origin_address, destination):
        self.shipment = shipment
        logging.basicConfig(level=logging.INFO)
        logger.info("using %s" % self.nickname)

        smart_post_count = 0
        rateable_weight = sum([item.get_weight() for item in items])
        smart_post = self.smart_post_enable and rateable_weight <= (self.smart_post_cutoff or 70)
        logger.info("FedEx SmartPost: %s" % smart_post)
        logger.info("SmartPost cutoff: %s, Rateable Weight: %s" % (self.smart_post_cutoff, rateable_weight))

        config = self._create_config()
        rate_request = FedexRateServiceRequest(config)

        rate_request.RequestedShipment.RateRequestTypes = 'NONE'
        rate_request.RequestedShipment.DropoffType = 'REGULAR_PICKUP'
        rate_request.RequestedShipment.ServiceType = None
        if rateable_weight > 150:
            rate_request.RequestedShipment.FreightShipmentDetail.TotalHandlingUnits = 0
            rate_request.RequestedShipment.FreightShipmentDetail.FedExFreightAccountNumber = self.account_number
            rate_request.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Contact.PersonName = self.contact.get(
                'PersonName')
            rate_request.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Contact.CompanyName = self.contact.get(
                'CompanyName')
            rate_request.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Contact.PhoneNumber = self.contact.get(
                'PhoneNumber')
            rate_request.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Address.StreetLines = self.contact.get(
                'StreetLines')
            rate_request.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Address.City = self.contact.get(
                'City')
            rate_request.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Address.StateOrProvinceCode = self.contact.get(
                'StateOrProvinceCode')
            rate_request.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Address.PostalCode = self.contact.get(
                'PostalCode')
            rate_request.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Address.CountryCode = self.contact.get(
                'CountryCode')
            rate_request.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Address.Residential = self.contact.get(
                'Residential')

            rate_request.RequestedShipment.ShippingChargesPayment.PaymentType = 'SENDER'
            rate_request.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber = self.account_number

            spec = rate_request.create_wsdl_object_of_type('ShippingDocumentSpecification')
            spec.ShippingDocumentTypes = [spec.CertificateOfOrigin]
            rate_request.RequestedShipment.ShippingDocumentSpecification = spec

            rate_request.RequestedShipment.FreightShipmentDetail.CollectTermsType = 'STANDARD'

            role = rate_request.create_wsdl_object_of_type('FreightShipmentRoleType')
            rate_request.RequestedShipment.FreightShipmentDetail.Role = role.SHIPPER

        rate_request.RequestedShipment.PackagingType = 'YOUR_PACKAGING'

        if rateable_weight > 150:
            rate_request.RequestedShipment.Shipper.Address.StreetLines = "815 Jefferson Blvd"  # origin_address.address.address_line_1
            rate_request.RequestedShipment.Shipper.Address.City = "Warwick"  # origin_address.address.city
            rate_request.RequestedShipment.Shipper.Address.StateOrProvinceCode = 'RI'  # origin_address.address.state
            rate_request.RequestedShipment.Shipper.Address.PostalCode = '02884'  # origin_address.address.postal_code
            rate_request.RequestedShipment.Shipper.Address.CountryCode = 'US'  # country
            rate_request.RequestedShipment.Shipper.Address.Residential = False
        else:
            rate_request.RequestedShipment.Shipper.Address.StreetLines = origin_address.get('address')
            rate_request.RequestedShipment.Shipper.Address.City = origin_address.get('city')
            rate_request.RequestedShipment.Shipper.Address.StateOrProvinceCode = origin_address.get('state')
            rate_request.RequestedShipment.Shipper.Address.PostalCode = origin_address.get('postal_code')
            rate_request.RequestedShipment.Shipper.Address.CountryCode = origin_address.get('country')
            rate_request.RequestedShipment.Shipper.Address.Residential = False

        rate_request.RequestedShipment.Recipient.Address.PostalCode = destination.get('postal_code')
        rate_request.RequestedShipment.Recipient.Address.StateOrProvinceCode = destination.get('state')
        rate_request.RequestedShipment.Recipient.Address.City = destination.get('city')
        rate_request.RequestedShipment.Recipient.Address.CountryCode = destination.get('country')
        rate_request.RequestedShipment.Recipient.Address.Residential = True

        del rate_request.RequestedShipment.EdtRequestType

        if rateable_weight > 150:
            pallets = [self.lbs_per_pallet] * int(rateable_weight / self.lbs_per_pallet)
            pallets += [int(rateable_weight) % self.lbs_per_pallet] if int(
                rateable_weight) % self.lbs_per_pallet else []
            logger.info("Shipping pallets: %s" % pallets)

            for p in pallets:
                package_weight = rate_request.create_wsdl_object_of_type('Weight')
                package_weight.Value = p
                package_weight.Units = "LB"

                package = rate_request.create_wsdl_object_of_type('FreightShipmentLineItem')
                package.Packaging = 'PALLET'
                package.FreightClass = 'CLASS_065'

                package.Weight = package_weight
                rate_request.RequestedShipment.FreightShipmentDetail.LineItems.append(package)
                rate_request.RequestedShipment.FreightShipmentDetail.TotalHandlingUnits += 1

            rate_request.RequestedShipment.TotalWeight.Value = rateable_weight

            logger.info(rate_request.RequestedShipment.FreightShipmentDetail)
        else:
            # check each item
            for item in items:
                groupnumber = 1
                for box in item.get_boxes():
                    box_quantity = box[0]
                    box_weight = box[1]
                    box_length = box[2]('length')
                    box_width = box[2]('width')
                    box_height = box[2]('height')
                    logger.info("%s %s %sx%sx%s %slbs" % (
                    item.sku, box_quantity, box_length, box_width, box_height, box_weight))

                    # only go through the motions if there are actuall boxes to ship
                    if not box_quantity:
                        continue

                    # check for SMARTPost eligibility
                    if smart_post:
                        # determine if package is eligible for smartpost
                        smart_post_dims = box_length + (2 * box_width) + (2 * box_height) <= 84
                        smart_post_size = (True, True, True) in map(
                            lambda dim: (6 <= dim[0] < 60, 4 <= dim[1] < 60, 1 <= dim[2] < 60), itertools.permutations(
                                (box_length, box_width, box_height)))

                        smart_post_eligible = smart_post_dims and smart_post_size and item.product.get_weight() <= 70
                        if smart_post_eligible:
                            smart_post_count += 1

                    # per FedEx guidelines, if the dimensional weight is greater than the actual weight
                    # use the dimensional weight
                    dimensional_weight = box_length * box_width * box_height
                    dimensional_weight = dimensional_weight / 166 if destination.get(
                        'country') == "US" else dimensional_weight / 139
                    use_dimensional_weight = dimensional_weight > box_weight
                    if use_dimensional_weight:
                        logger.info(
                            "Using dimensional weight: %s vs Actual Weight: %s" % (dimensional_weight, box_weight))

                    package_weight = rate_request.create_wsdl_object_of_type('Weight')
                    package_weight.Value = float(dimensional_weight) if use_dimensional_weight else max(1, box_weight)
                    package_weight.Units = "LB"

                    package_dimensions = rate_request.create_wsdl_object_of_type('Dimensions')
                    package_dimensions.Length = box_length
                    package_dimensions.Width = box_width
                    package_dimensions.Height = box_height
                    package_dimensions.Units = "IN"

                    if rateable_weight > 150:
                        package = rate_request.create_wsdl_object_of_type('FreightShipmentLineItem')
                        package.Packaging = 'PALLET'
                        package.FreightClass = 'CLASS_065'
                    else:
                        package = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
                        package.PhysicalPackaging = 'BOX'

                    package.Weight = package_weight
                    package.Dimensions = package_dimensions

                    if rateable_weight > 150:
                        package.Weight.Value = package.Weight.Value * box_quantity
                        rate_request.RequestedShipment.FreightShipmentDetail.LineItems.append(package)
                        rate_request.RequestedShipment.FreightShipmentDetail.TotalHandlingUnits += 1
                        rate_request.RequestedShipment.TotalWeight.Value += package.Weight.Value * box_quantity
                    else:
                        # package.GroupPackageCount = 1
                        # for i in range(0, box_quantity):
                        #     rate_request.add_package(package)
                        package.GroupNumber = groupnumber
                        package.GroupPackageCount = box_quantity
                        rate_request.add_package(package)
                        groupnumber += 1

        if smart_post_count == len(items):
            logger.info("Package is eligible for smart post")
            rate_request.RequestedShipment.ServiceType = 'SMART_POST'
            rate_request.RequestedShipment.SmartPostDetail.Indicia = 'PRESORTED_STANDARD' if rateable_weight < 1 else 'PARCEL_SELECT'
            rate_request.RequestedShipment.SmartPostDetail.AncillaryEndorsement = 'CARRIER_LEAVE_IF_NO_RESPONSE'
            rate_request.RequestedShipment.SmartPostDetail.HubId = self.smart_post_hub_id

        # logger.info(rate_request.RequestedShipment)
        shipment.carrier_request = rate_request.RequestedShipment
        try:
            rate_request.send_request()
            shipment.carrier_response = rate_request.response
            self.rates = self._parse_response(rate_request)
        except FedexError as e:
            shipment.carrier_response = e

        shipment.save()

        return self.rates

    def _parse_response(self, rate_request):

        logger.info(rate_request.response)

        for detail in rate_request.response.RateReplyDetails[0].RatedShipmentDetails:
            for surcharge in detail.ShipmentRateDetail.Surcharges:
                if surcharge.SurchargeType == 'OUT_OF_DELIVERY_AREA':
                    logger.info("ODA rate_request charge %s" % surcharge.Amount.Amount)

        return_rates = []
        for rate_reply_detail in rate_request.response.RateReplyDetails:
            code = rate_reply_detail.ServiceType
            for rate_shipment_detail in rate_reply_detail.RatedShipmentDetails:
                rate_type = rate_shipment_detail.ShipmentRateDetail.RateType
                total_amount = rate_shipment_detail.ShipmentRateDetail.TotalNetFedExCharge.Amount
                if code in self.FEDEX__SCAC_LOOKUP_DICT:
                    scac = self.FEDEX__SCAC_LOOKUP_DICT[code]
                else:
                    logger.info("%s not found in SCAC Lookup Dictionary" % code)
                    continue
                code_split = scac.split("-")
                try:
                    carrier = Carrier.objects.get(carrier_code=code_split[0],
                                                  service_code=code_split[1] if len(code_split) > 1 else "")
                except Carrier.DoesNotExist:
                    logger.info("%s not found in Carrier Dictionary" % code)
                    carrier = Carrier.objects.create(carrier_code=code_split[0],
                                                     carrier_name=self.display_label,
                                                     service_code=code_split[1] if len(code_split) > 1 else "")
                logger.info("%s %s $%.2f" % (code, rate_type, total_amount))
                response_rate = ResponseRate.objects.create(shipment=self.shipment,
                                                            carrier=carrier,
                                                            time_in_transit=0,
                                                            rate=Decimal(str(total_amount)))
                response_rate.add_surcharges(self)
                return_rates.append(response_rate)

        return return_rates
