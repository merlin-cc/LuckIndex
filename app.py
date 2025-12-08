from flask import Flask, render_template
import io
import base64


app = Flask (__name__)

@app.route("/")
def welcome():
    return render_template("welcome.html")


if __name__ == "__main__":
    app.run(debug=True)
