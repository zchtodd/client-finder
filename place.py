import os
import csv
import time
import requests

lat = 28.5383
lng = -81.3792


def get_place_rank(place_id, keyword):
    place_results = requests.get(
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
        params={
            "key": os.environ["GOOGLE_MAPS_API_KEY"],
            "keyword": keyword,
            "location": "{},{}".format(lat, lng),
            "radius": 50000,
        },
    ).json()

    results = place_results["results"]

    while place_results.get("next_page_token"):
        time.sleep(2)

        place_results = requests.get(
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
            params={
                "key": os.environ["GOOGLE_MAPS_API_KEY"],
                "keyword": keyword,
                "location": "{},{}".format(lat, lng),
                "radius": 50000,
                "pagetoken": place_results["next_page_token"],
            },
        ).json()

        results += place_results["results"]

    for i, row in enumerate(results, 1):
        if row["place_id"] == place_id:
            return i
    return "Not ranking"


def get_place_details(place_id):
    result = requests.get(
        "https://maps.googleapis.com/maps/api/place/details/json",
        params={
            "key": os.environ["GOOGLE_MAPS_API_KEY"],
            "place_id": place_id,
            "fields": "name,formatted_address,url,website",
        },
    ).json()

    return result["result"]


def place_search(name):
    place_details = requests.get(
        "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
        params={
            "key": os.environ["GOOGLE_MAPS_API_KEY"],
            "input": name,
            "inputtype": "textquery",
            "locationbias": "point:{},{}".format(lat, lng),
        },
    ).json()

    for candidate in place_details["candidates"]:
        yield candidate["place_id"]


writer = csv.writer(
    open("results.csv", "w"), dialect="excel", quoting=csv.QUOTE_NONNUMERIC
)
writer.writerow(["Name", "Address", "Search Term", "Local Rank", "GMB URL", "Website"])

names = set()
with open("place_names.csv", "r") as f:
    for line in f:
        name, term = line.strip().split("\t")

        if name in names:
            continue

        names.add(name)

        for place_id in place_search(name):
            result = get_place_details(place_id)
            rank = get_place_rank(place_id, term)

            writer.writerow(
                [
                    result["name"],
                    result["formatted_address"],
                    term,
                    str(rank),
                    result["url"],
                    result.get("website", ""),
                ]
            )
