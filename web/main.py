from flask import Flask, render_template, request, Response, jsonify
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))
import analyses
import sseStream
import scraperX
import scraperYT


app = Flask(__name__)


@app.route("/web/static")
@app.route("/home")
@app.route("/")
def home():
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

stream_to = None
@app.route("/stream")
def stream():
    """
    This route streams the server-sent events (SSE) to the frontend.
    """
    global stream_to
    if stream_to == 'x':
        csv_file_path = os.path.join(os.path.dirname(__file__), 'comm/X_replies.csv')
        return Response(sseStream.generate_sse(csv_file_path), content_type='text/event-stream')
    if stream_to == 'yt':
        csv_file_path = os.path.join(os.path.dirname(__file__), 'comm/YT_replies.csv')
        return Response(sseStream.generate_sse(csv_file_path), content_type='text/event-stream')    
    if stream_to == 'amazon':
        csv_file_path = os.path.join(os.path.dirname(__file__), 'comm/Amazon_replies.csv')
        return Response(sseStream.generate_sse(csv_file_path), content_type='text/event-stream')

@app.route('/x_review', methods=["GET", "POST"])
def x_review():
    if request.method == "POST":
        url = request.form["textinput"]
        task_done = True
        return render_template(
            'x_review.html', 
            textinput=url, 
            task_done=task_done)
    else:
        return render_template('x_review.html')
    

@app.route('/yt_review', methods=["GET", "POST"])
def yt_review():
    if request.method == "POST":
        url = request.form["textinput"]
        # https://www.youtube.com/watch?v=XqZsoesa55w&ab_channel=BabyShark-PinkfongKids%E2%80%99Songs%26Stories
        start = url.find("watch?v=") + len("watch?v=")
        end = url.find("&ab_channel")
        id = url[start:end]
        print(f'\n\n\n YOUR ID IS: {id}\n\n\n')
        task_done = True
        return render_template(
            'yt_review.html', 
            textinput=url, 
            task_done=task_done)
    else:
        return render_template('yt_review.html')
    

@app.route('/start_scraping', methods=["POST"])
def start_scraping_route():
    global stream_to
    data = request.get_json()
    url = data.get('url')
    file = data.get('file')
    if url and file == 'x_review':
        print("Scraping from X...")
        stream_to = 'x'
        scraperX.scrap_and_save(url)
        return jsonify(success=True, file=file)
    if url and file == 'yt_review':
        print("Scraping from YT...")
        stream_to = 'yt'
        scraperYT.scrap_and_save(url)
        return jsonify(success=True, file=file)
    if url and file == 'amazon_review':
        print("Scraping from Amazon...")
        stream_to = 'amazon'
        pass
        return jsonify(success=True, file=file)
    return jsonify(success=False)


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

#------------------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)