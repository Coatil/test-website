from flask import Flask, render_template, request

import googlemaps
from datetime import datetime

app = Flask(__name__)
#makes Flask object

@app.route('/', methods = ["GET", "POST"])
def gfg():
    if request.method == "POST":
        location1 = request.form.get("loc1")
        location2 = request.form.get("loc2")
        location3 = request.form.get("loc3")

        gmaps = googlemaps.Client(key="AIzaSyDGzP0Xzw5hVQ7FxHtKgZgNJhoPO0KeVno")

        # geocodes the locations of the user, destination, and car
        geocode_results = gmaps.geocode(location1)
        latitude1 = geocode_results[0]["geometry"]["location"]["lat"]
        longitude1 = geocode_results[0]["geometry"]["location"]["lng"]

        geocode_results = gmaps.geocode(location2)
        latitude2 = geocode_results[0]["geometry"]["location"]["lat"]
        longitude2 = geocode_results[0]["geometry"]["location"]["lng"]

        geocode_results = gmaps.geocode(location3)
        latitude3 = geocode_results[0]["geometry"]["location"]["lat"]
        longitude3 = geocode_results[0]["geometry"]["location"]["lat"]

        # binary search algorithm that finds the pickup point where the user and driver arrives at the same time
        personDur = 0
        carDur = 1

        frontX = latitude1
        frontY = longitude1

        backX = latitude2
        backY = longitude2

        middleX = 0.0
        middleY = 0.0

        isFound = True
        while isFound:
            # finds the potential pickup point by dividing the journey in halves
            middleX = (frontX + backX) / 2.0
            middleY = (frontY + backY) / 2.0
            locBlue = (middleX, middleY)

            # reverse geocodes the potential pickup point to a Place ID
            results = gmaps.reverse_geocode(locBlue)
            locBlueP = "place_id:" + results[0]["place_id"]

            # finds the duration between the user and the Place ID
            distance_matrix_results = gmaps.distance_matrix(location1, locBlueP, mode="walking", language="en", avoid=None,
            units="metric", departure_time=datetime.utcnow(), arrival_time=None, transit_mode="rail",
            transit_routing_preference="fewer_transfers", traffic_model="best_guess", region=".ca" )
            personDur = distance_matrix_results["rows"][0]["elements"][0]["duration"]["value"]

            # finds the duration between the car and the Place ID
            results = gmaps.distance_matrix(location3, locBlueP, mode="driving", language="en", avoid=None, units="metric",
            departure_time=datetime.utcnow(), arrival_time=None, transit_mode="rail",
            transit_routing_preference="fewer_transfers", traffic_model="pessimistic", region=".ca" )
            carDur = results["rows"][0]["elements"][0]["duration"]["value"]

            # finds whether the durations are close enough
            if personDur - 150 <= carDur and carDur <= personDur + 150:
                    isFound = False
            # if not, changes the variables appropriately to find the new potential pickup point
            elif personDur > carDur:
                    backX = middleX
                    backY = middleY
            elif carDur > personDur:
                    frontX = middleX
                    frontY = middleY

        reverse_geocode_results = gmaps.reverse_geocode((middleX, middleY))
        pickup_address = reverse_geocode_results[0]["formatted_address"]
        seconds = (personDur + carDur) / 2
        discount = round(seconds * 0.01, 2)
        url_geocode = gmaps.geocode(pickup_address)
        url_geocode_lat = str(url_geocode[0]["geometry"]["location"]["lat"])
        url_geocode_lng = str(url_geocode[0]["geometry"]["location"]["lng"])

        latitude1 = str(latitude1)
        longitude1 = str(longitude1)
        midX = (float(url_geocode_lat) + float(latitude1)) / 2.0
        midY = (float(url_geocode_lng) + float(longitude1)) / 2.0
        midReverse = gmaps.reverse_geocode((midX, midY))
        midReverseResults = midReverse[0]["formatted_address"]
        midReverseResultsAddress = midReverseResults.replace(" ","+")
        zoom = '15'
        if seconds >= 600 and seconds <= 1900:
              zoom = '14'
        if seconds >= 1900:
              zoom = '13'
        url = "https://maps.googleapis.com/maps/api/staticmap?center=" + midReverseResultsAddress + "&zoom=" + zoom + "&size=600x300&maptype=roadmap&markers=color:red%7Clabel:B%7C" + url_geocode_lat + "," + url_geocode_lng + "&markers=color:black%7Clabel:A%7C" + latitude1 + "," + longitude1 + "&key=" + API_KEY
        return render_template("index.html", pickup_address=pickup_address, seconds=seconds, discount=discount, url=url)
    return render_template("form.html")

if __name__ == '__main__':
    app.run()

