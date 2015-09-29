from django.contrib import admin
from django.contrib.admin import StackedInline, TabularInline
from super_inlines.admin import SuperModelAdmin, SuperInlineModelAdmin
from shipping.models import *


class SurchargeInline(admin.TabularInline):
    model = Surcharge
    min_num = 1
    extra = 0


class RuleInline(admin.TabularInline):
    model = Rule
    min_num = 1
    extra = 0


class RateAdmin(admin.ModelAdmin):
    inlines = [SurchargeInline, RuleInline]
    list_display_links = ["nickname"]
    list_editable = ["enabled"]
    list_filter = ["enabled"]
    list_display = ["nickname", "enabled", "debug"]


admin.site.register(Rate, RateAdmin)


class FedExRateRequestAdmin(RateAdmin):
    pass


admin.site.register(FedExRateRequest, FedExRateRequestAdmin)


class UPSRateRequestAdmin(RateAdmin):
    pass


admin.site.register(UPSRateRequest, UPSRateRequestAdmin)


class USPSRateRequestAdmin(RateAdmin):
    pass


admin.site.register(USPSRateRequest, USPSRateRequestAdmin)


class ModeRateRequestAdmin(RateAdmin):
    pass


admin.site.register(ModeRateRequest, ModeRateRequestAdmin)


class CanadaPostRateRequestAdmin(RateAdmin):
    pass


admin.site.register(CanadaPostRateRequest, CanadaPostRateRequestAdmin)


class FreightExpressRateRequestAdmin(RateAdmin):
    pass


admin.site.register(FreightExpressRateRequest, FreightExpressRateRequestAdmin)


class AustraliaPostRateRequestAdmin(RateAdmin):
    pass


admin.site.register(AustraliaPostRateRequest, AustraliaPostRateRequestAdmin)


class CarrierAdmin(admin.ModelAdmin):
    model = Carrier
    fields = [('carrier_code', 'carrier_name'),
              ('service_code', 'service_code_description'),
              ('enabled', 'hide_from_customers'),
              'customer_display_text',
              ('include_tracking_number', 'url_pattern')]
    list_filter = ['enabled']
    ordering = ['-enabled', 'carrier_code', 'service_code']
    search_fields = ['carrier_name', 'carrier_code', 'service_code', 'service_code_description']
    list_display = ['__unicode__', 'enabled', 'hide_from_customers']
    list_editable = ['enabled', 'hide_from_customers']


admin.site.register(Carrier, CarrierAdmin)


class ResponseSurchargeInline(SuperInlineModelAdmin, TabularInline):
    model = ResponseSurcharge
    min_num = 1
    extra = 0


class ItemInline(SuperInlineModelAdmin, TabularInline):
    model = Item
    extra = 0


class ResponseRateInline(SuperInlineModelAdmin, StackedInline):
    model = ResponseRate
    inlines = (ResponseSurchargeInline,)
    extra = 0
    min_num = 1


class ShipmentInline(SuperInlineModelAdmin, StackedInline):
    model = Shipment
    inlines = (ItemInline, ResponseRateInline)
    extra = 0


class ShippingRequestAdmin(SuperModelAdmin):
    inlines = (ShipmentInline,)
    list_display = ['__str__', 'user', 'ip']
    list_filter = ['user', 'ip']


admin.site.register(ShippingRequest, ShippingRequestAdmin)