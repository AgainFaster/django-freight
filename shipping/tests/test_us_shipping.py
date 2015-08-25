from django.test import TestCase
import mock
from afshop.models import AgainFasterProduct
from shipping.exceptions import ShippingException
from shipping.models import Rate, USPSRateRequest
from shop.models import CartItem
from shipping.shipping_requestors import _get_shipping_rate_requestors, _get_rates


class TestUSShipping(TestCase):
    def setUp(self):
        pass

    # def test__get_rate(self):
    #     # from shipping.shipping_countries.US.shipping_requestors import _get_rate
    #     # test whether an Exception is caught correctly
    #     config = {'get_rate.side_effect': Exception}
    #     with mock.patch('shipping.models.Rate', **config) as mock_rate:
    #         import shipping
    #
    #         with self.assertRaises(Exception):
    #             _get_rate(mock_rate, [], None, False, 0, 0)
    #
    #     # test return values
    #     config = {'get_rate.return_value': True,
    #               'lowest_rate': 5,
    #               'get_surcharges': 5}
    #     with mock.patch('shipping.models.Rate', **config) as mock_rate:
    #         # if only_flat is True, the rates are queried to get carrier info (get_rate.return_value = True)
    #         # but the cost of flat_rate shipping items is returned
    #         self.assertEqual(
    #             _get_rate(rate_object=mock_rate, rate_args=[], cart=None,
    #                       only_flat=True,
    #                       flat_cost=10, subsidy=0),
    #             10
    #         )
    #         # if only_flat is False, rates are queried for rateable items and any flat_cost
    #         # is added to it
    #         self.assertEqual(
    #             _get_rate(rate_object=mock_rate, rate_args=[], cart=None,
    #                       only_flat=False,
    #                       flat_cost=10, subsidy=0),
    #             20
    #         )
    #         # whatever rate comes down at the end, the subsidy is added to it
    #         # for flat_rate only
    #         self.assertEqual(
    #             _get_rate(rate_object=mock_rate, rate_args=[], cart=None,
    #                       only_flat=True,
    #                       flat_cost=10, subsidy=10),
    #             20
    #         )
    #         # for none flat rate
    #         self.assertEqual(
    #             _get_rate(rate_object=mock_rate, rate_args=[], cart=None,
    #                       only_flat=False,
    #                       flat_cost=10, subsidy=10),
    #             30
    #         )

    def test__get_shipping_rate_requestors(self):

        # mock_filter = mock.Mock()
        # Rate.objects.filter = mock_filter
        # mock_filter.return_value = []

        with self.assertRaises(ShippingException):
            _get_shipping_rate_requestors()

        # mock_filter.return_value = [mock.Mock()]
        # USPSRateRequest.objects.filter = mock_filter
        # mock_filter.return_value = [USPSRateRequest()]

        USPSRateRequest.objects.create(enabled=True, debug=False, country='US')

        self.assertTrue(
            _get_shipping_rate_requestors(country="US", originating_warehouse=None, debug=False)
        )

    def test_get_rates(self):
        pass