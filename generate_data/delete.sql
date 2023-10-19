DELETE FROM customer.transactions ;
DELETE FROM customer.accounts;
DELETE FROM customer.account_types ;
ALTER SEQUENCE customer.account_types_type_seq RESTART;
DELETE FROM customer.customer_info  ;
DELETE FROM django.auth_user;
ALTER SEQUENCE django.auth_user_id_seq RESTART;

TRUNCATE django.auth_user CASCADE;
