import logging

from escpos.config import Config
from escpos.escpos import Escpos
from escpos.printer import Dummy
from flask import Flask, request

from cafe.order.Order import Order
from cafe.printer.PrintClient import PrintClient
from cafe.printer.PrintService import PrintService

# print_service = PrintService(PrintClient(Dummy()))
c = Config()
c.load("cafe/printer/config.yaml")
raw_printer: Escpos = c.printer()
print_service = PrintService(PrintClient(raw_printer))

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/health-check")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/order", methods=["POST"])
def order():
    content = request.json
    try:
        order = Order.from_dict(content)
    except KeyError as e:
        logger.error(e)
        return "Bad Request", 400
    except TypeError as e:
        logger.error(e)
        return "Bad Request", 400
    print_service.print(order)
    return "", 201
