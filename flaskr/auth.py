#!/usr/bin/env python
# -*- coding=UTF-8 -*-

import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route("/register",methods=["POST","GET"])
def register():

    if request.method == "POST":
        #如果是POST请求
        username = request.form["username"]  #用户名
        password= request.form["password"]  #密码
        db = get_db()
        error= None

        if not username:
            error = "username is required!"
        elif not password:
            error = "passname is required"
        elif db.execute(
            'select id from user where username=?',(username,)
        ).fetchone() is not None:
            error = "username {} is already registered".format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route("/login",methods=["POST","GET"])
def login():
    """
    登陆模块
    :return:
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        error = None

        user = db.execute(
            "select * from user where username=?",(username,)
        ).fetchone()
        if user is None:
            error = "Incorrect username"
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for('index'))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    """
    检查user_id是否存在
    :return:
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "select * from user where id=?",(user_id,)
        ).fetchone()

@bp.route("/logout")
def logout():
    """
    退出，从定向到index页面
    :return:
    """
    session.clear()
    return redirect(url_for("/index"))


def login_required(view):
    """
    检查是否登陆,如果已经登陆，继续访问请求页面，没有登陆则访问登陆页面
    :param view: 请求视图
    :return: 新的视图
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("/auth.login"))
        return view(**kwargs)

    return wrapped_view