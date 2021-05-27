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
    return render_template("settings/setup.html")
