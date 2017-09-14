CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS flags(flag TEXT PRIMARY KEY, value INTEGER NOT NULL, event_id INTEGER REFERENCES events(id));
CREATE TABLE IF NOT EXISTS flagsfound(
  flag_id TEXT NOT NULL REFERENCES flags(flag),
  user_id TEXT NOT NULL REFERENCES users(id),
  PRIMARY KEY (flag_id, user_id)
);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, name TEXT NOT NULL, active BOOLEAN, has_teams BOOLEAN);
CREATE TABLE IF NOT EXISTS teams(
  name TEXT NOT NULL,
  event_id INTEGER REFERENCES events(id),
  PRIMARY KEY (name, event_id)
);
CREATE TABLE IF NOT EXISTS teamusers(
  team_name TEXT NOT NULL REFERENCES teams(name),
  event_id INTEGER NOT NULL REFERENCES teams(event_id),
  user_id TEXT NOT NULL REFERENCES users(id),
  PRIMARY KEY (team_name, event_id, user_id)
);