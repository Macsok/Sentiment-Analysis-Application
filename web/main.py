from flask import Flask, render_template, request, redirect

app = Flask(__name__)

def calculate_value(a): return 2*a 


@app.route("/web/static")

@app.route("/home")
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/allcommentsreview")
def allcommentsreview():
    return render_template("allcommentsreview.html")
@app.route("/singlereview")
def singlereview():
    return render_template("singlereview.html")

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
    if request.method == 'POST':
        input_value = float(request.form['input_value'])
        result = calculate_value(input_value)
    return render_template("calc.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)