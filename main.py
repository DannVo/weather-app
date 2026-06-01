import streamlit as st
import streamlit.components.v1 as components
import os
import base64
from database import init_db, DB_NAME
from models import get_all_locations, get_location_by_name, get_today_weather, get_week_forecast

# Ensure database is initialized before launching the app
db_path = f'db/{DB_NAME}'
if not os.path.exists(db_path):
    init_db()

# Set up page configurations
st.set_page_config(
    page_title="Weather App",
    page_icon="🌤️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Extract query params in a robust, backward-compatible way
search_query = ""
if hasattr(st, "query_params"):
    search_query = st.query_params.get("search_query", "")
    if isinstance(search_query, list) and len(search_query) > 0:
        search_query = search_query[0]
else:
    try:
        params = st.experimental_get_query_params()
        search_query = params.get("search_query", [""])[0]
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Helper to read local images as base64 to embed in HTML
def get_image_base64(filename):
    path = os.path.join(CURRENT_DIR, "images", filename)
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    return ""

# Fetch city locations
locations = get_all_locations()
current_location = locations[0] if locations else None

if search_query:
    found_location = get_location_by_name(search_query)
    if found_location:
        current_location = found_location
    else:
        current_location = None

# Query weather info for the current location
if current_location:
    today = get_today_weather(current_location["id"])
    week = get_week_forecast(current_location["id"])
else:
    today = None
    week = []

# Base64 icons dictionary
icons = {
    "clouds": get_image_base64("clouds.png"),
    "sun": get_image_base64("sun.png"),
    "heavy_rainy": get_image_base64("heavy_rainy.png"),
    "humidity": get_image_base64("humidity.png"),
    "rainy_day": get_image_base64("rainy-day.png"),
    "temperature": get_image_base64("temperature.png")
}

# Determine today's main icon
main_icon_b64 = icons["sun"]
if today:
    if today["status_icon"] == 'cloudy_sun':
        main_icon_b64 = icons["clouds"]
    elif today["status_icon"] == 'sun':
        main_icon_b64 = icons["sun"]
    elif today["status_icon"] == 'rain':
        main_icon_b64 = icons["heavy_rainy"]
    elif today["status_icon"] == 'cloudy':
        main_icon_b64 = icons["clouds"]

# Generate week forecast cards HTML
week_cards_html = ""
for day in week:
    week_icon_b64 = icons["sun"]
    if day["status_icon"] == 'cloudy_sun':
        week_icon_b64 = icons["clouds"]
    elif day["status_icon"] == 'sun':
        week_icon_b64 = icons["sun"]
    elif day["status_icon"] == 'rain':
        week_icon_b64 = icons["rainy_day"]
    elif day["status_icon"] == 'cloudy':
        week_icon_b64 = icons["clouds"]
        
    week_cards_html += f"""
    <div class="card week-card">
        <div class="week-day">{day['day_name']}</div>
        <div class="week-date">{day['date_text']}</div>
        <div class="week-icon">
            <img src="data:image/png;base64,{week_icon_b64}" class="week-img-icon" alt="Status" />
        </div>
        <div class="week-temp">{day['temp_min']}°/{day['temp_max']}°</div>
    </div>
    """
if week:
    week_cards_html += '<div class="card empty"></div>'

# Build inner HTML depending on location status
if current_location and today:
    content_html = f"""
    <!-- LEFT PANEL -->
    <div class="left-panel">
        <form action="" method="GET" class="search-form" target="_parent">
            <div class="search-bar">
                <button type="submit">&#128269;</button>
                <input type="text" name="search_query" placeholder="Search for places..." value="{search_query}" required />
            </div>
        </form>
        
        <div class="location-badge">{current_location['name']}</div>
        
        <div class="weather-icon-container">
            <img src="data:image/png;base64,{main_icon_b64}" alt="Weather" class="main-weather-img" />
        </div>
        
        <div class="temp-badge">{today['temperature']}°C</div>
        <div class="time-badge">{today['date_time']}</div>
    </div>

    <!-- RIGHT PANEL -->
    <div class="right-panel">
        <div class="tabs">
            <div id="tab-today" class="tab active" onclick="switchTab('today')">Today</div>
            <div id="tab-week" class="tab" onclick="switchTab('week')">Week</div>
        </div>

        <!-- TODAY VIEW -->
        <div id="view-today" class="view active-view">
            <div class="weather-details">
                <div class="detail-badge">
                    <img src="data:image/png;base64,{icons['clouds']}" style="width: 22px; height: 22px; object-fit: contain;">
                    {today['condition']}
                </div>
                <div class="detail-badge">
                    <img src="data:image/png;base64,{icons['rainy_day']}" style="width: 22px; height: 22px; object-fit: contain;">
                    Rain {today['rain_chance']}%
                </div>
            </div>
            
            <div class="grid-2x2">
                <div class="card detail-card">
                    <img src="data:image/png;base64,{icons['humidity']}" class="detail-img-icon" alt="Humidity">
                    <span class="detail-title">Humidity</span>
                    <span class="detail-value">{today['humidity']}%</span>
                </div>
                <div class="card detail-card">
                    <span class="detail-emoji-icon">💨</span>
                    <span class="detail-title">Wind Speed</span>
                    <span class="detail-value">{today['wind_speed']} km/h</span>
                </div>
                <div class="card detail-card">
                    <span class="detail-emoji-icon">🍃</span>
                    <span class="detail-title">Air Quality</span>
                    <span class="detail-value">{today['air_quality']}</span>
                </div>
                <div class="card detail-card">
                    <img src="data:image/png;base64,{icons['temperature']}" class="detail-img-icon" alt="Feels Like">
                    <span class="detail-title">Feels Like</span>
                    <span class="detail-value">{today['temperature'] + 1.5}°C</span>
                </div>
            </div>
        </div>

        <!-- WEEK VIEW -->
        <div id="view-week" class="view">
            <div class="grid-4x2">
                {week_cards_html}
            </div>
        </div>
    </div>
    """
else:
    content_html = f"""
    <div style="padding: 100px 50px; text-align: center; width: 100%; font-family: 'Kalam', cursive; display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <h2 style="font-size: 32px; color: #ff6b6b; margin-bottom: 20px;">Location not found!</h2>
        <a href="/" target="_parent" style="font-size: 22px; color: #000; text-decoration: none; font-weight: bold; border: 2.5px solid #000; padding: 8px 25px; border-radius: 12px; background: #8be3df; box-shadow: 2px 2px 0px #000; transition: transform 0.2s;">Go Back</a>
    </div>
    """

# Complete HTML page to render in iframe
html_page = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather App</title>
    <link href="https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0; padding: 0;
            display: flex; justify-content: center; align-items: center;
            height: 100vh; background-color: #f0f4f8;
            font-family: 'Kalam', cursive;
            overflow: hidden;
        }}
        .app-container {{
            width: 850px; height: 550px;
            display: flex; border-radius: 30px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.15);
            overflow: hidden; background-color: #ffffff;
            border: 2px solid #e0e0e0;
        }}
        /* LEFT PANEL */
        .left-panel {{
            width: 38%; background-color: #ffffff;
            padding: 30px 20px; display: flex; flex-direction: column;
            align-items: center; border-right: 2px solid #f0f0f0;
            position: relative;
        }}
        .search-form {{ width: 100%; margin-bottom: 25px; }}
        .search-bar {{
            width: 100%; display: flex; align-items: center;
            border: 2px solid #e0e0e0; border-radius: 12px;
            padding: 5px 15px; background-color: #fdfdfd;
            transition: border-color 0.3s;
        }}
        .search-bar:focus-within {{ border-color: #8be3df; }}
        .search-bar button {{
            background: none; border: none; font-size: 18px; color: #555;
            margin-right: 5px; cursor: pointer; padding: 0;
        }}
        .search-bar input {{
            border: none; outline: none; width: 100%;
            font-family: 'Kalam', cursive; font-size: 18px;
            color: #333; background: transparent;
        }}
        .search-bar input::placeholder {{ color: #ccc; }}
        
        .location-badge {{
            background-color: #8be3df; border: 2px solid #000;
            border-radius: 12px; padding: 6px 25px;
            font-size: 24px; font-weight: 700; margin-bottom: 15px;
            color: #000; letter-spacing: 1px; text-transform: uppercase;
            box-shadow: 2px 2px 0px #000;
        }}
        
        @keyframes float {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
            100% {{ transform: translateY(0px); }}
        }}
        
        .weather-icon-container {{
            width: 160px; height: 160px; display: flex;
            justify-content: center; align-items: center; margin-bottom: 15px;
        }}
        .main-weather-img {{
            width: 140px; height: 140px; object-fit: contain;
            animation: float 4s ease-in-out infinite;
            filter: drop-shadow(0px 10px 10px rgba(0,0,0,0.1));
        }}

        .temp-badge {{
            border: 2px solid #000; border-radius: 12px; padding: 2px 20px;
            font-size: 32px; font-weight: 700; background-color: #fff;
            margin-bottom: 15px; box-shadow: 2px 2px 0px #000;
        }}
        .time-badge {{
            border: 2px solid #000; border-radius: 15px; padding: 5px 25px;
            font-size: 18px; font-weight: 700; background-color: #fff;
            box-shadow: 2px 2px 0px #000;
        }}

        /* RIGHT PANEL */
        .right-panel {{
            width: 62%; background-color: #e8eaee;
            padding: 30px 40px; display: flex; flex-direction: column;
        }}
        .tabs {{ display: flex; gap: 30px; margin-bottom: 20px; }}
        .tab {{ font-size: 28px; color: #999; cursor: pointer; transition: all 0.3s; font-weight: 700; }}
        .tab:hover {{ color: #555; }}
        .tab.active {{
            color: #000; text-decoration: underline;
            text-decoration-thickness: 3px; text-underline-offset: 5px;
        }}
        
        .view {{ display: none; flex-direction: column; flex-grow: 1; animation: fadeIn 0.4s ease-in-out; }}
        .view.active-view {{ display: flex; }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* TODAY VIEW */
        .weather-details {{ display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }}
        .detail-badge {{
            border: 2px solid #000; border-radius: 10px; padding: 5px 15px;
            background-color: #fff; font-size: 16px; font-weight: 700;
            display: inline-flex; align-items: center; gap: 10px; width: fit-content;
            box-shadow: 2px 2px 0px #000;
        }}
        .grid-2x2 {{
            display: grid; grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr; gap: 15px; flex-grow: 1;
        }}
        .card {{ background-color: #ffffff; border-radius: 20px; width: 100%; height: 100%; }}
        
        .detail-card {{
            display: flex; flex-direction: column; justify-content: center;
            align-items: center; padding: 10px; border: 2px solid transparent;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;
        }}
        .detail-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }}
        .detail-img-icon {{ width: 45px; height: 45px; object-fit: contain; margin-bottom: 5px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }}
        .detail-emoji-icon {{ font-size: 35px; margin-bottom: 5px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }}
        .detail-title {{ font-size: 16px; color: #777; font-weight: bold; }}
        .detail-value {{ font-size: 22px; font-weight: 700; color: #000; }}

        /* WEEK VIEW */
        .grid-4x2 {{
            display: grid; grid-template-columns: repeat(4, 1fr);
            gap: 15px; flex-grow: 1; margin-top: 10px;
        }}
        .week-card {{
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            padding: 10px 5px; border: 2px solid transparent; height: 130px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05); transition: transform 0.2s;
        }}
        .week-card:hover {{
            transform: translateY(-3px);
            border: 2px solid #8be3df;
        }}
        .week-day {{ font-weight: 700; font-size: 18px; color: #000; }}
        .week-date {{ font-size: 14px; color: #888; margin-bottom: 5px; }}
        .week-img-icon {{ width: 40px; height: 40px; object-fit: contain; margin-bottom: 5px; filter: drop-shadow(0 2px 3px rgba(0,0,0,0.1)); }}
        .week-temp {{ font-size: 15px; font-weight: bold; color: #333; }}
        .grid-4x2 .empty {{ background: transparent; border: none; box-shadow: none; }}
    </style>
</head>
<body>

<div class="app-container">
    {content_html}
</div>

<script>
    function switchTab(tab) {{
        document.getElementById('tab-today').classList.remove('active');
        document.getElementById('tab-week').classList.remove('active');
        document.getElementById('view-today').classList.remove('active-view');
        document.getElementById('view-week').classList.remove('active-view');

        document.getElementById('tab-' + tab).classList.add('active');
        document.getElementById('view-' + tab).classList.add('active-view');
    }}
</script>

</body>
</html>
"""

# Style parent page to center iframe and clean Streamlit margins
st.markdown("""
<style>
    header, footer { visibility: hidden !important; }
    div[data-testid="stAppViewContainer"] {
        background-color: #f0f4f8 !important;
    }
    div.block-container {
        max-width: 900px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div[data-testid="stVerticalBlock"] {
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# Render entire page inside iframe
components.html(html_page, height=560, width=860, scrolling=False)
