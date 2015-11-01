DROP TABLE if EXISTS character;

CREATE TABLE character (
  id integer PRIMARY KEY autoincrement,
  name varchar(100) NOT NULL,
  description varchar(2000) NULL,
  films varchar(200) NOT NULL,
  friends varchar(200) NULL,
  enemies varchar(200) NULL,
  score float DEFAULT 1500,
  wins integer DEFAULT 0,
  matches integer DEFAULT 0
);

