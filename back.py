# do pip install -U googlemaps in the terminal
from datetime import datetime
import googlemaps

gmaps = googlemaps.Client(key="AIzaSyDGzP0Xzw5hVQ7FxHtKgZgNJhoPO0KeVno")

# geocodes the locations of the user, destination, and car
location1 = "1455 Glen Abbey Gate, Oakville, Canada"
geocode_results = gmaps.geocode(location1)
latitude1 = geocode_results[0]["geometry"]["location"]["lat"]
longitude1 = geocode_results[0]["geometry"]["location"]["lng"]

location2 = "587 Third Line, Oakville, Canada"
geocode_results = gmaps.geocode(location2)
latitude2 = geocode_results[0]["geometry"]["location"]["lat"]
longitude2 = geocode_results[0]["geometry"]["location"]["lng"]

location3 = "1330 Montclair Dr, Oakville, Canada"
geocode_results = gmaps.geocode(location3)
latitude3 = geocode_results[0]["geometry"]["location"]["lat"]
longitude3 = geocode_results[0]["geometry"]["location"]["lat"]

# finds the pickup point where the user and driver arrives at the same time
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
    distance_matrix_results = gmaps.distance_matrix(location1, locBlueP, mode="walking", language="en", avoid=None, units="metric", departure_time=datetime.utcnow(), arrival_time=None, transit_mode="rail", transit_routing_preference="fewer_transfers", traffic_model="best_guess", region=".ca")
    personDur = distance_matrix_results["rows"][0]["elements"][0]["duration"]["value"]

    # finds the duration between the car and the Place ID
    results = gmaps.distance_matrix(location3, locBlueP, mode="driving", language="en", avoid=None, units="metric", departure_time=datetime.utcnow(), arrival_time=None, transit_mode="rail", transit_routing_preference="fewer_transfers", traffic_model="pessimistic", region=".ca")
    carDur = results["rows"][0]["elements"][0]["duration"]["value"]

    # finds whether the durations are close enough
    if personDur - 150 <= carDur and carDur <= personDur + 150:
        isFound = False
        print("The pickup point is about", personDur +
              carDur / 2, "seconds away from the person.")
    # if not, changes the variables appropriately to find the new potential pickup point
    elif personDur > carDur:
        backX = middleX
        backY = middleY
    elif carDur > personDur:
        frontX = middleX
        frontY = middleY

# prints the pickup point
print("The person and the driver needs to meet at: ", middleX, middleY)
address = gmaps.reverse_geocode((middleX, middleY))
print("The person and the driver needs to meet at: ",address[0]["formatted_address"])
