def filter_item_single(sale, filter_params):
    """Filter a single sale against a single filter configuration"""
    if sale["eventType"] != "listed":
        return False
    
    item = sale["sale"]
    
    # Min price
    if filter_params.get("minPrice"):
        try:
            if int(item.get("salePrice", 0)) < int(filter_params["minPrice"]):
                return False
        except ValueError:
            pass
    
    # Max price
    if filter_params.get("maxPrice"):
        try:
            if int(item.get("salePrice", 0)) > int(filter_params["maxPrice"]):
                return False
        except ValueError:
            pass
    
    # Name (single name check)
    if filter_params.get("name"):
        filter_name = filter_params["name"].strip().lower()
        market_name = item.get("marketName", "").lower()
        if filter_name not in market_name:
            return False
    
    # Pattern ("pattern matches" OR-Logic)
    if filter_params.get("patterns"):
        try:
            patterns = [int(p.strip()) for p in filter_params["patterns"].split(",")]
            item_pattern = item.get("pattern")
            if item_pattern is None or item_pattern not in patterns:
                return False
        except ValueError:
            pass
    
    # Min wear
    if filter_params.get("minWear"):
        try:
            if float(item.get("wear", 1)) < float(filter_params["minWear"]):
                return False
        except ValueError:
            pass
    
    # Max wear
    if filter_params.get("maxWear"):
        try:
            if float(item.get("wear", 0)) > float(filter_params["maxWear"]):
                return False
        except ValueError:
            pass
    
    # Exterior
    if filter_params.get("exterior"):
        exterior_value = filter_params["exterior"].strip().lower()
        item_exterior = item.get("exterior", "").lower()
        if item_exterior != exterior_value:
            return False
    
    return True


def filter_item(sale, query_params):
    """Filter a sale against multiple filter configurations"""
    # Handle both old and new format
    if "filters" in query_params:
        # New format with multiple filters
        filters = query_params["filters"]
        
        # Check if sale matches ANY of the filters (OR logic between filters)
        for filter_config in filters:
            if filter_item_single(sale, filter_config):
                return True, filter_config  # Return True and the matching filter
        
        return False, None
    else:
        # Old format compatibility
        result = filter_item_single(sale, query_params)
        return result, query_params if result else None

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