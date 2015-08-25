import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from shipping.models import ShippingRequest, Shipment, Item
from datetime import datetime
from shipping.tasks import get_shipping_rates


def _response(request, summary=None, success=True):
    response_status = status.HTTP_200_OK if success else status.HTTP_500_INTERNAL_SERVER_ERROR
    return Response({'request_id': request.DATA.get('request_id'), 'summary': summary}, status=response_status)


class ShippingRateRequest(APIView):

    def get(self, request, *args, **kw):
        return _response(request, 'GET is currently not implemented. Try POST.')

    def post(self, request, *args, **kw):

        raw_request = request.DATA.get('request')
        if not raw_request:
            return _response(request, 'No request data received.', False)

        shipments = raw_request.get('shipments')
        if not shipments:
            return _response(request, 'No shipment data received.', False)

        destination = raw_request.get('destination')
        if not destination:
            return _response(request, 'No destination address received.', False)

        incoming_request = ShippingRequest.objects.create(raw_request=json.dumps(raw_request),
                                                          destination=json.dumps(raw_request.get('destination')),
                                                          received=datetime.now())

        for warehouse_id in shipments.keys():
            shipment = shipments[warehouse_id]
            shipment_object = Shipment.objects.create(shipping_request=incoming_request,
                                                      warehouse=warehouse_id,
                                                      origin=json.dumps(shipment.get('origin')))
            for item in shipment.get('items'):
                Item.objects.create(shipment=shipment_object,
                                    sku=item.get('sku'),
                                    weight=item.get('weight'),
                                    unit=item.get('unit') or "lb",
                                    flat_rate=item.get('flat_rate') or 0,
                                    ships_free=True if item.get('ships_free') == "true" else False,
                                    quantity=item.get('quantity'),
                                    dimensions=json.dumps(item.get('dimensions', {})),
                                    inner=json.dumps(item.get('inner', {})),
                                    carton=json.dumps(item.get('carton', {}))
                                    )

            get_shipping_rates(shipment_object, json.loads(incoming_request.destination))

        incoming_request.raw_response = incoming_request.serialize()
        incoming_request.save()

        return _response(request, incoming_request.raw_response)