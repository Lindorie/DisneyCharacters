DROP TABLE if EXISTS character;

CREATE TABLE character (
  id integer PRIMARY KEY autoincrement,
  name varchar(100) NOT NULL,
  description varchar(2000) NOT NULL,
  pictures varchar(200) NOT NULL,
  films varchar(200) NOT NULL,
  friends varchar(200) NULL,
  enemies varchar(200) NULL
);

