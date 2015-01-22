from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import PROTECT


class Location(models.Model):
    postcode = models.CharField(max_length=4, unique=True)


class AUSurchargeTier(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    surcharge = models.FloatField()

    class Meta:
        verbose_name = "AU Surcharge Tier"

    def __unicode__(self):
        return "%s ($%s)" % (self.name, self.surcharge)


class AUZone(models.Model):
    name = models.CharField(max_length=5, blank=False, null=False, unique=True)
    long_name = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        verbose_name = "AU Zone"
        ordering = ['name']

    def __unicode__(self):
        return self.name


class AUPostCode(Location):
    surcharge = models.ForeignKey(AUSurchargeTier, blank=True, null=True)
    zone = models.ForeignKey(AUZone, related_name="postcodes", blank=False, null=False)

    class Meta:
        verbose_name = "AU Post Code"

    def __unicode__(self):
        return self.postcode


class AUFee(models.Model):
    name = models.CharField(help_text="Name by which to identify the fee",
                            max_length=255, blank=False, null=True)
    fee = models.FloatField(help_text="Fee to add to the returned rate")
    enabled = models.BooleanField(help_text="Fee is currently active and being applied to the rate",
                                  blank=False, null=False, default=False)
    percentage = models.BooleanField(help_text="Enable if fee is to be calculated as a percentage of the rate",
                                     blank=False, null=False, default=False)

    class Meta:
        verbose_name = "AU Fee"

    def __unicode__(self):
        if not self.percentage:
            return "%s ($%.2f)" % (self.name, self.fee)
        return "%s (%.2f%%)" % (self.name, self.fee)


class Rate(models.Model):
    from_zone = models.ForeignKey(AUZone, blank=True, null=True, related_name="origin_rates")
    to_zone = models.ForeignKey(AUZone, blank=True, null=True, related_name="destination_rates")
    service = models.CharField(max_length=25, blank=True, null=True, default="EXP") #so far just "EXP", but could change, I guess
    basic_charge = models.FloatField()
    rate = models.FloatField()
    type = models.CharField(max_length=25, blank=True, null=True, default="KG", choices=[('KG', 'KG'),('LB', 'LB')]) #Kilo
    min_charge = models.FloatField()
    cubic_conv = models.FloatField(default=250.0)

    class Meta:
        unique_together = (('from_zone', 'to_zone',))
        verbose_name = "AU Rate"

    def __unicode__(self):
        return "%s -> %s" % (self.from_zone.name, self.to_zone.name)


class UKShippingProvider(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        verbose_name = "UK Shipping Provider"
    def __unicode__(self):
        return "%s" % self.name


class UKRate(models.Model):
    from_country_code =  models.CharField(max_length=2, blank=False, null=False) # ISO
    to_country_code =  models.CharField(max_length=2, blank=False, null=False) # ISO
    to_region = models.CharField(max_length=100, blank=True, null=True)
    shipping_provider = models.ForeignKey(UKShippingProvider, on_delete=PROTECT)
    max_weight = models.FloatField(default=0)
    initial_rate = models.FloatField(default=0)
    weight_multiplier_rate = models.FloatField(default=0)
    weight_offset = models.FloatField(default=0)

    def __unicode__(self):

        to_county_string = 'DEFAULT COUNTIES'
        if self.to_region:
            to_county_string = self.to_region
        #    return_string = "%s (%s)" % (return_string, self.to_region)

        return_string = "%s -> %s (%s)" % (self.from_country_code, self.to_country_code, to_county_string)

        if self.weight_multiplier_rate:
            formula = "%s + (weight - %s) * %s" % (self.initial_rate, self.weight_offset, self.weight_multiplier_rate)
        else:
            formula = self.initial_rate

        return_string = "%s /// <=%skg, Carrier: %s /// Formula: %s" % (return_string, self.max_weight, self.shipping_provider.name, formula)

        return return_string

    class Meta:
        verbose_name = "UK Rate"
        # django 1.3 only respects the first element in a tuple
        ordering = ('-max_weight',)


class NZDistanceFactor(models.Model):
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    default_freight_tonne_rate = models.FloatField(null=True, blank=True)
    default_freight_cubic_rate = models.FloatField(null=True, blank=True)
    minimum_freight_cost = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "NZ Distance Factor"

    def __unicode__(self):
        return "Area #%s - %s" % (self.number, self.name)


class NZLocation(models.Model):
    postcode = models.CharField(max_length=4)
    distance_factor = models.ForeignKey(NZDistanceFactor)
    location_name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    is_rural = models.BooleanField()
    town_code = models.CharField(max_length=3)
    delivery_depot = models.CharField(max_length=100)

    class Meta:
        verbose_name = "NZ Location"

    def __unicode__(self):
        return "%s, %s %s (%s)" % (self.area, self.city, self.postcode, self.distance_factor)


class NZCourierRate(models.Model):
    distance_factor = models.ForeignKey(NZDistanceFactor)
    max_weight = models.IntegerField(default=5)
    cubic_conversion = models.FloatField()
    rate = models.FloatField()

    class Meta:
        verbose_name = "NZ Courier Rate"

    def __unicode__(self):
        return "%s, cubic factor: %s, rate: $%s" % (self.distance_factor, self.cubic_conversion, self.rate)


class NZFreightRate(models.Model):
    destinations = models.ManyToManyField(NZLocation)
    destination_group = models.CharField(max_length=100)
    tonne_rate = models.FloatField()
    cubic_rate = models.FloatField()

    class Meta:
        verbose_name = "NZ Freight Rate"

    def __unicode__(self):
        return "%s %s per tonne, %s per cubic meter" % (self.destination_group, self.tonne_rate, self.cubic_rate)


class CAFreightRate(models.Model):
    from_province = models.CharField(max_length=2)
    to_province = models.CharField(max_length=2)
    to_city = models.CharField(max_length=100, blank=True, null=True)
    rate = models.FloatField()

    class Meta:
        unique_together = (('from_province', 'to_province', 'to_city'),)
        verbose_name = 'CA Freight Rate'

    def __unicode__(self):
        return '%s primary warehouse -> %s, %s - $%.2f' % (self.from_province, self.to_city if self.to_city else '(DEFAULT)', self.to_province, self.rate)


class CAFreightMultiplier(models.Model):
    description = models.CharField(max_length=100, blank=True, null=True)
    from_province = models.CharField(max_length=2)
    sku_list = models.TextField()
    multiplier = models.FloatField()

    class Meta:
        verbose_name = 'CA Freight Multiplier'

    def __unicode__(self):
        return '%s primary warehouse - %s x %s' % (self.from_province, self.description, self.multiplier)


class CAFreightSettings(models.Model):
    from_province = models.CharField(max_length=2, unique=True)
    skid_weight = models.FloatField(default=50.0)
    minimum_weight = models.FloatField(default=640.0)
    default_multiplier = models.FloatField(default=1.2)
    surcharge = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'CA Freight Setting'

    def __unicode__(self):
        return 'Settings for %s primary warehouse' % self.from_province
