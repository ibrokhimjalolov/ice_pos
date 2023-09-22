docker compose -f local.yml build
docker compose -f local.yml up -d
docker exec -it ice_pos_db service cron start
