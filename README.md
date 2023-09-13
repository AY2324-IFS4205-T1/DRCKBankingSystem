# DRCKBankingSystem

## Setup Instructions

* Log in to Postgres

```bash
psql -U postgres
# OR
sudo -u postgres psql
```

* Set up database

```sql
postgres=# CREATE DATABASE drck_banking;
postgres=# CREATE USER django with encrypted password 'XXX'; # not needed if user alr created
postgres=# GRANT ALL PRIVILEGES ON DATABASE drck_banking to django;
postgres=# \c drck_banking postgres;
drck_banking=# CREATE SCHEMA django;
drck_banking=# CREATE SCHEMA customer;
drck_banking=# CREATE SCHEMA staff;
drck_banking=# GRANT ALL ON SCHEMA django to django;
drck_banking=# GRANT ALL ON SCHEMA customer to django;
drck_banking=# GRANT ALL ON SCHEMA staff to django;
drck_banking=# exit
```

* Set up Django

```bash
python manage.py makemigrations
python manage.py migrate
```