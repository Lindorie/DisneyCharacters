from flask import Flask, redirect, url_for, request
app = Flask(__name__)

@app.route("/")
def root():
  return "The default route"

@app.route("/detail/")
def detail():
  animal = request.args.get('animal','')
  if (animal != ''):
    return "Details for %s" % animal
  else:
    return redirect(url_for('root'))

@app.route("/map")
def map():
  region = request.args.get('region','')
  if (region != ''):
    return "List of the animals in this region %s" % region
  else:
    return "the map"

@app.route("/map/<region>")
def region(region):
  return "the region %s" % region

@app.errorhandler(404)
def page_not_found(error):
  return "Couldn't find the page you requested.", 404

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
