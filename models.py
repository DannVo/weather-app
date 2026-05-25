from database import get_connection

def get_all_locations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM locations")
    locations = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1]} for row in locations]

def get_location_by_name(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM locations WHERE REPLACE(name, ' ', '') LIKE ?", ('%' + name.replace(' ', '') + '%',))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1]}
    return None

def get_today_weather(location_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT temperature, condition, status_icon, rain_chance, date_time, humidity, wind_speed, air_quality, uv_index
        FROM weather_today WHERE location_id = ?
    """, (location_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        status_icon = row[2]
        
        # Map API icon to template icon
        icon_mapping = {
            '01': 'sun',
            '02': 'cloudy_sun',
            '03': 'cloudy',
            '04': 'cloudy',
            '09': 'rain',
            '10': 'rain',
            '11': 'rain',
            '13': 'rain',
            '50': 'cloudy'
        }
        
        for key, value in icon_mapping.items():
            if status_icon and status_icon.startswith(key):
                status_icon = value
                break
                
        return {
            "temperature": row[0],
            "condition": row[1],
            "status_icon": status_icon,
            "rain_chance": row[3],
            "date_time": row[4],
            "humidity": row[5],
            "wind_speed": row[6],
            "air_quality": row[7],
            "uv_index": row[8]
        }
    return None

def get_week_forecast(location_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT day_name, date_text, temp_min, temp_max, status_icon
        FROM weather_week WHERE location_id = ? ORDER BY id ASC
    """, (location_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{
        "day_name": row[0],
        "date_text": row[1],
        "temp_min": row[2],
        "temp_max": row[3],
        "status_icon": row[4]
    } for row in rows]
