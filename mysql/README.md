# Database Details

## Data Source

CSV:  https://docs.google.com/spreadsheets/d/1F0aWurN1tqbUcx7EQEeQKWgqnp7kJj3DLsVlhtWyz5A/edit#gid=0
Data has been conveniently loaded into [cards_info_utf8.csv](./cards_info_utf8.csv) available in this git repo

## MySQL

To create the database table used by the app, issue the following MySQL command:

```
CREATE TABLE agricola_cards (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  ext_id INT UNIQUE,
  card_title VARCHAR(80),
  insight MEDIUMTEXT,
  rating INT,
  source VARCHAR(255),
  deck VARCHAR(25),
  base_expansion VARCHAR(255),
  type VARCHAR(255),
  players CHAR(2),
  cost VARCHAR(255),
  vps VARCHAR(5),
  prerequisites VARCHAR(255),
  pass_left TINYINT(1),
  category VARCHAR(255),
  text MEDIUMTEXT,
  count INT,
  row_id INT
);
```

## Loading Data

Once the MySQL table is created, load the data from the CSV into it
