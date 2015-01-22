from django.conf.urls import patterns, include
from freight_express.api import RateResource

__author__ = 'jule'

from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(RateResource())

urlpatterns = patterns('',
    (r'^api/', include(v1_api.urls)),
)