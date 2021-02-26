CREATE TABLE tests(
  id SERIAL PRIMARY KEY,
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
  temperature1 DOUBLE PRECISION,
  temperature2 DOUBLE PRECISION,
  FOREIGN KEY (test_id) REFERENCES tests (id)
);

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
SELECT create_hypertable('sensor_data', 'time');

INSERT INTO tests (started, finished) VALUES
  ('NOW()', 'NOW()');