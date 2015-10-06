from flask import Flask, redirect, url_for, abort
app = Flask(__name__, static_folder = "images")

@app.route("/")
def root():
  return "The default route"

@app.route("/hello/")
def hello():
  return "Hello !!!"

@app.route("/img")
def img():
  start = '<img src="'
  url = url_for('static', filename='chat.jpg')
  end = '">'
  return start+url+end, 200 

@app.route("/login")
def login():
  return "Now we would get username & password"

@app.route("/private")
def private():
  return redirect(url_for('login'))

@app.route('/force404')
def force404():
  abort(404)

@app.errorhandler(404)
def page_not_found(error):
  return "Couldn't find the page you requested.", 404

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
