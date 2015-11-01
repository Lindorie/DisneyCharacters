# all the imports
import ConfigParser
import sqlite3
import logging
import os
import random

from logging.handlers import RotatingFileHandler
from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash
from contextlib import closing

from elo2 import Elo

elo = Elo()

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
  conn = sqlite3.connect(app.config['database'])
  conn.row_factory = sqlite3.Row
  return conn

def init_db():
  with closing(connect_db()) as db:
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

def query_db(query, args=(), one=False):
  cur = g.db.execute(query, args)
  rv = [dict((cur.description[idx][0], value)
          for idx, value in enumerate(row)) for row in cur.fetchall()]
  return (rv[0] if rv else None) if one else rv

def get_character(id):
  query = 'SELECT * FROM character WHERE id = ?'
  character = query_db(query, [id], one=True)
  if character is not None:
    character['picture'] = 'characters/'+str(character['id'])+'.jpg'
  return character

def get_all_characters(sort, order):
  query = 'SELECT * FROM character ORDER BY '+sort+' '+order
  allcharacters = query_db(query)
  if allcharacters:
    for c in allcharacters:
      c['picture'] = 'characters/'+str(c['id'])+'.jpg'
  return allcharacters

def get_search_results(search):
  query = 'SELECT * FROM character WHERE name LIKE "%'+search+'%" \
  OR films LIKE "%'+search+'%" ORDER BY name ASC'
  results = query_db(query)
  if results:
    for c in results:
      c['picture'] = 'characters/'+str(c['id'])+'.jpg'
  return results

def get_the_last_id():
  query = 'SELECT id FROM character ORDER BY id DESC'
  lastid = query_db(query, [], one=True)
  return lastid['id']

def get_random_player():
  max = int(get_the_last_id())
  player = None
  while (player == None):
    rand = random.randrange(1, max+1)
    player = get_character(rand)
  return player

def get_x_characters(x=1):
  i = 1
  collection = []
  while (i <= x):
    char = get_random_player()
    collection.append(char)
    i = i + 1
  return collection

@app.before_request
def before_request():
  g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

@app.route('/')
def home():
  collection = get_x_characters(6)
  return render_template('home.html', collection=collection)

@app.route('/top10')
def top10():
  this_route = url_for('.top10')
  app.logger.info("Logging a test message from "+this_route)
  cur = g.db.execute('SELECT id,name,score,films FROM character ORDER BY \
  score DESC LIMIT 0,10')
  top = [dict(id=row[0],name=row[1],score=row[2],films=row[3],picture='characters/'+str(row[0])+'.jpg') for row in cur.fetchall()]
  return render_template('top10.html', top=top)

@app.route('/fullrankings')
def full():
  rankings = get_all_characters("score","DESC")
  return render_template('full.html', rankings=rankings)

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
    query = 'SELECT * FROM character WHERE name = ?'
    testname = query_db(query, [request.form['name']])
    if testname:
      error = "Sorry, there is already a character with this name"
      return render_template('add.html', error=error)
    cur = g.db.cursor()
    cur.execute('INSERT INTO character (name,description,films) VALUES \
    (?,?,?)', [request.form['name'], request.form['description'], request.form['films']])
    g.db.commit()
    f = request.files['picture']
    lastid = str(cur.lastrowid)
    f.save('static/characters/'+lastid+'.jpg')
    flash('New character was successfully posted')
    return redirect(url_for('character', id=lastid))
  return render_template('add.html', error=error)

@app.route('/delete/<int:id>')
def delete(id):
  error = None
  if not session.get('logged_in'):
    abort(401)
  cur = g.db.cursor()
  cur.execute('DELETE FROM character WHERE id = ?', [id])
  g.db.commit()
  os.remove('static/characters/'+str(id)+'.jpg')
  flash('The character was successfully removed.')
  return redirect(url_for('top10'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
  if not session.get('logged_in'):
    abort(401)
  if request.method == 'POST':
    query = 'UPDATE character SET name = ?, description = ?, films = ? WHERE id = ?'
    cur = g.db.cursor()
    cur.execute(query, [request.form['name'], request.form['description'],\
    request.form['films'], id])
    g.db.commit()
    if request.files['picture']:
      f = request.files['picture']
      f.save('static/characters/'+str(id)+'.jpg')
    flash('The character was edited')
    return redirect(url_for('character', id=id))
  else:
    query = 'SELECT * FROM character WHERE id = ?'
    character = query_db(query, [id], one=True)
    if character:
      picture = 'characters/'+str(character['id'])+'.jpg'
      return render_template('edit.html', character=character, picture=picture)
    else:
      flash('No such character')
      return redirect(url_from('browse'))

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

@app.route('/match', methods=['GET', 'POST'])
def match():
  player_context = [get_random_player(),get_random_player()]
  while player_context[0]['id'] == player_context[1]['id']:
    player_context[1] = get_random_player()

  if session.new:
    session['player_store'] = [x['id'] for x in player_context]

  if request.method == 'POST':
    choice = int(request.form['choice'])
    winner_id = session['player_store'][choice-1]
    looser_id = session['player_store'][choice-2]

    winner = get_character(winner_id)
    looser = get_character(looser_id)

    winner, looser = elo.match(winner, looser)
    
    # set scores, wins, matches
    query = 'UPDATE character SET score = ?, wins = ?, matches = ? \
    WHERE id  = ?'
    cur = g.db.cursor()
    cur.execute(query, [winner['score'], winner['wins'],\
    winner['matches'], winner['id']])
    cur.execute(query, [looser['score'], looser['wins'],\
    looser['matches'], looser['id']])
    g.db.commit()
    
  else:
    winner = None
    looser = None
  
  session['player_store'] = [x['id'] for x in player_context]

  return render_template('match.html', players=player_context, winner=winner,
  looser=looser)

@app.route('/browse', methods=['GET', 'POST'])
@app.route('/browse/<sort>/<order>', methods=['GET', 'POST'])
def browse(sort=None,order=None):
  if sort == None:
    sort = "name"
  if order == None:
    order = "ASC"
  collection = {}
  search = None
  results = None
  if request.method == 'POST':
    if request.form['search']:
      search = request.form['search']
      collection = get_search_results(search)
      if not collection:
        results = "nothing"
  if not collection:
    collection = get_all_characters(sort, order)
  return render_template('browse.html', collection=collection, search=search,
  order=order, results=results)

@app.route('/character')
@app.route('/character/<int:id>')
def character(id=None):
  if id == None:
    return redirect(url_for('browse'))
  else:
    query = 'SELECT * FROM character WHERE id=?'
    character = query_db(query, [id], one=True)
    if character is None:
      flash('No such character')
      return redirect(url_for('browse'))
    else:
      films = character['films']
      id = character['id']
      query2 = 'SELECT id,name FROM character WHERE films = ? AND id <> ?'
      samefilms = query_db(query2, [films, id])
      picture = 'characters/'+str(character['id'])+'.jpg'
      pictures = {}
      if samefilms:
        for c in samefilms:
          cid = c['id']
          pictures[cid] = 'characters/'+str(cid)+'.jpg'
      return render_template('character.html', character=character, picture=picture, samefilms=samefilms, pictures=pictures)

@app.route('/film')
@app.route('/film/<name>')
def film(name=None):
  if name == None:
    return redirect(url_for('browse'))
  else:
    query = 'SELECT id,name FROM character WHERE films = ?'
    characters = query_db(query, [name])
    if characters is None:
      flash('No such film')
      return redirect(url_for('browse'))
    else:
      pictures = {}
      for c in characters:
        cid = c['id']
        pictures[cid] = 'characters/'+str(cid)+'.jpg'
      return render_template('film.html', characters=characters,
      pictures=pictures, filmname=name)

if __name__ == '__main__':
  init(app)
  logs(app)
  app.run(
    host = app.config['ip_address'], 
    port = int(app.config['port'])
  )
