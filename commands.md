
# Setup
## Compose container
```
docker-compose up -d --build
```
## Enter container
```
docker exec -it mongo-cont bash
```

## Move
```
cd /root/db_files
```

## Read setup
```
mongosh lib_mgmt --authenticationDatabase "admin" -u "admin" -p 1234 /root/db_files/setup.js
```

## Start app
```
python app.py
```

# Docker

## Compose container
```
docker-compose up -d --build
```

## Enter container
### MongoDB-Shell
```
docker exec -it mongo-cont mongosh
```

### MongoDB-Shell
```
docker exec -it mongo-cont bash
```

## Stop container
```
docker stop mongo-cont
```

## Remove container and volume
```
docker rm mongo-cont; docker volume rm library_management_task_mongo_data
```
### Remove while shutdown (with data -v)
```
docker-compose down -v
```

## Status of containers
```
docker ps --all
```

## List volumes
```
docker volume ls
```

# Mongo DB

## Load setup data (from outside of the container)

```
docker exec -it mongo-cont mongosh lib_mgmt --authenticationDatabase "admin" -u "admin" -p 1234 /root/db_files/setup.js
```

## Load setup data (from inside of the container)

```
mongosh lib_mgmt --authenticationDatabase "admin" -u "admin" -p 1234 /root/db_files/setup.js
```


