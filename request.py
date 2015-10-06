from flask import Flask, request, url_for
app = Flask(__name__, static_folder = "images")

@app.route("/account/", methods=['POST', 'GET'])
def account():
  if request.method == 'POST':
    f = request.files['datafile']
    filename = f.filename
    path = 'images/'+filename
    f.save(path)
    return '<img src="'+url_for('static', filename=filename)+'" alt="'+filename+'" />'
  else:
    page = '''
    <html><body>
      <form action="" method="post" name="form" enctype="multipart/form-data">
        <label for="name">File:</label>
        <input type="file" name="datafile" id="name" />
        <input type="submit" name="submit" id="submit" value="Envoyer" />
      </form>
    </body></html>'''
    return page

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
