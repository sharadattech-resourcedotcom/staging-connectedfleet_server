JSON=$(curl -X POST -H "Content-Type: application/json" -d '{
        "username" : "stefan123",
        "password" : "stefan"
        }' 127.0.0.1:8000/session/login
)
#to install jq just simply "sudo cp jq /usr/bin"
ACCESS=$(echo "$JSON" | jq '.data.access')
ID=$(echo "$JSON" | jq '.data.token_id')

curl -X POST -H "Content-Type: application/json" -d '{
        "token_id" : '$ID',
        "access" : '$ACCESS',
        "trip_id" : 1,
	"end_date" : "2014-07-23 12:00:00"
        }' 127.0.0.1:8000/driver/endtrip
