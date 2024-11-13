from flask import Flask, render_template, request, redirect
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))
from scripts import analyses


app = Flask(__name__)


@app.route("/web/static")
@app.route("/home")
@app.route("/")
def home():
    # Landing page
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/index")
def index():
    return render_template("index.html")
  

@app.route("/allcommentsreview", methods=["GET", "POST"])
def allcommentsreview():
    if request.method == "POST":
        text = request.form["textinput"]
        print(text)
        score = str(len(text)) + '%'
        return render_template("allcommentsreview.html", textinput=text, score=score)
    else:
        return render_template("allcommentsreview.html")

      
@app.route("/singlereview", methods=["GET", "POST"])
def singlereview():
    if request.method == "POST":
        text = request.form["textinput"]
        print(text)
        scores = analyses.default_analysis(text)
        sentiment = analyses.get_sentiment(scores[3])

        return render_template("singlereview-new.html", textinput=text, sentiment=sentiment, positive=scores[0]*100, 
                               negative=scores[1]*100, neutral=scores[2]*100, language=scores[4].upper(), text=scores[5])
    else:
        return render_template("singlereview-new.html")

      
@app.route("/wordreview", methods=["GET", "POST"])
def wordreview():
    if request.method == "POST":
        text = request.form["textinput"]
        print(text)
        score = str(len(text)) + '%'
        return render_template("wordreview.html", textinput=text, score=score)
    else:
        return render_template("wordreview.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

  
@app.route("/contribute")
def contribute():
    return render_template("contribute.html")

  
@app.route("/logo")
def logo():
    return render_template("logo.html")

  
@app.route("/review")
def review():
    return render_template("review.html")


@app.route("/calc", methods=['GET', 'POST'])
def calc():
    result = None
    
    
#------------------------------------------------------------
# Testing
#------------------------------------------------------------

# Base form of GET and POST function
"""
@app.route('/form', methods=['GET', 'POST'])
def baseForm():
    if request.method == 'POST':
        # Retrieve data from a form
        user_data = request.form['user_input']
        # Render site with results
        return render_template('form.html', user_data=user_data)
    # Display form site using GET method
    return render_template('form.html')
"""
#------------------------------------------------------------

import random
from flask import jsonify

@app.route('/fetch')
def js_fetch():
    return render_template('js-fetch.html')

# Trasa dla danych słupków progresu
@app.route('/progress')
def get_progress():
    # Generowanie losowych wartości progresu
    # progress_values = analyses.analyseText()
    return jsonify([1, 0.5, 0.2])


#------------------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)