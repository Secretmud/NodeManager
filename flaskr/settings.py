from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.auth import login_required
from flaskr.db import get_db
bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/setup", methods=("GET", "POST"))
@login_required
def setup():
    db = get_db()

    customers = db.execute("SELECT * FROM customers").fetchall()
    print(customers)

    return render_template("settings/setup.html", customers=customers)


@bp.route("/setup/customer", methods=("GET", "POST"))
@login_required
def add_customer():
    db = get_db()
    if request.method == "POST":
        company_name = request.form["company"]
        company_id = request.form["id"]

        db.execute("INSERT INTO customers (id, name) VALUES (?, ?)",
                    (company_id, company_name))
        db.commit()


    return render_template("settings/customer.html")


@bp.route("/setup/ip", methods=("GET", "POST"))
@login_required
def add_ip():
    db = get_db()
    customers = db.execute("SELECT * FROM customers").fetchall()
    if request.method == "POST":
        file =  request.form["ip_file"]
        ip = request.form["ip"]
        customer = request.form["customer"]
        if file is not None:
            with open(file, "r") as f:
                ips = f.readall()
            import datetime 
            db.execute("INSTERT INTO machine (lookup_id, cust_id, ip, created, last_attack, online) VALUES (?,?,?,?,?,?)",
                      (session["user_id"], customer, ip, datetime.now(), datetime.now(), True))

    return render_template("settings/ip.html", customers=customers)