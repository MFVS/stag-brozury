from flask import Flask, render_template, send_from_directory
from stag_data import *

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/<predmet>')
def overview(predmet):
    data = get_data(predmet)
    return render_template('predmet.html', data=data)

@app.route('/favicon.ico')
def icon():
    return send_from_directory('static','ujep_erasmus.png')


if __name__ == "__main__":
    app.run()