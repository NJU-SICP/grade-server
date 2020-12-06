DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS scores;

CREATE TABLE students (
    stuid TEXT PRIMARY KEY,
    stuname TEXT NOT NULL
);

CREATE TABLE scores (
  stuid TEXT NOT NULL,
  assignment TEXT NOT NULL,
  score INTEGER NOT NULL,
  PRIMARY KEY (stuid, assignment, score),
  FOREIGN KEY (stuid) REFERENCES student (stuid)
);
