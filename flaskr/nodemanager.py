import json

import celery
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.tools.find_units import *
from datetime import datetime

bp = Blueprint('node', __name__)


@bp.route('/')
def index():
    db = get_db()
    nodes = db.execute(
        "SELECT * FROM machine LEFT OUTER JOIN ports ON machine.id=ports.ip_id"
    ).fetchall()
    return render_template('nodes/index.html', machines=nodes)


def get_data():
    us = UnitSearch()
    us.set_ip("192.168.1.1")
    us.set_subnet("255.255.255.0")
    online_machines, ssh_port_open = us.parallel_calls()
    dict = {}
    i = 0
    for online in online_machines:
        ssh_enabled = True if (online in ssh_port_open) else False
        dict[i] = {"ip": online, "ssh": ssh_enabled}
        i += 1

    return json.dumps(dict)


@bp.route('/scan', methods=("GET", "POST"))
@login_required
def scan():
    if request.method == "GET":
        db = get_db()
        hosts = json.loads(get_data())
        for host in hosts:
            ip = hosts[host]['ip']
            ssh = hosts[host]['ssh']
            check = db.execute("SELECT id FROM machine WHERE ip=?", (ip,)).fetchone()
            if check is None:
                db.execute("INSERT INTO machine (lookup_id, created, ip, last_seen) VALUES (?, ?, ?, ?)",
                           (session['user_id'], datetime.now(), ip, datetime.now()))
                db.commit()
            check_ssh = db.execute("SELECT id FROM ports WHERE "
                                   "ip_id=(SELECT machine.id FROM machine WHERE machine.ip=?)",
                                   (ip,)).fetchone()
            if check_ssh is None:
                db.execute("INSERT INTO ports (port, ip_id) VALUES "
                           "(?, (SELECT machine.id FROM machine WHERE machine.ip=?))",
                           (ssh, ip))
                db.commit()

            if check is not None:
                db.execute("UPDATE machine SET last_seen = ? WHERE ip=?",
                           (datetime.now(), ip))
                db.commit()
            if check_ssh is not None:
                db.execute("UPDATE ports SET port = ? WHERE"
                           " ip_id=(SELECT machine.id FROM machine WHERE machine.ip=?)",
                           (ssh, ip))
                db.commit()

    nodes = db.execute(
        "SELECT * FROM machine LEFT OUTER JOIN ports ON machine.id=ports.ip_id"
    ).fetchall()

    return render_template('nodes/index.html', machines=nodes)


@bp.route('/<string:ip>/update', methods=("GET", "POST"))
@login_required
def scan_single(ip):
    db = get_db()
    check = db.execute("SELECT id FROM machine WHERE ip=?", (ip,)).fetchone()

    if check is not None:
        us = UnitSearch()
        ip_check = us.active_machines(ip)
        ssh_check = True if (us.locate_ssh(ip) == ip) else False
        db.execute("UPDATE machine SET last_seen = ? WHERE ip=?",
                   (datetime.now(), ip_check))
        db.execute("UPDATE ports SET port = ? WHERE"
                   " ip_id=(SELECT machine.id FROM machine WHERE machine.ip=?)",
                   (ssh_check, ip_check))
        db.commit()

    else:
        abort(404, "The requested ip is not availabel")

    nodes = db.execute(
        "SELECT * FROM machine LEFT OUTER JOIN ports ON machine.id=ports.ip_id"
    ).fetchall()

    return render_template('nodes/index.html', machines=nodes)


@bp.route('/<string:ip>/ping')
@login_required
def ping(ip):
    db = get_db()
    check = db.execute("SELECT id FROM machine WHERE ip=?", (ip,)).fetchone()

    if check is not None:
        us = UnitSearch()
        ping_time = us.ping(ip)
        print(ping_time)
    else:
        abort(404, "The requested ip is not availabel")

    nodes = db.execute(
        "SELECT * FROM machine LEFT OUTER JOIN ports ON machine.id=ports.ip_id"
    ).fetchall()

    return render_template('nodes/index.html', machines=nodes)
