create materialized view if not exists biggest_tx_receivers as
with out_msg_after_airdrop as (
	select source_address ,
		destination_address 
	from out_messages om 
	where created_lt > 46894144000001
)
select destination_address, count(*) 
from out_msg_after_airdrop
group by destination_address
having count(*) > 3