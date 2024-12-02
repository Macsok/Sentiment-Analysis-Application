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
    """Render the home page."""
    return render_template("home.html")


@app.route("/about")
def about():
    """Render the about page."""
    return render_template("about.html")


@app.route("/pepe")
def pepe():
    """Render the pepe page."""
    return render_template("pepe.html")


@app.route("/singlereview", methods=["GET", "POST"])
def singlereview():
    """Handle single review analysis."""
    if request.method == "POST":
        start = time.time()
        text = request.form["textinput"]
        print(text)
        scores = analyses.default_analysis(text)
        sentiment = analyses.get_sentiment(scores[3])
        end = time.time()
        adbreak = 15
        wait_time = max(0, (adbreak - (end - start)) * 1000)
        return render_template(
            "singlereview.html", 
            textinput=text, 
            sentiment=sentiment, 
            positive=scores[0] * 100, 
            negative=scores[1] * 100, 
            neutral=scores[2] * 100, 
            language=scores[4].upper(), 
            text=scores[5], 
            wait_time=wait_time
        )
    else:
        return render_template("singlereview.html", wait_time=0)


@app.route("/contact")
def contact():
    """Render the contact page."""
    return render_template("contact.html")


@app.route("/contribute")
def contribute():
    """Render the contribute page."""
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
    """Handle X review scraping."""
    if request.method == "POST":
        url = request.form["textinput"]
        task_done = True
        return render_template(
            'x_review.html', 
            textinput=url, 
            task_done=task_done
        )
    else:
        return render_template('x_review.html')


@app.route('/amazon_review', methods=["GET", "POST"])
def amazon_review():
    """Handle Amazon review scraping."""
    if request.method == "POST":
        url = request.form["textinput"]
        task_done = True
        return render_template(
            'amazon_review.html', 
            textinput=url, 
            task_done=task_done
        )
    else:
        return render_template('amazon_review.html')


@app.route('/yt_review', methods=["GET", "POST"])
def yt_review():
    """Handle YouTube review scraping."""
    if request.method == "POST":
        url = request.form["textinput"]
        task_done = True
        return render_template(
            'yt_review.html', 
            textinput=url, 
            task_done=task_done
        )
    else:
        return render_template('yt_review.html')


@app.route('/start_scraping', methods=["POST"])
def start_scraping_route():
    """Start the scraping process based on the provided URL and file type."""
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


if __name__ == "__main__":
    app.run(debug=True)