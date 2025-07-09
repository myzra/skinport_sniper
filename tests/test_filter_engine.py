import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core")))

from filter_engine import filter_item


sales_data = [
    {
        "eventType": "listed",
        "sale": {
            "saleId": 61598590,
            "marketName": "Karambit Tiger Tooth",
            "category": "Knife",
            "salePrice": "200",
            "wear": "0.02453",
            "pattern": 231,
            "exterior": "Minimal Wear",
            "tags": [
                {"name": "Industrial Grade"},
                {"name": "Minimal Wear"}
            ]
        },
        "timestamp": 1746650292048
    },
    {
        "eventType": "listed",
        "sale": {
            "saleId": 61598591,
            "marketName": "Desert Eagle | The Bronze (Minimal Wear)",
            "category": "Pistol",
            "salePrice": "10",
            "wear": "0.06424",
            "pattern": 81,
            "exterior": "Minimal Wear",
            "tags": [
                {"name": "Industrial Grade"},
                {"name": "Field Tested"}
            ]
        },
        "timestamp": 1746650292048
    },
    {
        "eventType": "listed",
        "sale": {
            "saleId": 61598592,
            "marketName": "StatTrak™ MP9 | Nexus (Minimal Wear)",
            "category": "SMG",
            "salePrice": "50",
            "wear": "0.04311",
            "pattern": 321,
            "exterior": "Factory New",
            "tags": [
                {"name": "Mil-Spec Grade"},
                {"name": "Minimal Wear"}
            ]
        },
        "timestamp": 1746650292048
    }
]

query_params = {
    "names": "Karambit",
    "minPrice": "50",
    "maxPrice": "210",
    "patterns": "100, 231, 31, 321",
    "minWear": "0.001",   # Mindest-Wear von 0.1
    "maxWear": "0.5",   # Maximal-Wear vom 0.5
    "exterior": "Minimal Wear"    # Nur Well-Worn Items
}

for s in sales_data:
    print(filter_item(sale=s, query_params=query_params))