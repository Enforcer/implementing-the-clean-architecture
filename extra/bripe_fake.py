from typing import Any
from uuid import uuid4

from flask import Flask, request, abort, jsonify
from marshmallow import Schema, fields, ValidationError, validate

app = Flask(__name__)


class ChargePayloadSchema(Schema):
    card_token = fields.Str(required=True)
    currency = fields.Str(required=True, validate=validate.OneOf(["USD", "PLN"]))
    amount = fields.Int(required=True)


@app.post("/api/v1/charge")
def charge() -> Any:
    if not request.is_json:
        abort(400)

    try:
        ChargePayloadSchema().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages)

    return jsonify({"charge_uuid": str(uuid4()), "success": True})


app.run(host="127.0.0.1", port=5050)
