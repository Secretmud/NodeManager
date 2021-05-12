from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from tools.find_units import *

bp = Blueprint('node', __name__)

@bp.route('/')
def index():
    db = get_db()
    nodes = get_data("active");
    return render_template('nodes/index.html', machines=nodes)

def get_data(data):
    us = UnitSearch()
    us.set_ip("192.168.1.1")
    us.set_subnet("255.255.255.0")
    active, ssh = us.parallel_calls()
    ax = UnitSearch()
    print(us.parallel_calls())
    print(ax.parallel_calls())

    if data == "active":
        return active
    elif data == "ssh":
        return ssh
    else:
        return "no data"



@bp.route('/active', methods=["GET"])
def active():
    return jsonify({"Machines": get_data("active")})

@bp.route('/ssh', methods=["GET"])
def ssh():
    return jsonify({"SSH": get_data("ssh")})


if __name__ == "__main__":
    app.run(debug = True)
