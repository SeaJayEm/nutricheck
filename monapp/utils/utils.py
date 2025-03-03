def parse_mistral_response(response):
    products = []
    lines = response.split("\n")
    for line in lines:
        if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
            parts = line.split(", ")
            product_info = {}
            for part in parts:
                if ": " in part:  # Vérifier que la partie contient bien ": "
                    key, value = part.split(": ", 1)  # Utiliser split avec maxsplit=1
                    product_info[key.lower()] = value
            products.append(product_info)
    return products