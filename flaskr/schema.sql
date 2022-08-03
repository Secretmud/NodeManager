DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS machine;
DROP TABLE IF EXISTS ports;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS payloads;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  email TEXT,
  password TEXT,
  role TEXT,
  reg_data timestamp
);

CREATE TABLE machine (
  id INTEGER PRIMARY KEY,
  lookup_id INTEGER,
  cust_id INTEGER,
  ip TEXT,
  created timestamp,
  last_attack timestamp,
  online boolean,
  FOREIGN KEY (cust_id) REFERENCES customers (id)
);

CREATE TABLE ports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  port TEXT NOT NULL,
  name TEXT,
  description TEXT,
  ip_id INTEGER NOT NULL,
  FOREIGN KEY (ip_id) REFERENCES machine (id)
);

CREATE TABLE customers (
  id INTEGER PRIMARY KEY,
  name TEXT
);

CREATE TABLE payloads (
  id INTEGER PRIMARY KEY,
  payload TEXT,
  name TEXT,
  type TEXT,
  creator INTEGER,
  FOREIGN KEY (creator) REFERENCES user (id)
);