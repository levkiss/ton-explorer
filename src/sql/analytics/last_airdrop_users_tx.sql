create materialized view last_airdrop_users_tx as 
WITH max_lts AS (
  SELECT account_address, MAX(lt) AS max_lt
  FROM transactions
  GROUP BY account_address
)
SELECT t.*
FROM max_lts
JOIN transactions t 
  ON t.account_address = max_lts.account_address 
 AND t.lt = max_lts.max_lt