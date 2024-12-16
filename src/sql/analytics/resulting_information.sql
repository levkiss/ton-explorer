create materialized view if not exists resulting_information as 
with airdrop_info as (
	select receiver_url, 
		receiver,
		sum(tx_value) as ttl_value_received, 
		count(distinct sender) as got_airdrop_from_drops_number,
		string_agg(distinct tx_date::text, ', ') as amount_receival_dates
	from airdrop_tx at2 
	group by receiver_url, receiver
)
select ai.receiver_url,
	ttl_value_received,
	got_airdrop_from_drops_number,
	amount_receival_dates,
	coalesce(be.tx_number, 0) as tx_before_airdrop,
	coalesce(af.tx_number, 0) as tx_after_airdrop,
	to_timestamp(la.utime)::date as last_tx_date,
	la.end_balance / 10^9 as ending_balance
from airdrop_info ai
	left join before_airdrop_tx_number be 
		on ai.receiver = be.account_address 
	left join after_airdrop_tx_number af
		on ai.receiver = af.account_address
	left join last_airdrop_users_tx la
		on ai.receiver = la.account_address 
