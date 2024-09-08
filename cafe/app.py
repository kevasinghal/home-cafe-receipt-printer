import datetime
import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from escpos.config import Config
from escpos.escpos import Escpos
from escpos.printer import Dummy
from flask import Flask, request
from flask_cors import CORS

from cafe.order.Order import Order
from cafe.printer.PrintClient import PrintClient
from cafe.printer.PrintService import PrintService

load_dotenv()

raw_printer: Escpos
if os.getenv("PRINTER") == "sidewalk":
    c = Config()
    c.load("cafe/printer/config.yaml")
    raw_printer = c.printer()
else:
    raw_printer = Dummy()

print_client = PrintClient(raw_printer)
print_service = PrintService(print_client)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route("/health-check")
def hello_world():
    return "Hello, World!"


@app.route("/order", methods=["POST"])
def order():
    logger.info(f"Request: {request.data}")
    content = request.json
    try:
        order = Order.from_dict(content)
        logger.info(f"Order: {order}")
    except KeyError as e:
        logger.error(e)
        return "Bad Request", 400
    except TypeError as e:
        logger.error(e)
        return "Bad Request", 400
    print_service.print(order)
    return "", 201


@app.route("/orders", methods=["GET"])
def get_orders():
    def default(something: Any) -> Any:
        if isinstance(something, datetime.datetime):
            return something.isoformat()

        return json.dumps(something)

    return json.dumps(print_service.orders, default=default), 200
