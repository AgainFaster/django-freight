from django.contrib import admin
from django.contrib.admin import ModelAdmin
from freight_express.models import *

__author__ = 'jule'


class AUPostCodeAdmin(admin.ModelAdmin):
    ordering = ['postcode']
    search_fields = ['postcode']
    list_display = ['postcode', 'zone', 'surcharge']
    list_filter = ['zone', 'surcharge']
    list_editable = ['surcharge']


class AUSurchargeTierAdmin(admin.ModelAdmin):
    pass


class AUPostCodeInline(admin.TabularInline):
    model = AUPostCode
    ordering = ['postcode']


class AUZoneAdmin(admin.ModelAdmin):
    inlines = [AUPostCodeInline]
    ordering = ['name']


class AUFeeAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = ['enabled', '__unicode__']
    list_editable = ['enabled']
    list_display_links = ['__unicode__']


class RateAdmin(ModelAdmin):
    ordering = ['to_zone']
    search_fields = ['from_zone', 'to_zone']


class UKRateAdmin(ModelAdmin):
    list_filter = ('from_country_code', 'to_country_code', 'to_region')
    ordering = ['from_country_code', 'to_country_code', 'to_region', '-max_weight']


class UKShippingProviderAdmin(ModelAdmin):
    pass


class NZLocationAdmin(ModelAdmin):
    search_fields = ('area', 'city', 'location_name', 'postcode')


class NZDistanceFactorAdmin(ModelAdmin):
    pass


class NZCourierRateAdmin(ModelAdmin):
    pass


class NZFreightRateAdmin(ModelAdmin):
    filter_vertical = ('destinations',)


class CAFreightRateAdmin(ModelAdmin):
    pass


class CAFreightMultiplierAdmin(ModelAdmin):
    pass


class CAFreightSettingsAdmin(ModelAdmin):
    pass


admin.site.register(AUPostCode, AUPostCodeAdmin)
admin.site.register(AUSurchargeTier, AUSurchargeTierAdmin)
admin.site.register(AUZone, AUZoneAdmin)
admin.site.register(AUFee, AUFeeAdmin)
admin.site.register(Rate, RateAdmin)

admin.site.register(UKRate, UKRateAdmin)
admin.site.register(UKShippingProvider, UKShippingProviderAdmin)

admin.site.register(NZLocation, NZLocationAdmin)
admin.site.register(NZDistanceFactor, NZDistanceFactorAdmin)
admin.site.register(NZCourierRate, NZCourierRateAdmin)
admin.site.register(NZFreightRate, NZFreightRateAdmin)

admin.site.register(CAFreightRate, CAFreightRateAdmin)
admin.site.register(CAFreightMultiplier, CAFreightMultiplierAdmin)
admin.site.register(CAFreightSettings, CAFreightSettingsAdmin)