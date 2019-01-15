#!/usr/bin/env python
# -*- coding=UTF-8 -*-

import sqlite3

import click
from flask import current_app,g
from flask.cli import with_appcontext


def get_db():
    """
    创建一个db连接
    :return:一个数据库连接对象
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  #设置返回结果为类字典

    return g.db


def close_db(e=None):
    """
    关闭一个数据库连接
    :param e:
    :return:
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)  #告诉 Flask 在返回响应后进行清理的时候调用此函数。
    app.cli.add_command(init_db_command)  #添加一个新的 可以与 flask 一起工作的命令。