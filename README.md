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

## For testing purposes

```sql
postgres=# CREATE DATABASE test_drck_banking;
postgres=# GRANT ALL PRIVILEGES ON DATABASE test_drck_banking to django;
postgres=# \c test_drck_banking postgres;
drck_banking=# CREATE SCHEMA django;
drck_banking=# CREATE SCHEMA customer;
drck_banking=# CREATE SCHEMA staff;
drck_banking=# GRANT ALL ON SCHEMA django to django;
drck_banking=# GRANT ALL ON SCHEMA customer to django;
drck_banking=# GRANT ALL ON SCHEMA staff to django;
drck_banking=# exit
```

To run tests: `python manage.py test --keepdb`. This is because with Postgres, Django cannot create new schemas on its own, so we have to preserve the above setup. By default, all entries should be deleted after testing.

## For code coverage

```basg
pip install coverage==7.3.1
coverage run manage.py test --keepdb
coverage xml -o coverage-reports/coverage.xml
```
