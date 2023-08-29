# DRCKBankingSystem

DRCK Banking System
This is from application-skeleton-branch

## Set Up Instructions

### Virtual Environment

I am using Anaconda to set up the vitual environment with Python 11.

1. `wget https://repo.anaconda.com/archive/Anaconda3-2023.07-2-Linux-x86_64.sh`
2. `sudo Anaconda3-2023.07-2-Linux-x86_64.sh`
3. `conda env create --file=conda_environment.yml` which was created using `conda env export > conda_environment.yml`
4. `conda activate drck_banking`

If you are not using Anaconda, set up using pip.

1. `pip install -r requirements`

### Start Server Locally

`python manage.py runserver`
