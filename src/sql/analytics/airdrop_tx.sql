create materialized view airdrop_tx as 
select hash as tx_hash,
	'https://tonviewer.com/' || in_msg_source_address as sender_url,
	'https://tonviewer.com/' || account_address as receiver_url,
	to_timestamp(utime)::date as tx_date,
	in_msg_value / 10^9 as tx_value,
	in_msg_source_address as sender,
	account_address as receiver,
	lt,
	utime,
	end_balance,
	in_msg_value,
	total_fees
from transactions 
where in_msg_source_address in (
		"some_address"
		)