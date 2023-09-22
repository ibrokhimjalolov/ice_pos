echo "Dumping database..."
pg_dump "host=localhost port=5432 dbname=ice_pos user=postgres password=postgres" | gzip > /var/db_dumps/ice_pos_$(date +\%Y_\%m_\%d_\%H:\%M:\%S).sql.gz
echo "Done."