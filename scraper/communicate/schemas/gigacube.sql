CREATE SCHEMA IF NOT EXISTS gigacube;
COMMENT ON SCHEMA gigacube is '1';

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

DROP TABLE IF EXISTS gigacube.data;
CREATE TABLE IF NOT EXISTS gigacube.data
(
    timestamp       TIMESTAMPTZ NOT NULL,
    volume          NUMERIC NOT NULL,               -- current volume consumption (e.g. 123.4GB)
    billing_id      TEXT NOT NULL                   -- billing period, MD5 hash
);

DROP TABLE IF EXISTS gigacube.billing;
CREATE TABLE IF NOT EXISTS gigacube.billing
(
    billing_id      TEXT NOT NULL,
    start_date      TIMESTAMPTZ NOT NULL,           -- first day of billing period
    end_date        TIMESTAMPTZ NOT NULL,           -- last day of billing period
    total_volume    NUMERIC NOT NULL,               -- total volume available (e.g. 500GB)
    UNIQUE(billing_id)
);

SELECT create_hypertable('gigacube.data',
                         'timestamp',
                         chunk_time_interval => INTERVAL '7 day',
                         if_not_exists => TRUE);
