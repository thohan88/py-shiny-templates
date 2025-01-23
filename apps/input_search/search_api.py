import requests
import json

def get_search_result_api(query):
    url = "https://ws.geonorge.no/adresser/v1/sok"
    params = {
        "sok": query if query else "Oslo",
        "asciiKompatibel": "true",
    }

    response = requests.get(url, params=params)
    results = response.json()

    choices_dict = [
        {
            # This is a hackish way to provide all needed info into the
            # selected value (input.search_x()). This is fine to keep it 
            # simple as the other example (database) shows how to query for 
            # additional information based on a single returned value (city).
            "value": json.dumps(
                {
                    "addressText": address["adressetekst"],
                    "zipCode": address["postnummer"],
                    "zipName": address["poststed"].title(),
                }
            ),
            "label": address["adressetekst"],
            "addressName": address["adressenavn"],
            "addressNumber": address["nummer"],
            "addressLetter": address["bokstav"],
            "zipCode": address["postnummer"],
            "zipName": address["poststed"].title(),
            "municipality": address["kommunenavn"].title(),
        }
        for address in results["adresser"]
    ]
    choices_dict.insert(0, {"value": None, "label": "", "optGroup": None})

    return choices_dict
