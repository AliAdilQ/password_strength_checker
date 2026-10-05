"""Public informational pages."""
from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.get("/")
def home():
    return render_template("index.html")


@main.get("/about")
def about():
    return render_template("about.html")


@main.get("/security-tips")
def security_tips():
    return render_template("security_tips.html")
