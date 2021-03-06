from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from url_shortener.models import User, Url
from url_shortener.db import db
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Could not find that user!", "danger")
            return redirect(url_for("auth.login"))
        elif not check_password_hash(user.password, password):
            flash("Invalid password!", "danger")
            return redirect(url_for("auth.login"))

        if session.get("logged_out_links"):
            flattened_list = [link[1] for link in session.get("logged_out_links")]
            db.session.query(Url).filter(Url.shortened_id.in_(flattened_list)).update({"user_id": user.id})
            db.session.commit()

            session.pop("logged_out_links")

        login_user(user)
        next_url = request.args.get("next")
        return redirect(next_url or url_for("main.index"))


@auth.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/signup.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Invalid login info!", "danger")
            return redirect(url_for("auth.register"))

        user = User.query.filter_by(username=username).first()
        if user:
            flash("A user with that username already exists!!", "danger")
            return redirect(url_for("auth.register"))

        user = User(
            username=username,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("auth.login"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
