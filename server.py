from flask import Flask, render_template, request, flash, redirect, session
import requests
import googlemaps
import os

app = Flask(__name__)
app.secret_key = "131fd7d8781ee66aa8fae53123ab046b"

GMAPS_API_KEY = os.environ['GMAPS_API_KEY']
REI_API_KEY = os.environ['REI_API_KEY']
REI_API_URL = "https://www.hikingproject.com/data/get-trails"
gmaps = googlemaps.Client(key=GMAPS_API_KEY)
difficulty_level = {
    "green": "Easy",
    "greenBlue": "Easy/Moderate",
    "blue": "Moderate",
    "blueBlack": "Moderate/Difficult",
    "black": "Difficult",
}


@app.route("/")
def index():
    """Show homepage"""

    return render_template("homepage.html")


@app.route("/show-trails")
def show_trails():
    """
    1. Get latitude, longitude from user-specified zipcode (Google Maps API)
    2. Get list of trails based on user's location and desired radius (REI API)
    3. Keep maxResults as 500 and sort based on distance
    """

    # Get user specified values from the form
    radius = request.args.get("radius")
    zipcode = request.args.get("zipcode")

    # Validate user input in radius field
    if not (radius.isdigit() and (0 < int(radius) < 200)):
        flash("Please enter a distance less than 200 miles")
        return redirect("/")

    radius = int(radius)

    # Call Google Maps API to geocode the enetered address/zipcode
    result = gmaps.geocode(zipcode)

    # Generate a flash message if user-entered address/zipcode is not valid
    if len(result) == 0:
        flash("Please enter a valid address or zipcode")
        return redirect("/")

    # Extract the location (lat/lng) from the API result
    location = result[0]['geometry']['location']

    # Call REI's Hiking API to display trail results
    payload = {
        'key': REI_API_KEY,
        'lat': location['lat'],
        'lon': location['lng'],
        'maxDistance': radius,
        'maxResults': 5,
        'sort': 'distance'
    }

    response = requests.get(REI_API_URL, params=payload)

    # Handle any errors in response from the API
    try:
        response.raise_for_status()
    except Exception as e:
        return render_template("500.html", error=e)

    # Get the JSON from the API response
    hike_trails = response.json()

    hike_trails_json = response.text

    num_results = len(hike_trails['trails'])

    # # Extract trail information from the hike_trails dict
    # for trail in hike_trails['trails']:
    #     name = trail.get('name')
    #     url = trail.get('url')
    #     location = trail.get('location')
    #     latitude = trail.get('latitude')
    #     longitude = trail.get('longitude')
    #     summary = trail.get('summary')
    #     length = trail.get('length')
    #     ascent = trail.get('ascent')
    #     descent = trail.get('descent')
    #     diff_color = trail.get('difficulty')
    #     status = trail.get('conditionStatus')
    #     details = trail.get('conditionDetails')

    # if diff_color in diff_level:
    #     difficulty = diff_level[diff_color]
    # else:
    #     "No corresponding difficulty level found."

    # Pass information to HTML to show map and a list of trails.
    # Location and difficulty_levels are passed as a dicts.
    return render_template("show_trails.html",
                           radius=radius,
                           location=location,
                           api_key=GMAPS_API_KEY,
                           hike_trails=hike_trails,
                           trail_json=hike_trails_json,
                           difficulty_level=difficulty_level,
                           num_results=num_results)

#######################################################

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    # connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
