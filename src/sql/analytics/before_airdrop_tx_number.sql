create materialized view if not exists before_airdrop_tx_number as
select t.account_address, 
    count(*) as tx_number 
from transactions t 
	join airdrop_tx a 
		on t.account_address = a.receiver 
where t.lt < a.lt 
	and in_msg_msg_type = 'ext_in_msg' 
	and end_status = 'active'
group by t.account_address