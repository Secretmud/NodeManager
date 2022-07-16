import json

import celery
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.tools.find_units import *
from datetime import datetime

bp = Blueprint('node', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    nodes = db.execute(
        "SELECT * FROM machine LEFT OUTER JOIN ports ON machine.id=ports.ip_id"
    ).fetchall()
    return render_template('nodes/index.html', machines=nodes)


def get_data():
    us = UnitSearch()
    db = get_db()
    ip_fetch = db.execute("SELECT ip FROM machine").fetchall()
    ip_list = []
    dict = {}
    for ip in ip_fetch:
        ip_list.append(ip['ip'])
        us.set_ip(ip_list=ip_list)
        online_machines, ssh_port_open, time_taken = us.parallel_calls()
        i = 0
        for online in online_machines:
            ssh_enabled = True if (online in ssh_port_open) else False
            dict[i] = {"ip": online, "ssh": ssh_enabled}
            i += 1
    flash(f"Search took: {round(time_taken, 2)}s")
    return dict


@bp.route('/scan', methods=("GET", "POST"))
@login_required
def scan():
    if request.method == "GET":
        db = get_db()
        hosts = get_data()
        print(hosts)
        error = 0
        for host in hosts.keys():
            try:
                ip = hosts[host]['ip']
                ssh = hosts[host]['ssh']
                check = db.execute("SELECT id FROM machine WHERE ip=?", (ip,)).fetchone()
                if check is None:
                    db.execute("INSERT INTO machine (lookup_id, created, ip, last_attack) VALUES (?, ?, ?, ?)",
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
                    db.execute("UPDATE machine SET last_attack = ? WHERE ip=?",
                               (datetime.now(), ip))
                    db.commit()
                if check_ssh is not None:
                    db.execute("UPDATE ports SET port = ? WHERE"
                               " ip_id=(SELECT machine.id FROM machine WHERE machine.ip=?)",
                               (ssh, ip))
                    db.commit()
            except TypeError:
                print(host)
                error += 1

    print(f"Errors: {error}")

    nodes = db.execute(
        "SELECT * FROM machine LEFT OUTER JOIN ports ON machine.id=ports.ip_id"
    ).fetchall()
    for node in nodes:
        print(node['id'], node['ip'])

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
        db.execute("UPDATE machine SET last_attack = ? WHERE ip=?",
                   (datetime.now(), ip_check))
        db.execute("UPDATE ports SET port = ? WHERE"
                   " ip_id=(SELECT machine.id FROM machine WHERE machine.ip=?)",
                   (ssh_check, ip_check))
        db.commit()

    else:
        abort(404, "The requested ip is not available")

    nodes = db.execute(
        "SELECT * FROM machine LEFT OUTER JOIN ports ON machine.id=ports.ip_id"
    ).fetchall()

    return render_template('nodes/index.html', machines=nodes)


@bp.route('/<string:ip>/ping')
@login_required
def ping(ip):
    db = get_db()
    check = db.execute("SELECT id FROM machine WHERE ip=?", (ip,)).fetchone()
    ping_time = 0
    if check is not None:
        us = UnitSearch()
        ping_time = us.ping(ip)
        print(ping_time)
    else:
        abort(404, "The requested ip is not available")

    nodes = db.execute(
        "SELECT * FROM machine LEFT OUTER JOIN ports ON machine.id=ports.ip_id"
    ).fetchall()
    machine = db.execute(
        "SELECT ip FROM machine WHERE ip=?", (ip,)
    ).fetchone()

    return render_template('nodes/index.html', machines=nodes, ping=ping_time, node_ip=machine['ip'])


@bp.route('/<string:ip>/info')
@login_required
def get_info(ip):
    db = get_db()
    nodes = db.execute(
        "SELECT * FROM machine LEFT OUTER JOIN ports ON machine.id=ports.ip_id"
    ).fetchall()
    machine = db.execute(
        "SELECT * FROM machine WHERE ip=?", (ip,)
    ).fetchone()

    return render_template('nodes/index.html', machines=nodes, machine=machine)
