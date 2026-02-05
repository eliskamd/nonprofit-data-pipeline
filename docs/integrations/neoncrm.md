# NeonCRM API Integration

## Overview
Cloud-based CRM with modern REST API (use v2 for new projects)

## Authentication
- Method: API Key
- Location: Settings > User Management > User > API Key
- Create dedicated user for integration
- Storage: .env file (NEON_API_KEY, NEON_ORG_ID)

## Base URLs
- API v2: https://api.neoncrm.com/v2
- API v1: https://api.neoncrm.com/neonws/services/api (legacy)

## Key Endpoints (API v2)
- GET /accounts - List accounts (constituents)
- GET /accounts/{id} - Get account details
- POST /accounts - Create account
- PATCH /accounts/{id} - Update account
- GET /donations - List donations
- POST /donations - Create donation
- GET /events - List events
- GET /customFields - Work with custom fields

## Authentication Header
```
Authorization: Bearer {API_KEY}
```

## Rate Limits
Not publicly specified - monitor for 429 errors

## Features
- Webhook support for real-time updates
- Custom objects (create your own tables!)
- Sandbox available for testing
- Make/Zapier integrations

## Partner Requirements
If building for others:
- Complete integration survey
- Provide documentation
- Attend product demo
- Test in sandbox

## Data Schema
[Will document JSON responses in next phase]