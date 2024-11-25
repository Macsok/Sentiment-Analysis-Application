from flask import Flask, render_template, request, redirect, Response, jsonify
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))
import analyses
import sseStream
import xScrape


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


@app.route("/pepe")
def pepe():
    return render_template("pepe.html")
  

@app.route("/singlereview", methods=["GET", "POST"])
def singlereview():
    if request.method == "POST":
        start = time.time()
        text = request.form["textinput"]
        print(text)
        scores = analyses.default_analysis(text)
        sentiment = analyses.get_sentiment(scores[3])
        end = time.time()
        adbreak = 15
        wait_time = max(0, (adbreak - (end - start)) * 1000)
        return render_template("singlereview.html", textinput=text, sentiment=sentiment, positive=scores[0]*100, 
                               negative=scores[1]*100, neutral=scores[2]*100, language=scores[4].upper(), text=scores[5], wait_time=wait_time)
    else:
        return render_template("singlereview.html", wait_time=0)


@app.route("/contact")
def contact():
    return render_template("contact.html")

  
@app.route("/contribute")
def contribute():
    return render_template("contribute.html")


@app.route("/stream")
def stream():
    """
    This route streams the server-sent events (SSE) to the frontend.
    """
    csv_file_path = os.path.join(os.path.dirname(__file__), 'data.csv')
    return Response(sseStream.x_generate_sse(csv_file_path), content_type='text/event-stream')


@app.route('/x_review', methods=["GET", "POST"])
def x_review():
    if request.method == "POST":
        url = request.form["textinput"]
        task_done = True
        return render_template('x_review.html', textinput=url, task_done=task_done)
    else:
        return render_template('x_review.html')
    
@app.route('/start_scraping', methods=["POST"])
def start_scraping_route():
    data = request.get_json()
    url = data.get('url')
    if url:
        start_scraping(url)
        return jsonify(success=True)
    return jsonify(success=False)

def start_scraping(url):
    # Implement the scraping logic here
    time.sleep(5)
    print('scraping...')
    
    
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
# import random
# from flask_cors import CORS
# from flask import jsonify, send_from_directory

# CORS(app)

# @app.route('/get-data', methods=['GET'])
# def get_data():
#     """
#     Simulates a backend function generating random data.
#     """
#     random_number = random.randint(1, 100)  # Simulated data
#     timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
#     data = {"message": f"Random Number: {random_number}", "timestamp": timestamp}
#     return jsonify(data)


# @app.route('/x_review')
# def x_review():
#     return render_template('x_review.html')

#------------------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)