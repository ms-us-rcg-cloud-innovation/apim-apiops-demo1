import azure.functions as func
import json, uuid, datetime

app = func.FunctionApp()

ORDERS = [
    {"id":"o1001","customer":"alice","total":29.98,"status":"shipped"},
    {"id":"o1002","customer":"bob","total":54.49,"status":"processing"},
    {"id":"o1003","customer":"carol","total":129.97,"status":"delivered"},
]

@app.route(route="orders", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def list_orders(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(json.dumps({"count": len(ORDERS), "orders": ORDERS}), mimetype="application/json")

@app.route(route="orders", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def create_order(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except Exception:
        body = {}
    new = {
        "id": "o" + uuid.uuid4().hex[:6],
        "customer": body.get("customer", "anonymous"),
        "total": body.get("total", 0),
        "status": "pending",
        "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
    }
    return func.HttpResponse(json.dumps(new), status_code=201, mimetype="application/json")
