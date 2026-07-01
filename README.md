# LogSeal – PKI-Based Secure Log Integrity Monitoring System

## Overview
LogSeal is a PKI-based secure log integrity monitoring system developed using Flask, OpenSearch, OpenSearch Dashboards, Docker, and modern cryptographic techniques. The system securely collects application logs, stores them in OpenSearch, cryptographically seals each daily log index using a SHA-256 hash chain, digitally signs the final seal using RSA, verifies log integrity, detects tampering and replay attacks attempts, generates security alerts, and sends email notifications to administrators.
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
---
## Security Features

- SHA-256 Hash Chain
- RSA Digital Signatures
- PKI Certificate Management
- Certificate Validation
- Replay Attack Detection
- Tamper Detection
- AES-256 Encrypted Log Archive
- Email Notifications
- Security Alerts
- OpenSearch Alerting
---
# Technologies Used

| Component     | Technology                      |
|---------------|---------------------------------|
| Backend       | Flask                           |
| Database      | SQLite                          |
| Search Engine | OpenSearch                      |
| Dashboard     | OpenSearch Dashboards           |
| Cryptography  | RSA-2048, SHA-256, AES-256      |
| PKI           | OpenSSL                         |
| Email         | OpenSearch Notifications, Gmail SMTP |
| Deployment    | Docker & Docker Compose         |
| Automation    | Cron                            |
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
└── .env (create from .env.example)
```
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
Install packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

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
# Docker
Build project
```bash
docker compose up -d --build
```
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
Security Alert
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

# Running the Project
Build
```bash
docker compose up -d --build
```
Flask:
http://localhost:5000

OpenSearch:
http://localhost:9200

OpenSearch Dashboards:
http://localhost:5601

---

---
## Log Sealing

LogSeal automatically seals each daily OpenSearch index using a SHA-256 hash chain. After all log entries for a given day are collected, a final hash is generated and digitally signed using the application's RSA private key. The resulting seal metadata is stored for later integrity verification.

## Integrity Verification

The system recalculates the SHA-256 hash chain of the selected log index and compares it with the previously sealed value. It then validates the RSA digital signature using the corresponding public certificate. Any mismatch indicates that the logs have been modified after sealing.

## Secure Log Archiving

LogSeal supports exporting completed log indices into encrypted archives for long-term storage. Archived logs are protected using hybrid encryption, ensuring confidentiality while preserving integrity and authenticity for future forensic investigations.

## Security Monitoring

Whenever tampering, invalid signatures, or replay attempts are detected, LogSeal generates security alerts and stores them in a dedicated OpenSearch alert index. These alerts can be monitored through OpenSearch Dashboards, providing administrators with centralized visibility into security events.


## Automation

LogSeal supports automated integrity verification and daily index sealing using scheduled Cron jobs on Linux systems. Automation enables regular verification of log integrity without requiring manual execution and ensures that each daily OpenSearch index is cryptographically sealed after log collection has finished.
```cron
*/5 * * * * cd /path/to/logseal && python3 automation_runner.py >> automation.log 2>&1
*/10 * * * * cd /path/to/logseal && python3 auto_seal_runner.py >> seal_automation.log 2>&1
55 23 * * * cd /path/to/logseal && python3 auto_seal_runner.py >> final_daily_seal.log 2>&1
```
Example Cron Schedule

• Verify integrity every 5 minutes
• Perform scheduled sealing every 10 minutes
• Create the final daily seal before midnight

## OpenSearch Dashboards

OpenSearch Dashboards provides centralized monitoring of application logs and security alerts. Two index patterns should be created:

| Index Pattern | Time Field |
|---------------|------------|
| logs-* | timestamp |
| logseal-alerts | timestamp |

These dashboards allow administrators to review user activity, detect tampering attempts, and monitor replay attack detections from a single interface.

## Running the Project

After configuring the environment variables and building the Docker containers, the Flask application, OpenSearch, and OpenSearch Dashboards start automatically. Users can register, log in, generate application activities, and monitor logs through the web interface while administrators can verify log integrity and review security alerts from OpenSearch Dashboards.

# License
This project was developed for academic purposes as part of a cybersecurity coursework project.
It demonstrates secure log integrity monitoring using PKI, OpenSearch, Docker, and modern cryptographic techniques.
