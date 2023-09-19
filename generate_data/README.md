# Generation of Data into Customer Schema

## Dataset Generation
This script generates a random dataset that populates the Customer Schema and the auth_table of Users. It makes use of fixtures to load the data directly into the existing database, so it is mainly useful for testing of anonymity.

# Warnings
General:
* Assumes that id in django.auth_user starts from 1 (can be modified)
* Number of auth_users and transactions must be modified in the code
* Due to primary key concerns, try to run script only once or clear database using delete.sql before running agian

In Transactions table:
* Only checks if sender_id and recipient_id is different 
* Only checks if sending amount < sender's balance
* Does not minus amount transacted from balance


## Setup Instructions
1. Ensure that auth_user only contains all customer data or database is empty

2. Run python script
```python
python manage.py shell < generate_data/generate.py
```
3. Check database


