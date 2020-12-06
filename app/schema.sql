DROP TABLE IF EXISTS stu;
DROP TABLE IF EXISTS scores;

CREATE TABLE stu (
    stuid INTEGER PRIMARY KEY,
    username TEXT NOT NULL
);

CREATE TABLE scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  stuid INTEGER NOT NULL,
  proj TEXT NOT NULL,
  score INTEGER NOT NULL,
  FOREIGN KEY (stuid) REFERENCES stu (stuid)
);