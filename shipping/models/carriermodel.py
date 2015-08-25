from django.db import models


class Carrier(models.Model):
    carrier_code = models.CharField(max_length=5, blank=False, null=False,
                                    help_text="Carrier Code.")
    carrier_name = models.CharField(max_length=100, blank=False, null=False,
                                    help_text="Carrier Name.")
    service_code = models.CharField(max_length=5, blank=True, null=True,
                                    help_text="Carrier Service Code.")
    service_code_description = models.CharField(max_length=100, blank=True, null=True,
                                                help_text="Service Code Description.")
    enabled = models.BooleanField(default=False,
                                  help_text="Enable this Carrier.")
    hide_from_customers = models.BooleanField(default=False,
                                              help_text="Allow customers to select this carrier as an option.")
    customer_display_text = models.CharField(max_length=25, blank=True, null=True,
                                             help_text="Name with which to override Carrier Name to customers.")

    url_pattern = models.CharField(max_length=200, blank=True, null=True)
    include_tracking_number = models.BooleanField(default=True)

    class Meta:
        app_label = 'shipping'

    def __unicode__(self):
        return self.__str__()


    def __str__(self):
        if self.service_code:
            ret = "%s: %s (%s-%s)" % (self.carrier_name, self.service_code_description,
                                       self.carrier_code, self.service_code)
        else:
            ret = "%s (%s)" % (self.carrier_name, self.carrier_code)

        return ret

    @property
    def get_customer_display_text(self):

        if self.customer_display_text and self.customer_display_text.strip():
            return self.customer_display_text

        if self.service_code:
            ret = "%s %s" % (self.carrier_name, self.service_code_description)
        else:
            ret = "%s" % (self.carrier_name)

        return ret

    @property
    def get_carrier_service_code(self):
        return '%s-%s' % (self.carrier_code, self.service_code)