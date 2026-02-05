# Raiser's Edge NXT (Blackbaud SKY API) Integration

## Overview
Industry-leading nonprofit CRM with comprehensive REST API

## Authentication
- Method: OAuth 2.0
- Developer Portal: developer.blackbaud.com/skyapi
- Create developer account (free)
- Register application to get Client ID/Secret
- OAuth flow: Authorization Code Grant

## Base URL
https://api.sky.blackbaud.com/constituent/v1/

## Key Endpoints
- GET /constituents - List constituents
- GET /constituents/{id} - Get constituent details
- POST /constituents - Create constituent
- PATCH /constituents/{id} - Update constituent
- GET /gifts - List gifts
- POST /gifts - Create gift
- GET /lists - Access saved lists
- POST /query - Run dynamic queries

## Rate Limits
- Per-minute quotas (contact support to increase)
- Quota limits (monthly cap)
- Monitor usage in developer console

## Data Latency
List endpoints may have 5-15 minute ETL lag
Direct endpoints (GET /constituents/{id}) are real-time

## Integration Examples
- Microsoft Power Automate connector
- iWave (wealth screening)
- Hundreds of marketplace partners

## Data Schema
[Will document JSON responses in following phase]

## OAuth Flow
1. Redirect user to authorize URL
2. User grants permission
3. Receive authorization code
4. Exchange code for access token
5. Use token in API requests
6. Refresh token when expired