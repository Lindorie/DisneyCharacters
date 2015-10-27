# all the imports
import ConfigParser
import sqlite3
import logging

from logging.handlers import RotatingFileHandler
from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash
from contextlib import closing

app = Flask(__name__)

def init(app):
  config = ConfigParser.ConfigParser()
  config_location = "etc/config.cfg"
  try:
    config.read(config_location)

    app.config['DEBUG'] = config.get("config", "debug")
    app.config['ip_address'] = config.get("config", "ip_address")
    app.config['port'] = config.get("config", "port")
    app.config['url'] = config.get("config", "url")
    app.secret_key  = config.get("config", "secret_key")
    app.config['username'] = config.get("config", "username")
    app.config['password'] = config.get("config", "password")
    app.config['database'] = config.get("config", "database")

    app.config['log_file'] = config.get("logging", "name")
    app.config['log_location'] = config.get("logging", "location")
    app.config['log_level'] = config.get("logging", "level")
  except:
    print ("Could not read config from: "), config_location

def logs(app):
  log_pathname = app.config['log_location'] + app.config['log_file']
  file_handler = RotatingFileHandler(log_pathname, maxBytes=1024*1024*10, backupCount=1024)
  file_handler.setLevel(app.config['log_level'])
  formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(module)s |\
  %(funcName)s | %(message)s')
  file_handler.setFormatter(formatter)
  app.logger.setLevel(app.config['log_level'])
  app.logger.addHandler(file_handler)

def connect_db():
  init(app)
  return sqlite3.connect(app.config['database'])

def init_db():
  with closing(connect_db()) as db:
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

@app.before_request
def before_request():
  g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

@app.route('/')
def top10():
  this_route = url_for('.top10')
  app.logger.info("Logging a test message from "+this_route)
  cur = g.db.execute('SELECT id,name,description,films FROM character DESC')
  top = [dict(id=row[0],name=row[1],description=row[2],films=row[3],picture='characters/'+str(row[0])+'.jpg') for row in cur.fetchall()]
  return render_template('top10.html', top=top)

@app.route('/config')
def config():
  str = []
  str.append('Debug: '+app.config['DEBUG'])
  str.append('port: '+app.config['port'])
  str.append('url: '+app.config['url'])
  str.append('ip_address: '+app.config['ip_address'])
  str.append('username: '+app.config['username'])
  str.append('database: '+app.config['database'])
  return '\t'.join(str)

@app.route('/add', methods=['GET', 'POST'])
def add_character():
  error = None
  if not session.get('logged_in'):
    abort(401)
  if request.method == 'POST':
    # Check the required fields (name, picture, films)
    if request.form['name'] == "" or request.form['picture'] == "" or \
    request.form['films'] == "":
      error = "Please fill the required fields"
    else:
      cur = g.db.cursor()
      cur.execute('INSERT INTO character (name,description,films) VALUES \
      (?,?,?)', [request.form['name'], request.form['description'], request.form['films']])
      g.db.commit()
      f = request.files['picture']
      lastid = str(cur.lastrowid)
      f.save('static/characters/'+lastid+'.jpg')
      flash('New character was successfully posted')
      return redirect(url_for('top10'))
  return render_template('add.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    if request.form['username'] != app.config['username']:
      error = 'Invalid username'
    elif request.form['password'] != app.config['password']:
      error = 'Invalid password'
    else:
      session['logged_in'] = True
      flash('You were logged in')
      return redirect(url_for('top10'))
  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  flash('You were logged out')
  return redirect(url_for('top10'))

@app.route('/match')
def match():
  return render_template('match.html')

@app.route('/browse')
def browse():
  return render_template('browse.html')

if __name__ == '__main__':
  init(app)
  logs(app)
  app.run(
    host = app.config['ip_address'], 
    port = int(app.config['port'])
  )
