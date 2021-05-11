from flask import Flask, jsonify
from tools.find_units import *
app = Flask(__name__)

def get_data(data):
    us = UnitSearch("192.168.1.1", "0.0.0.0")
    active, ssh = us.parallel_calls()
    if data == "active":
        return active
    elif data == "ssh":
        return ssh
    else:
        return "no data"



@app.route('/active', methods=["GET"])
def active():
    return jsonify({"Machines": get_data("active")})

@app.route('/ssh', methods=["GET"])
def ssh():
    return jsonify({"SSH": get_data("ssh")})


if __name__ == "__main__":
    app.run(debug = True)
