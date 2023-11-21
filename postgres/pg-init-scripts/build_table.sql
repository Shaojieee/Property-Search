CREATE TABLE logs (
   id serial PRIMARY KEY,
   run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE locations(
    runs_id INT NOT NULL,
    lat FLOAT NOT NULL,
    long FLOAT NOT NULL,
    travel_type VARCHAR(50) NOT NULL,
    frequency INT NOT NULL,
    PRIMARY KEY (runs_id, lat, long),
    FOREIGN KEY (runs_id) REFERENCES logs (id)
);