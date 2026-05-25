from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from models import get_all_locations, get_location_by_name, get_today_weather, get_week_forecast
import os

app = Flask(__name__)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

@app.route("/", methods=["GET", "POST"])
def index():
    locations = get_all_locations()
    
    # Default to first location
    current_location = locations[0] if locations else None
    
    if request.method == "POST":
        search_query = request.form.get("search_query")
        if search_query:
            found_location = get_location_by_name(search_query)
            if found_location:
                current_location = found_location

    if not current_location:
        return render_template("index.html", location=None, today=None, week=[])

    today = get_today_weather(current_location["id"])
    week = get_week_forecast(current_location["id"])
    
    return render_template("index.html", location=current_location, today=today, week=week)

if __name__ == "__main__":
    from database import init_db
    init_db()
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=8501)
