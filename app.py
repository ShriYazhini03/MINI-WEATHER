from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

OPENWEATHER_API_KEY = "71b16a606188a50f8c7de5b8d949c1a2"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/weather")
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    city = request.args.get("city")

    try:
        if lat and lon:
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        elif city:
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        else:
            return jsonify({"error": "No location provided"}), 400

        response = requests.get(url)
        data = response.json()

        if data.get("cod") != "200":
            return jsonify({"error": "Location not found"}), 404

        location = data['city']['name']
        forecast = {}

        for entry in data['list']:
            date = entry['dt_txt'].split(" ")[0]
            if date not in forecast:
                forecast[date] = {
                    "temp": entry['main']['temp'],
                    "condition": entry['weather'][0]['main'],
                    "humidity": entry['main']['humidity'],
                    "icon": entry['weather'][0]['icon'],
                    "count": 1
                }
            else:
                forecast[date]['temp'] += entry['main']['temp']
                forecast[date]['humidity'] += entry['main']['humidity']
                forecast[date]['count'] += 1

        result = []
        for i, (date, values) in enumerate(forecast.items()):
            if i >= 5:
                break
            result.append({
                "date": date,
                "temp": round(values['temp'] / values['count'], 1),
                "humidity": round(values['humidity'] / values['count'], 1),
                "condition": values['condition'],
                "icon": values['icon']
            })

        return jsonify({"city": location, "forecast": result})

    except Exception as e:
        return jsonify({"error": "Something went wrong"}), 500

if __name__ == "__main__":
    app.run(debug=True)
