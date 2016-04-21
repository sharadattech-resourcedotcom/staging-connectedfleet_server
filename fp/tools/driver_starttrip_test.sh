JSON=$(curl -X POST -H "Content-Type: application/json" -d '{
        "username" : "michalrychlik@appsvisio.com",
        "password" : "michal123"
        }' 127.0.0.1:8000/session/login
)
#to install jq just simply "sudo cp jq /usr/bin"
ACCESS=$(echo "$JSON" | jq '.data.access')
ID=$(echo "$JSON" | jq '.data.token_id')

curl -X POST -H "Content-Type: application/json" -d '{
        "token_id" : '$ID',
        "access" : '$ACCESS',
        "estimated_time" : {"days" : 1, "hours" : 25, "minutes" : 0 },
	"start_location" : "Gdansk",
	"end_location" : "Warszawa",
	"start_date" : "2014-07-22 19:15:00",
        "start_lat" : 54.377,
        "start_lon" : 18.6099,
        "end_lat" : 52.25,
        "end_lon" : 21.0
        }' 127.0.0.1:8000/driver/starttrip

