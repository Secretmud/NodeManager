import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.tools.find_units import *
from socket import gethostname

bp = Blueprint('node', __name__)


@bp.route('/')
def index():
    db = get_db()
    nodes = db.execute(
        "SELECT id, lookup_id, created, ip, last_seen FROM machine ORDER BY id DESC"
    ).fetchall()
    return render_template('nodes/index.html', posts=nodes)


def get_data():
    us = UnitSearch()
    us.set_ip("192.168.1.1")
    us.set_subnet("255.255.255.0")
    online_machines, ssh_port_open = us.parallel_calls()
    dict = {}
    i = 0
    for online in online_machines:
        ssh_enabled = True if (online in ssh_port_open) else False
        dict[i] = {"ip": online, "SSH": ssh_enabled}
        i += 1

    return json.dumps(dict)


@bp.route('/scan', methods=("GET", "POST"))
@login_required
def scan():
    if request.method == "GET":
        hosts = json.loads(get_data())
        print(hosts)
        for host in hosts:
            print(host)


    return render_template('nodes/index.html')
