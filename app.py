from flask import Flask, render_template
from stag_data import *

app = Flask(__name__)

@app.route('/<predmet>')
def home(predmet):
    data = get_data(predmet)
    return render_template('home.html', data=data)


if __name__ == "__main__":
    app.run()