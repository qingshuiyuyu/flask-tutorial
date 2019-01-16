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
                "insert into user(username,password) value (?,?)",(username,generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')
