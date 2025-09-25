CREATE TABLE sleep_sequences (
  user_id STRING,
  path    STRING,        -- which alternative matched
  start_ts TIMESTAMP(3),
  end_ts   TIMESTAMP(3),
  states   ARRAY<STRING> -- the matched states in order
) WITH (
  'connector' = 'print'
);

INSERT INTO sleep_sequences
SELECT *
FROM sleep_events
MATCH_RECOGNIZE (
  PARTITION BY user_id
  ORDER BY ts
  MEASURES
    FIRST(A.ts) AS start_ts,
    LAST(W.ts)  AS end_ts,
    CASE
      WHEN CLASSIFIER() = 'ALT1' THEN 'Awake→Light→Deep→REM→WokeUp'
      WHEN CLASSIFIER() = 'ALT2' THEN 'Awake→Light→REM→WokeUp'
      WHEN CLASSIFIER() = 'ALT3' THEN 'Awake→Light→WokeUp'
    END AS path,
    ARRAY[FIRST(A.state), FIRST(L.state),
          IF (CLASSIFIER()='ALT1', FIRST(D.state), NULL),
          IF (CLASSIFIER() IN ('ALT1','ALT2'), FIRST(R.state), NULL),
          FIRST(W.state)
    ] AS states
  ONE ROW PER MATCH
  AFTER MATCH SKIP PAST LAST ROW
  PATTERN (
    ALT1 | ALT2 | ALT3
  ) WITHIN INTERVAL '8' HOUR
  DEFINE
    A AS A.state = 'Awake',
    L AS L.state = 'Light',
    D AS D.state = 'Deep',
    R AS R.state = 'REM',
    W AS W.state = 'WokeUp',
    ALT1 AS A L D R W,         -- Awake→Light→Deep→REM→WokeUp
    ALT2 AS A L R W,           -- Awake→Light→REM→WokeUp
    ALT3 AS A L W              -- Awake→Light→WokeUp
);
