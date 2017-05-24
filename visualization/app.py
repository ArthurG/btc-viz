from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/miserables.json")
def get_json():
    return render_template('miserables.json')



if __name__ == "__main__":
    app.run()
