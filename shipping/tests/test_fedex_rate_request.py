from django.test import TestCase
from core.models import PhoneNumber, Address


class TestFedExRateRequest(TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
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
                                                                                      number_type=1))

    def test_parse_response(self):
        pass
