from flask import (Blueprint, render_template, redirect, request, session, url_for, flash, g, make_response)
from sqlalchemy.sql import text
import uuid

def processQuery(sql, params):
    try:
        g.conn.execute(text(sql), params)
        return True
    except Exception as e:
        print(e)
        return False

