# K-anonymisation of Database

## K-anonymisation
Performs K-anonymity on transaction history stored in database and outputs k-anonymised data based on the user's k-value input and use case

Usage:
```python
python manage.py shell < staff/anonymise/overall.py
```

# Overall.py
Contains functions to take in user input and perform query on both original data and anonymised data. Processes data for output

# Anonymiser.py
Performs k-anonymity, using strict mondrian algorithm 

# Mondrian.py
Contains function which implements Mondrian algorithm to anonymise data. Adapted from: 

# read_my_withdrawal.py
Reads in withdrawal data from database and processes it based on the respective quasi-identifiers and sensitive attributes



## Warnings
* The scripts will print out data files with all information for testing purposes (remove later)