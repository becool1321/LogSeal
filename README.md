# LogSeal – PKI-Based Secure Log Integrity Monitoring System

## Overview

LogSeal is a PKI-based secure log integrity monitoring system developed using Flask, OpenSearch, OpenSearch Dashboards, Docker, and modern cryptographic techniques. The system securely collects application logs, stores them in OpenSearch, cryptographically seals each daily log index using a SHA-256 hash chain, digitally signs the final seal using RSA, verifies log integrity, detects tampering and replay attacks, generates security alerts, and sends email notifications to administrators.
The project demonstrates how Public Key Infrastructure (PKI) can be integrated into centralized log management to provide confidentiality, integrity, authenticity, and non-repudiation of security logs.

---
# Features

## Web Application
* User Registration
* User Login
* User Logout
* Product Page
* Blog Page
* Shopping Cart
* Dashboard
* Admin Dashboard
---
## Logging

* User activity logging
* Admin activity logging
* Daily OpenSearch indices
* Automatic timestamp generation
* Structured JSON logging

Example index:

```
logs-YYYY-MM-DD
```

---

## Security Features

* SHA-256 Hash Chain
* RSA Digital Signature
* PKI Certificate Management
* Certificate Revocation List (CRL)
* PKCS#12 Keystore
* Replay Attack Protection
* Tamper Detection
* Hybrid Encryption
* Email Notification
* Security Alerts
* OpenSearch Alerting

---

# Technologies Used

| Component     | Technology            |
| ------------- | --------------------- |
| Backend       | Flask                 |
| Database      | SQLite                |
| Search Engine | OpenSearch            |
| Dashboard     | OpenSearch Dashboards |
| Cryptography  | RSA, SHA-256, AES-GCM |
| PKI           | OpenSSL               |
| Email         | Gmail SMTP            |
| Deployment    | Docker                |
| Automation    | Cron                  |

---

# Project Structure

```
logseal/
│
├── alerts/
├── crypto/
├── elastic/
├── notifications/
├── pki/
├── security/
├── static/
├── templates/
├── instance/
│
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── verify_index.py
├── seal_index.py
├── export_logs.py
├── automation_runner.py
├── auto_seal_runner.py
└── .env.example
```

---

# requirement.txt

Before running LogSeal install:

anyio==4.13.0
blinker==1.9.0
certifi==2026.5.20
cffi==2.0.0
click==8.4.1
cryptography==48.0.0
Flask==3.1.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
greenlet==3.5.1
idna==3.16
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.3
pycparser==3.0
python-dateutil==2.9.0.post0
python-dotenv==1.2.2
six==1.17.0
sniffio==1.3.1
SQLAlchemy==2.0.50
typing_extensions==4.15.0
urllib3==2.7.0
Werkzeug==3.1.8
opensearch-py==2.8.0
pycryptodome
---

# Python Requirements

All dependencies are listed inside

```
requirements.txt
```

Create virtual environment

```bash
python3 -m venv venv
```

Activate

Linux

```bash
source venv/bin/activate
```

W
Install packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Verify

```bash
pip list
```

---

# Environment Configuration

Create

```
.env
```

Example

```env
SECRET_KEY=CHANGE_ME

OPENSEARCH_URL=http://opensearch:9200

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_google_app_password

ALERT_RECIPIENT=your_email@gmail.com
```

Never upload

```
.env
```

Instead upload

```
.env.example
```

---

# Docker

Build project

```bash
docker compose up -d --build
```

Stop

```bash
docker compose down
```

Restart

```bash
docker compose restart
```

Check containers

```bash
docker ps
```

Expected

```
logseal-flask
logseal-opensearch
logseal-opensearch-dashboards
```

---

# Access URLs

Flask

```
http://localhost:5000
```

OpenSearch

```
http://localhost:9200
```

OpenSearch Dashboards

```
http://localhost:5601
```

---

# OpenSearch Configuration

Daily logs

```
logs-YYYY-MM-DD
```

Security Alerts

```
logseal-alerts
```

List indices

```bash
curl http://localhost:9200/_cat/indices?v
```

---

# OpenSearch Dashboards

Create two index patterns.

## Activity Logs

```
logs-*
```

Time field

```
timestamp
```

---

## Security Alerts

```
logseal-alerts
```

Time field

```
timestamp
```

---

# Dashboard 1

## LogSeal Activity Dashboard

Panels

* Events Over Time
* Event Type Distribution
* Top Users
* Admin Activities

---

# Dashboard 2

## LogSeal Security Dashboard

Panels

* Total Alerts
* Alerts by Severity
* Recent Tamper Alerts
* Replay Attack Alerts

---

# Running the Project

Build

```bash
docker compose up -d --build
```

Open browser

```
localhost:5000
```

Register user

Login

Generate logs

Open

```
localhost:5601
```

Open Discover

Observe logs.

---

# Sealing Logs

```bash
docker exec -it logseal-flask python seal_index.py
```

---

# Verifying Logs

```bash
docker exec -it logseal-flask python verify_index.py
```

Expected

```
INDEX VERIFIED
```

---

# Export Logs

```bash
docker exec -it logseal-flask python export_logs.py
```


# Admin Guide

LogSeal provides an administrative interface to manage log integrity, PKI components, security alerts, and system automation.

## Admin Login

Navigate to:

```text
http://localhost:5000/login
```

Login using the administrator account.

---

## Admin Dashboard

Navigate to:

```text
http://localhost:5000/admin
```

The dashboard provides access to:

* Dashboard Overview
* User Management
* Audit Logs
* Security Alerts
* Seal Metadata
* Verify Log Integrity
* Certificate Management
* PKCS#12 Keystore
* Certificate Revocation List (CRL)
* Encryption Status
* Automation Status
* Export Encrypted Archive
* Email Alert Status

---

# User Activity Logging

The following user events are automatically logged:

```text
USER_REGISTER
USER_LOGIN
USER_LOGOUT
VIEW_HOME
VIEW_PRODUCTS
VIEW_CART
VIEW_BLOG
```

Each log contains:

```text
timestamp
user_id
username
event_type
message
status
source
```

---

# Admin Activity Logging

The following administrator actions are also logged:

```text
ADMIN_LOGIN
ADMIN_VIEW_DASHBOARD
ADMIN_VIEW_USERS
ADMIN_VIEW_ALERTS
ADMIN_VIEW_SEALS
ADMIN_VERIFY_INDEX
ADMIN_VIEW_CRL
ADMIN_VIEW_KEYSTORE
ADMIN_EXPORT_ARCHIVE
ADMIN_VIEW_AUTOMATION
ADMIN_VIEW_CERTIFICATES
ADMIN_VIEW_EMAIL_ALERTS
```

---

# PKI Configuration

LogSeal uses a private Public Key Infrastructure (PKI).

Directory:

```text
pki/
```

Contains:

```text
Root CA
Certificates
Private Keys
Public Keys
PKCS#12 Keystore
Certificate Signing Requests
CRL
```

---

# Certificate Management

The project generates:

* Root CA
* Application certificate
* RSA key pair

Used for:

* Digital signatures
* Identity verification
* Certificate validation

---

# PKCS#12 Keystore

The PKCS#12 keystore stores:

* Private Key
* Certificate
* Certificate Chain

Navigate to:

```text
Admin → PKCS#12 Keystore
```

---

# Certificate Revocation List (CRL)

Navigate to:

```text
Admin → CRL Status
```

The page displays:

* Current CRL
* Revocation Number
* Certificate Status

CRL files are stored in:

```text
pki/ca/
```

---

# SHA-256 Hash Chain

Each log entry contributes to a cumulative hash chain.

Example:

```text
GENESIS
 ↓
Hash(Log1)
 ↓
Hash(Log2 + Previous Hash)
 ↓
Hash(Log3 + Previous Hash)
 ↓
Final Hash
```

This prevents unauthorized log modification.

---

# Digital Signature

The final hash is digitally signed using RSA.

Metadata stored:

```text
Index Name
Final Hash
Seal Version
Seal Timestamp
Algorithm
Digital Signature
```

---

# Seal Metadata

Navigate to:

```text
Admin → Seal Metadata
```

Each seal stores:

* Index Name
* Seal Version
* Total Logs
* Final Hash
* RSA Signature
* Timestamp

---

# Replay Protection

Replay protection prevents reuse of outdated seals.

Implementation:

```text
security/replay_protection.py
```

Latest seal versions are stored in:

```text
security/replay_state.json
```

If an older seal is presented:

```text
Replay Attack Detected
```

A critical alert is generated.

---

# Tamper Detection

Verification recalculates the hash chain.

If:

```text
Stored Hash
≠
Current Hash
```

Then:

```text
[TAMPER DETECTED]
```

is displayed.

---

# Tamper Demonstration

Generate logs.

Seal logs.

```bash
docker exec -it logseal-flask python seal_index.py
```

Modify a document.

Example:

```bash
curl -X POST http://localhost:9200/logs-YYYY-MM-DD/_update/DOCUMENT_ID \
-H "Content-Type: application/json" \
-d '{
"doc":{
"message":"TAMPERED BY ATTACKER"
}
}'
```

Verify:

```bash
docker exec -it logseal-flask python verify_index.py
```

Expected:

```text
[TAMPER DETECTED]
```

---

# Security Alerts

Security alerts are stored in:

```text
logseal-alerts
```

Alert types include:

```text
HASH_MISMATCH
INVALID_SIGNATURE
REPLAY_ATTACK
```

Severity:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

# Hybrid Encryption

Log archives are encrypted before export.

Algorithm:

* AES-GCM
* RSA Key Wrapping

Files are stored inside:

```text
crypto/archive/
```

Encrypted archives:

```text
crypto/encrypted_logs/
```

---

# Export Encrypted Archive

Navigate:

```text
Admin
→ Export Encrypted Archive
```

The system:

1. Exports logs
2. Encrypts archive
3. Saves encrypted archive

---

# Email Notifications

Two notification mechanisms exist.

## Flask Email

Uses:

```text
notifications/email_sender.py
```

SMTP configuration comes from:

```text
.env
```

Example:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_google_app_password
ALERT_RECIPIENT=recipient@gmail.com
```

---

## OpenSearch Notifications

Sender:

```text
gmail_sender
```

Credentials stored securely inside the OpenSearch keystore.

Commands:

```bash
docker exec -it logseal-opensearch \
/usr/share/opensearch/bin/opensearch-keystore add \
opensearch.notifications.core.email.gmail_sender.username
```

```bash
docker exec -it logseal-opensearch \
/usr/share/opensearch/bin/opensearch-keystore add \
opensearch.notifications.core.email.gmail_sender.password
```

Restart:

```bash
docker restart logseal-opensearch
```

---

# Automation

Cron automates verification and sealing.

Recommended:

```cron
*/5 * * * * docker exec logseal-flask python automation_runner.py >> automation.log 2>&1

*/10 * * * * docker exec logseal-flask python auto_seal_runner.py >> seal_automation.log 2>&1

55 23 * * * docker exec logseal-flask python auto_seal_runner.py >> final_daily_seal.log 2>&1
```

Automation logs:

```text
automation.log
seal_automation.log
final_daily_seal.log
```

---

# Testing Guide

## Test User Logging

* Register
* Login
* Visit pages
* Logout

Verify logs appear in OpenSearch.

---

## Test Admin Logging

Login as administrator.

Open:

* Dashboard
* Alerts
* CRL
* Seal Metadata
* Verify Index

Verify admin events appear in OpenSearch.

---

## Test Sealing

```bash
docker exec -it logseal-flask python seal_index.py
```

Expected:

```text
SEAL COMPLETE
```

---

## Test Verification

```bash
docker exec -it logseal-flask python verify_index.py
```

Expected:

```text
INDEX VERIFIED
```

---

## Test Tampering

Modify a log.

Verify again.

Expected:

```text
TAMPER DETECTED
```

---

## Test Replay Protection

Present an older seal version.

Expected:

```text
REPLAY_ATTACK
```

---

## Test Email

Trigger an alert.

Expected:

Administrator receives an email.

---

## Test Dashboards

Open:

```text
http://localhost:5601
```

Verify:

Activity Dashboard

Security Dashboard

---

# Common Commands

Start:

```bash
docker compose up -d --build
```

Stop:

```bash
docker compose down
```

Restart:

```bash
docker compose restart
```

Flask logs:

```bash
docker logs logseal-flask
```

OpenSearch logs:

```bash
docker logs logseal-opensearch
```

Dashboards logs:

```bash
docker logs logseal-opensearch-dashboards
```

List indices:

```bash
curl http://localhost:9200/_cat/indices?v
```

Seal:

```bash
docker exec -it logseal-flask python seal_index.py
```

Verify:

```bash
docker exec -it logseal-flask python verify_index.py
```

---

# Troubleshooting

## Email not sending

* Verify Google App Password
* Restart OpenSearch
* Check sender name
* Verify SMTP configuration

---

## Dashboard shows no data

* Confirm index patterns
* Verify timestamp field
* Refresh dashboards

---

## Verification fails

* New logs may have been generated after sealing.
* Run:

```bash
docker exec -it logseal-flask python seal_index.py
```

before verifying again.

---

# Future Improvements

* Multi-factor authentication
* Certificate auto-renewal
* Hardware Security Module (HSM)
* SIEM integration
* Kubernetes deployment
* Role-Based Access Control (RBAC)
* Immutable object storage
* Distributed cluster support

---

# License

This project was developed for academic purposes as part of a cybersecurity coursework project.

It demonstrates secure log integrity monitoring using PKI, OpenSearch, Docker, and modern cryptographic techniques.
