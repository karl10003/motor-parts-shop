from flask import Flask, flash, redirect, render_template, request, url_for

from connect_db import create_tables
from inventory_service import get_all_parts, load_inventory_from_xml
from order_service import create_order, get_orders
from payment_service import get_payment_methods, validate_payment_method

app = Flask(__name__, template_folder="template")
app.secret_key = "motor-parts-shop-secret-key"


@app.before_request
def setup_database_once():
    """
    This runs once when the website starts.
    It creates database tables and loads data from inventory.xml.
    """

    if not getattr(app, "database_ready", False):
        create_tables()
        load_inventory_from_xml()
        app.database_ready = True


@app.route("/")
def home():
    """
    This displays the main website page.
    """

    search = request.args.get("search", "").strip()

    parts = get_all_parts(search)
    orders = get_orders()

    return render_template(
        "motor.html",
        parts=parts,
        orders=orders,
        payment_methods=get_payment_methods(),
        search=search
    )


@app.route("/order", methods=["POST"])
def order():
    """
    This handles the order form.
    """

    part_id = request.form.get("part_id")
    customer_name = request.form.get("customer_name", "").strip()
    quantity = request.form.get("quantity", 1)
    payment_method = request.form.get("payment_method")

    if not customer_name:
        flash("Please enter customer name.", "error")
        return redirect(url_for("home"))

    if not validate_payment_method(payment_method):
        flash("Invalid payment method.", "error")
        return redirect(url_for("home"))

    success, message = create_order(
        part_id,
        customer_name,
        quantity,
        payment_method
    )

    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)