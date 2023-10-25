# Logging

## Login Logs

The Login Logs records all login attempts.
Logs are marked with higher severity if:

1. Login attempt was unsuccessful.
2. Many unsuccessful attempts were executed within a short timeframe (5 minutes).

This log aims to identify a bruteforcing attack where an attacker repeatedly attempts to log into a user's account.

## Access Control Logs

The Access Control Logs records all unauthorised attempts to access an API.
Logs are marked with higher severity if:

1. Multiple attempts were made by the same user.
2. Multiple attempts were made by the same IP address.

This log aims to identify the situation where an unauthorised user attempts to bypass both the frontend and access control by directly accessing APIs that they are not authorised to.

## Conflict of Interest Logs

The Conflict of Interest Logs records all approval of customer tickets.
Logs are marked with higher severity if for each ticket:

1. The usernames of the customer and staff are the same.
2. The IP addresses of the customer and staff are the same.

This log aims to identify the misuse of a staff account by a staff who also owns a customer account. Specifically, it identifies the situation where a staff self-approves a ticket that they opened as a customer.
