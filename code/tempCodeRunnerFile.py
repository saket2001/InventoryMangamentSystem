from flask import Flask, render_template
app = Flask(__name__)  # creating the Flask class object


@app.route('/')  # decorator defines the
def home():
    return render_template('login.html')

# @app.route('/contact')
# def contact():
#     return render_template("contact.html")


app.run(debug=True)