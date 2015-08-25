from decimal import Decimal
from django.db import models
from suds.client import Client
from suds import WebFault, null
import logging, os
from django.conf import settings
from .basemodel import Rate


class UPSRateRequest(Rate):

    license_number = models.CharField(max_length=255, blank=False, null=False)
    account_name = models.CharField(max_length=255, blank=False, null=False)
    password = models.CharField(max_length=255, blank=False, null=False)
    shipper_number = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        app_label = "shipping"
        verbose_name = "UPS Settings"
        verbose_name_plural = "UPS Settings"

    def __init__(self, *args, **kwargs):

        super(UPSRateRequest, self).__init__(*args, **kwargs)

        self.UPS_SCAC_LOOKUP_DICT = {
            '01': 'UPSM-NDAY',  # Next Day Air',            #UPSM-NDAY
            '02': 'UPSM-2DAY',  # 2nd Day Air',             #UPSM-2DAY
            '03': 'UPSM-GRND',  # Ground',                  #UPSM-GRND
            '12': 'UPSM-3DAY',  # 3 Day Select",            #UPSM-3DAY
            '13': 'UPSM-NDAS',  # Next Day Air Saver',      #VERIFY
            '14': 'UPSM-NDAM',  # Next Day Air Early AM',   #UPSM-NDAM
            '59': 'UPSM-2AIR',  # 2nd Day Air AM'           #UPSM-2AIR
        }

        logging.basicConfig(level=logging.INFO)
        if settings.DEBUG:
            logging.getLogger('suds.client').setLevel(logging.DEBUG)
        self.logger = logging.getLogger('Shipping')


    def _create_access_token(self):
        self.access_token = {
            'UPSSecurity': {
                'ServiceAccessToken': {
                    'AccessLicenseNumber': self.license_number
                },
                'UsernameToken': {
                    'Username': self.account_name,
                    'Password': self.password
                }
            }
        }

    def _create_url(self):
        self.url = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'UPS-WSDLs/RateWS.wsdl')

    def get_rate(self, shipment, items, origin_address, destination):
        country = 'US'  # 'merica.

        self._create_url()
        client = Client('file://%s' % self.url)
        self._create_access_token()
        client.set_options(soapheaders=self.access_token)

        requestType = {'RequestOption': 'Shop'}
        shipment = client.factory.create('ns2:ShipmentType')
        shipment['Shipper'] = {
            'ShipperNumber': 'E0A334',
            'Name': 'AgainFaster',
            'Address': {
                'AddressLine': [origin_address.get('address')],
                'City': origin_address.get('city'),
                'StateProvinceCode': origin_address.get('state'),
                'PostalCode': origin_address.get('postal_code'),
                'CountryCode': origin_address.get('country'),
            }
        }
        shipment['ShipTo'] = {
            'Address': {
                'PostalCode': destination.get('postal_code'),
                'CountryCode': destination.get('country'),
                'StateProvinceCode': destination.get('state'),
                # 'ResidentialAddressIndicator' : True
            }
        }
        # shipment['Service']['Code'] = '03'  # UPS Ground

        packages = []
        for item in items:
            for box in item.get_boxes():
                box_quantity = box[0]
                box_weight = box[1]
                box_length = box[2]('length')
                box_width = box[2]('width')
                box_height = box[2]('height')
                # Describe a box
                package = {
                    'PackagingType': {'Code': '02'},  # Means customer supplied box.
                    'PackageWeight': {
                        'UnitOfMeasurement': {
                            'Code': 'LBS'
                        },
                        'Weight': box_weight
                    },
                    'Dimensions': {
                        'UnitOfMeasurement': {
                            'Code': 'IN'
                        },
                        'Length': box_length,
                        'Width': box_width,
                        'Height': box_height,
                    },
                }
                for i in range(box_quantity):
                    packages.append(package)
        shipment['Package'] = packages
        shipment['ShipmentRatingOptions']['NegotiatedRatesIndicator'] = null()

        classification = client.factory.create('ns2:CodeDescriptionType')
        classification.Code = '00'  # Get rates for the shipper account

        try:
            result = client.service.ProcessRate(
                **{'Request': requestType, 'Shipment': shipment, 'CustomerClassification': classification})
        except WebFault as ex:
            self.logger.info('Sent to UPS \n %s' % shipment)
            self.logger.info('The result was \n %s' % ex)
            raise Exception('There was an error in UPS')

        self.rates = self._parse_response(result)
        # print self.rates
        return self.rates

    def _parse_response(self, response):
        error_code = int(response['Response']['ResponseStatus']['Code'])
        if error_code == 1:
            ret_dict = {}
            for rated_shipment in response['RatedShipment']:
                code = rated_shipment['Service']['Code']
                total_charge = Decimal(rated_shipment['NegotiatedRateCharges']['TotalCharge']['MonetaryValue'])
                self.logger.info("UPS cost for service %s (%s): $%.2f" % (code, self.UPS_SCAC_LOOKUP_DICT[code], float(total_charge)))
                ret_dict.update({self.UPS_SCAC_LOOKUP_DICT[code]: {"rate": total_charge}})
            return ret_dict
        else:
            error_message = response['Response']['ResponseStatus']['Description']
            raise Exception("There was an error in UPS: %s: %s" % (error_code, error_message))


