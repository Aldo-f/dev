---
name: mail-tm-scripting
description: Automate mail.tm message stats and cleanup with domain validation and token authentication.
category: automation
tags: [email,pi5,mailtm]
---

# Mail.tm Scripting Skill
## Purpose
Automate retrieval of mail.tm message statistics and manage email volume by deleting old messages.

## Prerequisites
- curl
- jq
- Valid mail.tm account (must use @mail.tm domain)
- Basic shell scripting knowledge

## Authentication Workflow
1. **Token-based authentication** required:
   - First get token via POST to /token endpoint
   - Store token securely in script
   - Use Bearer token in Authorization header for subsequent requests

## Core Functionality
1. Authenticate using token
2. Fetch messages and calculate total size
3. If size > 40MB, delete oldest messages (up to 10 oldest)
4. Output:
   - Total messages count
   - Subject frequency report
   - Deletion confirmation count

## Key Enhancements from Recent Session
- **Domain validation**: Must use @mail.tm domain (web-library.net is rejected by API)
- **Counter tracking**: Implements JSON-based counters for session persistence
- **Deletion accounting**: Logs exact number of messages deleted per run

## Notes
- Test with a small dataset first
- Store credentials securely (environment variables preferred)
- Keep deleted count JSON file for audit trails
