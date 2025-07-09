def filter_item(sale, query_params):
    if sale["eventType"] != "listed":
        return False

    item = sale["sale"]

    # Min price
    if query_params.get("minPrice"):
        try:
            if int(item.get("salePrice", 0)) < int(query_params["minPrice"]):
                return False
        except ValueError:
            pass

    # Max price
    if query_params.get("maxPrice"):
        try:
            if int(item.get("salePrice", 0)) > int(query_params["maxPrice"]):
                return False
        except ValueError:
            pass

    # Name ("name contains" OR-Logic)
    if query_params.get("names"):
        name_filters = [n.strip().lower() for n in query_params["names"].split(",")]
        market_name = item.get("marketName", "").lower()
        if not any(name in market_name for name in name_filters):
            return False

    # Pattern ("pattern matches" OR-Logic)
    if query_params.get("patterns"):
        try:
            patterns = [int(p.strip()) for p in query_params["patterns"].split(",")]  # List of Numbers as integer
            item_pattern = item.get("pattern")
            if item_pattern is None or item_pattern not in patterns:
                return False
        except ValueError:
            pass

    # Min wear
    if query_params.get("minWear"):
        try:
            if float(item.get("wear", 1)) < float(query_params["minWear"]):
                return False
        except ValueError:
            pass

    # Max wear
    if query_params.get("maxWear"):
        try:
            if float(item.get("wear", 0)) > float(query_params["maxWear"]):
                return False
        except ValueError:
            pass

    # Exterior
    if query_params.get("exterior"):
        exterior_value = query_params["exterior"].strip().lower()
        item_exterior = item.get("exterior", "").lower()
        if item_exterior != exterior_value:
            return False
        
    return True

'''
query_params = {
    "names": "Karambit, Butterfly",
    "minPrice": "50",
    "maxPrice": "150",
    "patterns": "100, 231, 31, 321",
    "minWear": "0.1",   # Mindest-Wear von 0.1
    "maxWear": "0.5",   # Maximal-Wear vom 0.5
    "exterior": "Well-Worn"    # Nur Well-Worn Items
}'''