#!/bin/bash
curl -X POST -H "Content-Type: application/json" -d '{
        "username" : "kuba@appsvisio.com",
        "password" : "kuba123"
        }' http://localhost:8001/session/login
