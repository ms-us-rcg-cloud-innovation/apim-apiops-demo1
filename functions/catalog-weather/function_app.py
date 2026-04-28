import azure.functions as func
import json, random

app = func.FunctionApp()

@app.route(route="weather/{city}", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def get_weather(req: func.HttpRequest) -> func.HttpResponse:
    city = req.route_params.get("city")
    body = {
        "city": city,
        "tempC": round(random.uniform(-5, 35), 1),
        "condition": random.choice(["Sunny","Cloudy","Rainy","Snowy","Windy"]),
        "humidity": random.randint(20, 95),
    }
    return func.HttpResponse(json.dumps(body), mimetype="application/json")
