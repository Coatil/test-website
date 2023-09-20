from flask import Flask, render_template, request

import googlemaps
from datetime import datetime

app = Flask(__name__)
#makes Flask object

@app.route('/', methods = ["GET", "POST"])
def gfg():
    # requests locations from HTML form 
    if request.method == "POST":
        location1 = request.form.get("loc1")
        location2 = request.form.get("loc2")
        location3 = request.form.get("loc3")
        # collects the inputs we got from our forms in the shape of POST requests

        # loads API key
        gmaps = googlemaps.Client(api_key=API_KEY)

        # geocodes the locations of the user, destination, and driver
        results = gmaps.geocode(location1)
        latitude1 = results[0]["geometry"]["location"]["lat"]
        longitude1 = results[0]["geometry"]["location"]["lng"]

        results = gmaps.geocode(location2)
        latitude2 = results[0]["geometry"]["location"]["lat"]
        longitude2 = results[0]["geometry"]["location"]["lng"]

        results = gmaps.geocode(location3)
        latitude3 = results[0]["geometry"]["location"]["lat"]
        longitude3 = results[0]["geometry"]["location"]["lat"]

        # preparing variables for the algorithm
        personDur = 0
        driverDur = 1

        frontX = latitude1
        frontY = longitude1

        backX = latitude2
        backY = longitude2

        middleX = 0.0
        middleY = 0.0

        # algorithm that finds the pickup point
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
            results = gmaps.distance_matrix(location1, locBlueP, mode="walking", language="en", avoid=None,
            units="metric", departure_time=datetime.utcnow(), arrival_time=None, transit_mode="rail",
            transit_routing_preference="fewer_transfers", traffic_model="best_guess", region=".ca" )
            personDur = results["rows"][0]["elements"][0]["duration"]["value"]

            # finds the duration between the driver and the Place ID
            results = gmaps.distance_matrix(location3, locBlueP, mode="driving", language="en", avoid=None, units="metric",
            departure_time=datetime.utcnow(), arrival_time=None, transit_mode="rail",
            transit_routing_preference="fewer_transfers", traffic_model="pessimistic", region=".ca" )
            driverDur = results["rows"][0]["elements"][0]["duration"]["value"]

            # finds whether the durations are close enough
            if personDur - 150 <= driverDur and driverDur <= personDur + 150:
                    isFound = False
            # if not, changes the variables appropriately to find the new potential pickup point
            elif personDur > driverDur:
                    backX = middleX
                    backY = middleY
            elif driverDur > personDur:
                    frontX = middleX
                    frontY = middleY

        # reverse geocodes the pickup point into an address
        results = gmaps.reverse_geocode((middleX, middleY))
        pickupAddress = results[0]["formatted_address"]

        # calculates the discount
        seconds = (personDur + driverDur) / 2
        discount = round(seconds * 0.01, 2)

        # geocodes the pickup address into latitudes and longitudes
        URLGeocode = gmaps.geocode(pickupAddress)
        URLGeocodeLat = str(URLGeocode[0]["geometry"]["location"]["lat"])
        URLGeocodeLng = str(URLGeocode[0]["geometry"]["location"]["lng"])

        # prepares variables to be concatenated into static map url
        latitude1 = str(latitude1)
        longitude1 = str(longitude1)

        # the latitude and longitude of the center of the map
        midX = (float(URLGeocodeLat) + float(latitude1)) / 2.0
        midY = (float(URLGeocodeLng) + float(longitude1)) / 2.0

        # finds the address of the center of the map
        midReverse = gmaps.reverse_geocode((midX, midY))
        midReverseResults = midReverse[0]["formatted_address"]
        midReverseResultsAddress = midReverseResults.replace(" ","+")

        # prepares custom zoom levels 
        zoom = '15'
        if seconds >= 600 and seconds <= 1900:
              zoom = '14'
        if seconds >= 1900:
              zoom = '13'
        # the url for the static map, it concatenates multiple strings in order to have a custom map
        url = "https://maps.googleapis.com/maps/api/staticmap?center=" + midReverseResultsAddress + "&zoom=" + zoom + "&size=600x300&maptype=roadmap&markers=color:red%7Clabel:B%7C" + URLGeocodeLat + "," + URLGeocodeLng + "&markers=color:black%7Clabel:A%7C" + latitude1 + "," + longitude1 + "&key=" + API_KEY

        # renders the results page
        return render_template("index.html", pickup_address=pickup_address, seconds=seconds, discount=discount, url=url)
    # renders the landing page
    return render_template("form.html")

if __name__ == '__main__':
    app.run()
