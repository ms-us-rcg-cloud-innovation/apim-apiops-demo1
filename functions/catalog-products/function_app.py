import azure.functions as func
import json

app = func.FunctionApp()

PRODUCTS = [
    {"id":"p1","name":"Widget","price":9.99,"sku":"WGT-001"},
    {"id":"p2","name":"Gadget","price":19.99,"sku":"GDG-002"},
    {"id":"p3","name":"Gizmo","price":29.99,"sku":"GZM-003"},
    {"id":"p4","name":"Thingamajig","price":4.5,"sku":"TMJ-004"},
]

@app.route(route="products", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def list_products(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(json.dumps({"count": len(PRODUCTS), "products": PRODUCTS}), mimetype="application/json")

@app.route(route="products/{id}", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def get_product(req: func.HttpRequest) -> func.HttpResponse:
    pid = req.route_params.get("id")
    p = next((x for x in PRODUCTS if x["id"] == pid), None)
    if not p:
        return func.HttpResponse(json.dumps({"error":"not_found","id":pid}), status_code=404, mimetype="application/json")
    return func.HttpResponse(json.dumps(p), mimetype="application/json")
