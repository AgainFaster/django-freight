from django.conf.urls import patterns, url
from shipping.api import ShippingRateRequest

__author__ = 'jule'


urlpatterns = patterns('',
                       url(r'api/v1/shipment[/]?$', ShippingRateRequest.as_view(), name='shipping_rate_request'),
                       )

