#!/bin/bash

# Test script for Pokemon MCP authentication flow

echo "Testing Pokemon MCP authentication flow..."

# Ensure services are running
echo "1. Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "2. Waiting for services to be ready..."
sleep 30

# Test auth server health
echo "3. Testing auth server health..."
curl -s http://localhost:8000/health | jq .

# Test MCP server health
echo "4. Testing MCP server health..."
curl -s http://localhost:8001/health | jq .

# Test JWKS endpoint
echo "5. Testing JWKS endpoint..."
curl -s http://localhost:8000/.well-known/jwks.json | jq .

# Register a test client
echo "6. Registering test client..."
CLIENT_RESPONSE=$(curl -s -X POST http://localhost:8000/register \
    -H 'Content-Type: application/json' \
    -d '{"client_name":"test-client","grant_types":["client_credentials"],"token_endpoint_auth_method":"client_secret_post"}')

echo "Client registration response: $CLIENT_RESPONSE"

CLIENT_ID=$(echo $CLIENT_RESPONSE | jq -r '.client_id')
CLIENT_SECRET=$(echo $CLIENT_RESPONSE | jq -r '.client_secret')

echo "Client ID: $CLIENT_ID"
echo "Client Secret: $CLIENT_SECRET"

# Get access token
echo "7. Getting access token..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/token \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d "grant_type=client_credentials&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET&scope=read")

echo "Token response: $TOKEN_RESPONSE"

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')
echo "Access Token: $ACCESS_TOKEN"

# Test protected API endpoint
echo "8. Testing protected API endpoint..."
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
    "http://localhost:8001/pokemon/pikachu" | jq .

echo "Test complete!"
