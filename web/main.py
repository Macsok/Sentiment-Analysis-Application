from flask import Flask, render_template, request
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))
import analyses


app = Flask(__name__)


# Landing page
@app.route("/home")
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


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

@app.route('/script', methods=['GET', 'POST'])
def baseForm():
    if request.method == 'POST':
        # Retrieve data from a form
        user_data = request.form['user_input']
        print(user_data)
        # Render site with results
        return render_template('script.html', user_data=analyses.analyseText(user_data))
    # Display form site using GET method
    return render_template('script.html')


#------------------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)