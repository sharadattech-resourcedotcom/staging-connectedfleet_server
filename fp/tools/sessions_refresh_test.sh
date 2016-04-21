JSON=$(curl -X POST -H "Content-Type: application/json" -d '{
        "username" : "stefan123",
        "password" : "stefan"
        }' 127.0.0.1:8000/session/login
)
echo "$JSON"
#to install jq just simply "sudo cp jq /usr/bin"
REFRESH=$(echo "$JSON" | jq '.data.refresh')
ID=$(echo "$JSON" | jq '.data.token_id')

curl -X POST -H "Content-Type: application/json" -d '{
        "token_id" : '$ID',
        "refresh" : '$REFRESH'
        }' 127.0.0.1:8000/session/refresh
