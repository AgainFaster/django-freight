# Create your views here.
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def netsuite_fedex_test(request):
    return_dict = [
        {
            "warehouse_id": 1,
            "rates": [
                {
                    "carrier": "FedEx Freight Economy",
                    "carrier_code": "FXNL",
                    "service_code": None,
                    "rate": 100.6,
                    "surcharges": [
                        {
                            "name": "Shipping & Handling",
                            "rate": 2.50
                        },
                        {
                            "name": "Dean Markup",
                            "rate": 10.06
                        }
                    ],
                    "total_rate": 113.16
                },
                {
                    "carrier": "FedEx Freight Priority",
                    "carrier_code": "FXFE",
                    "service_code": None,
                    "rate": 201.2,
                    "surcharges": [
                        {
                            "name": "Shipping & Handling",
                            "rate": 2.50
                        },
                        {
                            "name": "Dean Markup",
                            "rate": 20.12
                        }
                    ],
                    "total_rate": 223.82
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
                    "rate": 50.6,
                    "surcharges": [
                        {
                            "name": "Shipping & Handling",
                            "rate": 2.50
                        },
                        {
                            "name": "Dean Markup",
                            "rate": 5.06
                        }
                    ],
                    "total_rate": 58.16
                },
                {
                    "carrier": "FedEx Overnight",
                    "carrier_code": "FDX",
                    "service_code": "PRT",
                    "time_in_transit": 1,
                    "rate": 400.53,
                    "surcharges": [
                        {
                            "name": "Shipping & Handling",
                            "rate": 2.50
                        },
                        {
                            "name": "Dean Markup",
                            "rate": 40.05
                        }
                    ],
                    "total_rate": 443.08
                }
            ]

        }

    ]

    return HttpResponse(json.dumps(return_dict), content_type="application/json")
