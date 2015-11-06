# Disney Characters
This Python Flask web app has been developed for the Advanced Web technologies module when studying at Edinburgh Napier University. This is a game based on the Elo rating system (used for chess competitions and in the film "The Social Network") where you have to choose your favourite Disney Character between two proposed.

![Screenshot of the homepage](http://home.carine-pic.com/Edinburgh/disney_characters.jpg)

# How to run the app


If you want to use the app, just launch the file `index.py` in the src folder:

```
python index.py
```

If you want to start from 0, you have to create the database (launch the file `create_db.py` in the src folder) and remove all the pictures in the `src/static/characters` folder.

```
python create_db.py
```

# Log in

If you want to log in, the default user name is `admin` and the password is `default`

Change the parameters in `etc/config.cfg`
