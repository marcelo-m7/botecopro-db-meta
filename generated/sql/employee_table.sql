-- SQLite table for Employee (table: employee)
CREATE TABLE IF NOT EXISTS employee (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  role TEXT,
  email TEXT,
  hourly_rate_cents INTEGER
);
