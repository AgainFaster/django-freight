from decimal import Decimal
from django.test import TestCase
import sys
import mock
from core.models import Address, PhoneNumber
from shipping.models import Rate, Surcharge, Rule


class TestRate(TestCase):
    def setUp(self):
        super(TestRate, self).setUp()

        self.address = Address.objects.create(first_name="test first name",
                                              last_name="test_last_name",
                                              address_line_1="test address line 1",
                                              address_line_2="test address line 1",
                                              company="test company",
                                              city="test city",
                                              postal_code="01234",
                                              state="MA",
                                              country="US",
                                              phone_number=PhoneNumber.objects.create(phone_number="555-212-1122",
                                                                                      number_type=1)
        )

        self.rate = Rate.objects.create(nickname="Test Rate",
                                        country="US",
                                        enabled=True)

        self.rate.rates = {'FDX': {'rate': 16.0}, 'UPSM-GRND': {'rate': 12.0}, 'USPS': {'rate': 14.0}}

    def test_get_rate(self):
        # base class should return NotImplementedError
        with self.assertRaises(NotImplementedError):
            self.rate.get_rate(items=[], origin_address=self.address, shipping_quote_destination=None)

    def test_get_lowest_rate(self):
        self.assertEqual(
            self.rate.lowest_rate,
            12.0
        )

    def test_lowest_rate_carrier_code(self):
        self.assertEqual(
            self.rate.lowest_rate_carrier_code,
            'UPSM'
        )

    def test_lowest_rate_service_code(self):
        self.assertEqual(
            self.rate.lowest_rate_service_code,
            'GRND'
        )

        self.rate.rates = {'FDX': {'rate': 16.0}, 'UPSM': {'rate': 12.0}, 'USPS': {'rate': 14.0}}

        self.assertFalse(
            self.rate.lowest_rate_service_code
        )

    def test_get_surcharges(self):
        Surcharge.objects.create(rate=self.rate,
                                 description="Test Surcharge",
                                 amount=Decimal("15.0"),
                                 active=True)

        self.assertEqual(
            self.rate.get_surcharges,
            15
        )

        surcharge_2 = Surcharge.objects.create(rate=self.rate,
                                               description="Test Surcharge 2",
                                               amount=Decimal("15.0"),
                                               active=True)

        self.assertEqual(
            self.rate.get_surcharges,
            30
        )

        surcharge_2.active = False
        surcharge_2.save()

        self.assertEqual(
            self.rate.get_surcharges,
            15
        )

    def test_in_range(self):
        # no rules, will return False
        self.assertFalse(
            self.rate.in_range(100)
        )

        rule_1 = Rule.objects.create(rate=self.rate,
                                     min_value="0",
                                     max_value="100")

        self.assertTrue(
            self.rate.in_range(0)
        )

        self.assertTrue(
            self.rate.in_range(50)
        )

        self.assertFalse(
            self.rate.in_range(100)
        )

        self.assertFalse(
            self.rate.in_range(150)
        )

        rule_1.min_value = 100
        rule_1.max_value = 0
        rule_1.save()

        self.assertFalse(
            self.rate.in_range(0)
        )

        self.assertFalse(
            self.rate.in_range(50)
        )

        self.assertTrue(
            self.rate.in_range(100)
        )

        self.assertTrue(
            self.rate.in_range(150)
        )

        self.assertTrue(
            self.rate.in_range(sys.maxint)
        )




