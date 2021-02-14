-- CREATE TABLE sensors(
--   id SERIAL PRIMARY KEY,
--   name VARCHAR(50)
-- );

CREATE TABLE tests(
  id SERIAL PRIMARY KEY,
  created TIMESTAMPTZ NOT NULL,
  status BOOLEAN NOT NULL DEFAULT FALSE,
  started TIMESTAMPTZ NOT NULL,
  finished TIMESTAMPTZ
);

CREATE TABLE sensor_data (
  test_id INTEGER NOT NULL,
  time TIMESTAMPTZ NOT NULL,
  timeconf TIME NOT NULL,
  onconf DOUBLE PRECISION,
  offconf DOUBLE PRECISION,
  speed DOUBLE PRECISION,
  temperature1 DOUBLE PRECISION,
  temperature2 DOUBLE PRECISION,
  FOREIGN KEY (sensor_id) REFERENCES sensors (id),
  FOREIGN KEY (test_id) REFERENCES tests (id)
);

SELECT create_hypertable('sensor_data', 'time');


-- INSERT INTO sensors (name) VALUES
--   ('pierwszy'),
--   ('drugi');

INSERT INTO tests (started, finished) VALUES
  ('NOW()', 'NOW()');