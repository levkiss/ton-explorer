CREATE INDEX if not exists idx_transactions_account_address ON public.transactions(account_address);
CREATE INDEX if not exists idx_transactions_utime ON public.transactions(utime);

CREATE INDEX if not exists idx_out_messages_source_address ON public.out_messages(source_address);
CREATE INDEX if not exists idx_out_messages_destination_address ON public.out_messages(destination_address);