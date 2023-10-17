
--- Database Creations
CREATE DATABASE drck_banking;
GRANT ALL PRIVILEGES ON DATABASE drck_banking to django;
\c drck_banking postgres;


--- Schema Creations
CREATE SCHEMA django;
CREATE SCHEMA customer;
CREATE SCHEMA staff;
CREATE SCHEMA anonymisation;
GRANT ALL ON SCHEMA django to django;
GRANT ALL ON SCHEMA customer to django;
GRANT ALL ON SCHEMA staff to django;
GRANT ALL ON SCHEMA anonymisation to django;

INSERT INTO django.auth_user (username, password, email, phone_no, type, date_joined, last_login)
VALUES ('test1', 'testpassword', '1@gmail.com', '12345678', 'Customer', '2011-01-01 00:00:00', '2023-01-01 00:00:00');

INSERT INTO django.auth_user (username, password, email, phone_no, type, date_joined, last_login, is_active)
VALUES ('test1', 'testpassword', '1@gmail.com', '12345678', 'Customer', '2011-01-01 00:00:00', '2023-01-01 00:00:00', true);
