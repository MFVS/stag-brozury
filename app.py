from flask import Flask, render_template, send_from_directory
from stag_data import *

app = Flask(__name__)

# Endpointy


@app.route("/")
def home():
    return render_template("home.html", katedry=katedry.keys())


@app.route("/<katedra>")
def overview(katedra):
    data = get_data(katedra)
    return render_template("predmet.html", data=data, katedra=katedra)


@app.route("/favicon.ico")
def icon():
    return send_from_directory("static", "stag_favcon.ico")


if __name__ == "__main__":
    app.run()
