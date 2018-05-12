
# Fumble



## Getting Started
These instructions will get you a copy of the project up and running on your local machine.

### Installing
You'll need Docker - if you're on macOS you can get it [here](https://www.docker.com/docker-mac).

Clone the repository:
```
git clone https://github.com/bf6/fumble
cd fumble/
```
Start the containers in the background:
```
docker-compose up --build -d
```

The API should now be accessible at `localhost:8000`.

### Using the API

#### POST a user's location to the API
```
curl -X POST \
    -d '{"userId": 13, "lat": -50.1, "lng": 42.0, "time": 16043123461}' \
    "localhost:8000" | python -m json.tool
```
You should get back a confirmation:
```
{
    "message": "Accepted!"
}
```
If your POST is incorrect,
```
curl -X POST \
    -d '{"userId": "13", "lat": -50.1, "lng": 42.0, "time": 16043123461}' \
    "localhost:8000" | python -m json.tool
```
an error message is returned:
```
{
    "message": "userId should be of type int"
}
```
```
curl -X POST \
    -d '{"userId": 13, "lng": 42.0, "time": 16043123461}' \
    "localhost:8000" | python -m json.tool
```
```
{
    "message": "Missing required field: lat"
}
```
#### GET a user's matches
```
curl "localhost:8000?userId=13" | python -m json.tool
```
```
{
    "items": [
        {
            "from": 14,
            "to": 13,
            "time": {
                "$date": 1526144562371
            }
        },
        {
            "from": 15,
            "to": 13,
            "time": {
                "$date": 1526144567246
            }
        },
        {
            "from": 16,
            "to": 13,
            "time": {
                "$date": 1526144618150
            }
        }
    ]
}
```

## Running the tests

`docker-compose run api pytest`

## Design & Discussion

When a device sends the user's coordinates to the app a record is upserted into MongoDB. MongoDB was chosen because it has native support for geospatial queries, which are central to the application. The `user_location` records have a TTL of 30 seconds. When the record is created or updated, a task to find matches is sent to RabbitMQ, then consumed by one or more workers. Given a userID, datetime, and coordinates, we find the `user_locations` that are near (<= 150 meters) and within 60 seconds of the newly updated record. For each one, we create two `match` records.

Optimizations include using Kafka and partitioning on geohash. Then, individual consumers could be responsible for messages from a specific geographical area of configurable size. We might want to avoid queuing up a task for every updated `user_location` - instead, consumers would read from the `user_locations` table and generate the matches in real-time as new data comes in.

Another optimization would be batching writes - with GPS updates flowing in continuously from a large number of devices, a significant performance gain could be achieved by avoiding a write for every one.



## Built With

* [pymongo](https://github.com/mongodb/mongo-python-driver) - The Python driver for MongoDB
* [Celery](https://github.com/celery/celery) - Asynchronous tasks


## Authors

* **Brian Fernandez** - [github](https://github.com/bf6)
