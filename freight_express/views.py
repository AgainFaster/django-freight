# Create your views here.
import json
from django.http import HttpResponse


def netsuite_fedex_test(request):
    return_dict = [
        {
            "warehouse_id": 1,
            "rates": [
                {
                    "carrier": "FedEx Freight Economy",
                    "carrier_code": "FXNL",
                    "service_code": None,
                    "time_in_transit": 3,
                    "rate": 100.6
                },
                {
                    "carrier": "FedEx Freight Priority",
                    "carrier_code": "FXFE",
                    "service_code": None,
                    "time_in_transit": 2,
                    "rate": 201.2
                }
            ]
        },
        {
            "warehouse_id": 2,
            "rates": [
                {
                    "carrier": "FedEx Home Delivery",
                    "carrier_code": "FDX",
                    "service_code": "HOM",
                    "time_in_transit": 3,
                    "rate": 50.6
                },
                {
                    "carrier": "FedEx Overnight",
                    "carrier_code": "FDX",
                    "service_code": "PRT",
                    "time_in_transit": 1,
                    "rate": 400.53
                }
            ]
        }
    ]

    return HttpResponse(json.dumps(return_dict))
