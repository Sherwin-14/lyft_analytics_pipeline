-- Check nulls
select *
from "lyft"."lyft-raw" 
where (symbol IS NULL) or (timestamp IS NULL) or (open IS NULL) or (high IS NULL) or (low IS NULL) or (price IS NULL) or (previous_close IS NULL) or (volume IS NULL);

-- Exact duplicates (same record written twice):

SELECT symbol, timestamp, price, volume, COUNT(*) AS copies
FROM "lyft"."lyft-raw" 
GROUP BY symbol, timestamp, price, volume
HAVING COUNT(*) > 1;

-- Repeated values with different timestamps (the closed-market effect):

SELECT price, previous_close, volume, COUNT(*) AS records
FROM "lyft"."lyft-raw" 
GROUP BY price, previous_close, volume
ORDER BY records DESC;

-- Validity

SELECT COUNT(*) AS invalid_records
FROM "lyft"."lyft-raw" 
WHERE NOT (low <= open AND open <= high AND low <= price AND price <= high)
   OR price <= 0 OR open <= 0 OR high <= 0 OR low <= 0
   OR volume < 0;
   
-- Timestamp gaps

SELECT timestamp, prev_timestamp, gap_seconds
FROM (
  SELECT timestamp,
         LAG(timestamp) OVER (ORDER BY from_iso8601_timestamp(timestamp)) AS prev_timestamp,
         date_diff('second',
                   LAG(from_iso8601_timestamp(timestamp)) OVER (ORDER BY from_iso8601_timestamp(timestamp)),
                   from_iso8601_timestamp(timestamp)) AS gap_seconds
  FROM "lyft"."lyft-raw" 
)
WHERE gap_seconds > 45
ORDER BY gap_seconds DESC;
