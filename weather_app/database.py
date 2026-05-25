import sqlite3
import requests
from datetime import datetime

DB_NAME = 'weather.db'

def get_connection():
    return sqlite3.connect(f'db/{DB_NAME}')

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Drop existing tables to recreate with new schema
    cursor.execute('DROP TABLE IF EXISTS weather_week')
    cursor.execute('DROP TABLE IF EXISTS weather_today')
    cursor.execute('DROP TABLE IF EXISTS locations')

    cursor.execute('''
        CREATE TABLE locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE weather_today (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER,
            temperature REAL,
            condition TEXT,
            status_icon TEXT,
            rain_chance INTEGER,
            date_time TEXT,
            humidity INTEGER,
            wind_speed REAL,
            air_quality TEXT,
            uv_index INTEGER,
            FOREIGN KEY (location_id) REFERENCES locations (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE weather_week (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER,
            day_name TEXT,
            date_text TEXT,
            temp_min REAL,
            temp_max REAL,
            status_icon TEXT,
            FOREIGN KEY (location_id) REFERENCES locations (id)
        )
    ''')

    conn.commit()
    conn.close()
    seed_data()

def seed_data():  
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM locations")
    location_amount = cursor.fetchone()[0]
    print(f"Số lượng location: {location_amount}")
    if location_amount == 0:
        # Locations
        cities = ["Ho Chi Minh City", "Ha Noi", "Da Nang", "Hai Phong"]
        cursor.executemany("INSERT INTO locations (name) VALUES (?)", [(city,) for city in cities])
        
        API_KEY = '630788f4219f13760737161cdbfb4a53' 
        
        for i, city in enumerate(cities, start=1):
            url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse data
                    temp = round(data['main']['temp'] - 273.15, 1) # Convert Kelvin to Celsius
                    condition = data['weather'][0]['main']
                    status_icon = data['weather'][0]['icon'] # API icon like '04n'
                    humidity = data['main']['humidity']
                    wind_speed = data['wind']['speed']
                    dt = data['dt']
                    date_time = datetime.fromtimestamp(dt).strftime('%A, %H:%M')
                    
                    cursor.execute("""
                        INSERT INTO weather_today (location_id, temperature, condition, status_icon, rain_chance, 
                                   date_time, humidity, wind_speed, air_quality, uv_index)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (i, temp, condition, status_icon, 0, date_time, humidity, wind_speed, "N/A", 0))
                else:
                    raise Exception(f"API failed with status {response.status_code}")
            except Exception as e:
                # Fallback to hardcoded data if API fails or key is invalid
                fallback_data = {
                    "Ho Chi Minh City": (32.5, "Most Cloudy", "cloudy_sun", 30, "Monday, 16:00", 75, 12.5, "Good", 6),
                    "Ha Noi": (28.0, "Rainy", "rain", 80, "Monday, 16:00", 85, 15.0, "Moderate", 3),
                    "Da Nang": (30.0, "Sunny", "sun", 10, "Monday, 16:00", 60, 8.0, "Good", 9),
                    "Hai Phong": (30.0, "Sunny", "sun", 10, "Monday, 16:00", 60, 8.0, "Good", 9)
                }
                data = fallback_data[city]
                cursor.execute("""
                    INSERT INTO weather_today (location_id, temperature, condition, status_icon, rain_chance, 
                               date_time, humidity, wind_speed, air_quality, uv_index)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (i, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]))
        
        # Week Weather for HCMC (location 1)
        week_hcm = [
            (1, "Mon", "12 Oct", 26, 32, "cloudy_sun"),
            (1, "Tue", "13 Oct", 25, 30, "rain"),
            (1, "Wed", "14 Oct", 26, 33, "sun"),
            (1, "Thu", "15 Oct", 27, 34, "sun"),
            (1, "Fri", "16 Oct", 26, 31, "cloudy_sun"),
            (1, "Sat", "17 Oct", 25, 29, "rain"),
            (1, "Sun", "18 Oct", 26, 32, "cloudy")
        ]
        
        # Week Weather for Ha Noi (location 2)
        week_hn = [
            (2, "Mon", "12 Oct", 22, 28, "rain"),
            (2, "Tue", "13 Oct", 21, 26, "rain"),
            (2, "Wed", "14 Oct", 23, 29, "cloudy"),
            (2, "Thu", "15 Oct", 24, 30, "cloudy_sun"),
            (2, "Fri", "16 Oct", 22, 27, "rain"),
            (2, "Sat", "17 Oct", 23, 28, "cloudy"),
            (2, "Sun", "18 Oct", 24, 30, "sun")
        ]

        # Week Weather for Da Nang (location 3)
        week_dn = [
            (3, "Mon", "12 Oct", 25, 30, "sun"),
            (3, "Tue", "13 Oct", 26, 31, "sun"),
            (3, "Wed", "14 Oct", 25, 29, "cloudy_sun"),
            (3, "Thu", "15 Oct", 26, 30, "cloudy_sun"),
            (3, "Fri", "16 Oct", 24, 28, "rain"),
            (3, "Sat", "17 Oct", 25, 29, "rain"),
            (3, "Sun", "18 Oct", 26, 31, "sun")
        ]
        
        cursor.executemany("""INSERT INTO weather_week (location_id, day_name, date_text, temp_min, temp_max, status_icon) 
                           VALUES (?, ?, ?, ?, ?, ?)""", week_hcm + week_hn + week_dn)
        
    conn.commit()
    conn.close()
