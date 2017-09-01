# BTC VIZ - TODO

## Setup
1. Setup bitcoin-core, bitcoin-abe and postgresql. Remember to point PG data to a large disk if required
2. Setup postgres database and user for bitcoin-abe
3. Point bitcoin-abe to the .bitcoin directory as well as the postgres instance setup by bitcoin core. 
4. (Optional) Delete some stuff from .bitcoin to make loading faster
5. Run bitcoin-abe to seed database
6. Export the database to a csv file using `python export-tx-to-csv.py --config abe-pg.conf`
7. Send the data to neo4j using `python load-tx-to-neo.py`
8. Start the Flask webserver `python app.py` and navigate to localhost:3000 
