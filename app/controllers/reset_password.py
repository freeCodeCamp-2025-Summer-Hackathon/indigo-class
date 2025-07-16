'''
from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app
from app.models import User, db
from app.utils.mail import send_password_reset_email
from app.utils.token import generate_reset_token
from typing import Optional
'''

reset_password_bp = Blueprint("reset_password", __name__)

@reset_password_bp.route("", methods=["GET", "POST"])
def verify_account(username, email):