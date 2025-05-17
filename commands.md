
# Docker

## Compose container
```
docker-compose up -d --build
```

## Enter container
```
docker exec -it pg-cont bash
```

## Stop container
```
docker stop pg-cont
```

## Remove container and volume
```
docker rm pg-cont; docker volume rm db_files_postgres_data
```
### Remove while shutdown
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

# Postgres

## Read sql-file

```
psql -U <user> -d <DB> -f <file>
```

### Read setup
```
psql -U admin -d lib_mgmt -f setup.sql
```



