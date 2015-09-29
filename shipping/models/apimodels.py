from decimal import Decimal
import json
from django.contrib.auth.models import User
from django.db import models
from shipping.models.carriermodel import Carrier
from .basemodel import Surcharge


class ShippingRequest(models.Model):
    raw_request = models.TextField()
    destination = models.TextField()
    received = models.DateTimeField(editable=False)
    raw_response = models.TextField()
    user = models.ForeignKey(User)
    ip = models.IPAddressField()

    def __str__(self):
        return "%s: %s" % (self.id, self.received)

    def serialize(self):
        return [shipment.serialize() for shipment in self.shipments.all()]

    class Meta:
        app_label = "shipping"


class Shipment(models.Model):
    shipping_request = models.ForeignKey(ShippingRequest, related_name="shipments")
    warehouse = models.IntegerField()
    origin = models.TextField()
    carrier_request = models.TextField()
    carrier_response = models.TextField()

    def __str__(self):
        return "Warehouse %s" % self.warehouse

    def serialize(self):
        return {"warehouse_id": self.warehouse,
                "rates": [rate.serialize() for rate in self.rates.all()]}

    class Meta:
        app_label = "shipping"


class Item(models.Model):
    shipment = models.ForeignKey(Shipment, related_name="items")
    sku = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=10)
    flat_rate = models.DecimalField(max_digits=12, decimal_places=2)
    ships_free = models.BooleanField(default=False)
    quantity = models.IntegerField(null=False)
    dimensions = models.CharField(max_length=255)
    inner = models.CharField(max_length=255)
    carton = models.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        self.carton_dict = {}
        self.inner_dict = {}
        self.dimensions_dict = {}

    def __str__(self):
        return "%s - %s" % (self.quantity, self.sku)

    def get_dimensions(self, *args):
        if not self.dimensions_dict:
            self.dimensions_dict = json.loads(self.dimensions)
        if args:
            return int(self.dimensions_dict.get(args[0]))
        return self.dimensions_dict

    def get_carton(self, *args):
        if not self.carton_dict:
            self.carton_dict = json.loads(self.carton)
        carton = self.carton_dict or copy_dict(self.get_inner(), {'qty': 1}) or copy_dict(self.get_dimensions(), {'qty': 1})
        if args:
            return int(carton.get(args[0]))
        return carton

    def get_inner(self, *args):
        if not self.inner_dict:
            self.inner_dict = json.loads(self.inner)
        inner = self.inner_dict or copy_dict(self.get_dimensions(), {'qty': 1})
        if args:
            return int(inner.get(args[0]))
        return inner

    @property
    def length(self):
        return self.get_dimensions('length')

    @property
    def width(self):
        return self.get_dimensions('width')

    @property
    def height(self):
        return self.get_dimensions('height')

    def get_weight(self):
        return self.weight * self.quantity

    def get_boxes(self):
        #find the amount of full cartons
        num_cartons = int(self.quantity / self.get_carton('qty'))
        #find the amount left over
        carton_remainder = self.quantity % self.get_carton('qty')
        #find the amount of full inners
        num_inners = int(carton_remainder / self.get_inner('qty'))
        #find the amount left over
        inner_remainder = carton_remainder % self.get_inner('qty')

        #if leftovers fit in an inner, put in 1 inner at the weight of the leftovers * weight
        if inner_remainder and inner_remainder < self.get_inner('qty'):
            left_over = 1
            left_over_weight = inner_remainder * self.weight
        else:
            #else put in the amount of left over, at the weight of a single
            left_over = inner_remainder
            left_over_weight = self.weight

        carton_weight = self.get_carton('qty') * self.weight
        inner_weight = self.get_inner('qty') * self.weight

        return_list = [(num_cartons, carton_weight, self.get_carton),
                       (num_inners, inner_weight, self.get_inner),
                       (left_over, left_over_weight, self.get_dimensions)]
        return return_list

    class Meta:
        app_label = "shipping"
        get_latest_by = "id"


class ResponseRate(models.Model):
    shipment = models.ForeignKey(Shipment, related_name="rates")
    carrier = models.ForeignKey(Carrier, related_name="rates")
    time_in_transit = models.IntegerField()
    rate = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return "%s - $%s" % (self.carrier, self.rate)

    def add_surcharges(self, rater):
        for surcharge in rater.surcharge_set.filter(active=True):
            if surcharge.percentage:
                surcharge_amount = surcharge.amount * (self.rate / Decimal('100.0'))
            else:
                surcharge_amount = surcharge.amount
            ResponseSurcharge.objects.create(ratedrate=self, surcharge=surcharge, amount=surcharge_amount)

    def get_total_rate(self):
        return self.rate + sum(surcharge.amount for surcharge in self.surcharges.all())

    def serialize(self):
        return {"carrier": self.carrier.__str__(),
                "carrier_code": self.carrier.carrier_code,
                "service_code": self.carrier.service_code,
                "time_in_transit": self.time_in_transit,
                "rate": self.rate,
                "total_rate": self.get_total_rate(),
                "surcharges": [surcharge.serialize() for surcharge in self.surcharges.all()]}
    class Meta:
        app_label = "shipping"


class ResponseSurcharge(models.Model):
    ratedrate = models.ForeignKey(ResponseRate, related_name="surcharges")
    surcharge = models.ForeignKey(Surcharge, related_name="rates")
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def serialize(self):
        return {"name": self.surcharge.description,
                "amount": self.amount}

    def __str__(self):
        return "%s - $%s" % (self.surcharge.description, self.amount)

    class Meta:
        app_label = "shipping"


def copy_dict(source_dict, diffs):
    """Returns a copy of source_dict, updated with the new key-value
       pairs in diffs."""
    res = dict(source_dict) # Shallow copy, see addendum below
    res.update(diffs)
    return res
