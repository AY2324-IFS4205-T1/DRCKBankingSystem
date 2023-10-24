# DRCK Banking System

The DRCK Banking System is a software platform developed to meet the diverse needs of multiple stakeholders within the banking ecosystem.
This comprehensive web-based application offers a user-friendly interface to access and manage banking services securely.
The system consists of four subsystems, each designed to fulfil specific functionalities, and it adheres with robust data management, access control and anonymisation principles.

The primary goal of DRCK Banking System is to provide an efficient and user-friendly bank service for customers, allowing them to manage their accounts, conduct financial transactions and interact with the bank system efficiently.
Additionally, ensuring the privacy and security of customer data is a top objective. Hence, access control mechanisms and encryption protocols are implemented to safeguard sensitive information.

The system also aims to meet compliance and regulatory requirements.
This is to ensure that compliance officers have access to relevant logs to ensure that the bank operates within legal frameworks.
Lastly, the project aims to enable valuable research through data anonymisation.
Researchers are provided access to anonymised banking data for analysis and business insights.

## Roles and Access

|   Roles  | Title                 | Access                                                                                                                                                                                                                                                                                                                      |
|:--------:|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Customer | -                     | customer/register: register as customer <br>customer/login: login as customer <br>customer/setup: set up 2FA <br>customer/verify: verify 2FA OTP <br>customer/dashboard: customer homepage <br>customer/accounts: view accounts <br>customer/tickets: view and create tickets <br>customer/atm: deposit and withdraw <br>customer/transfer: make a transfer |
| Staff    | -                     | staff/login: login as staff <br>staff/setup: set up 2FA <br>staff/verify: verify 2FA OTP <br>staff/dashboard: staff homepage                                                                                                                                                                                                            |
| Staff    | Ticket Reviewer       | staff/tickets: view, approve, and reject customer tickets                                                                                                                                                                                                                                                                   |
|          | Auditor               | staff/logs: view different sets of logs                                                                                                                                                                                                                                                                                     |
|          | Anonymisation Officer | staff/anon: view anonymised data statistics and set k-values for researcher                                                                                                                                                                                                                                                 |
|          | Researcher            | staff/anon: view query results and download k-anonymised data                                                                                                                                                                                                                                                               |

## Access to Website

You can access the DRCK Banking System at <https://ifs4205-23s1-1-1.comp.nus.edu.sg/>.
The staff portal can be access via <https://ifs4205-23s1-1-1.comp.nus.edu.sg/staff/login>.

## Customer Account Information

No customer accounts are prepared for the team.
Instead, the team is recommended to register for their own accounts on the website.

## Staff Account Information

Each member of each team is given 4 staff accounts.
The username is in the format `group<group_number>_user<user_number>_<title>`.
For example:

* `group1_user1_Ticket_Reviewer`
* `group3_user2_Auditor`
* `group2_user4_Researcher`
* `group3_user4_Anonymity_Officer`

The password for all sample accounts is provided in the summary report.
Note that you will be required to set up two-factor authentication upon login.
