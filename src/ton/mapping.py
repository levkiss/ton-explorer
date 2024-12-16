DEFAULT_TRANSACTION_COLUMNS = [
        'hash', 
        'lt', 
        'success', 
        'utime', 
        'total_fees', 
        'end_balance',
        'transaction_type', 
        'account_address', 
        'account_is_scam', 
        'account_is_wallet', 
        'wallet_address', 
        'in_msg_msg_type', 
        'orig_status', 
        'end_status',
        'in_msg_value', 
        'in_msg_source_address', 
        'in_msg_created_lt', 
        'in_msg_destination_address', 
        'in_msg_source_name', 
        'in_msg_op_code', 
        'in_msg_decoded_op_name', 
        'in_msg_decoded_body_text'
    ]

DEFAULT_OUT_MSG_COLUMNS = [
        'hash',  # transaction hash as foreign key
        'msg_type', 
        'created_lt', 
        'value', 
        'fwd_fee', 
        'ihr_fee', 
        'bounce',
        'destination_address', 
        'source_address', 
        'op_code',
        'decoded_op_name', 
        'decoded_body_text'
    ]