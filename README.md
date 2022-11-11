# Lion Network - W4111 Project 1
Harshini Ramanujam - hr2358 <br />
Donghan Kim - dk3245

# Developer references:
1. Set up virtual env `python3 -m venv env`
2. Source the env `source env/bin/activate`
3. Install dependencies `pip install -r requirements.txt`
4. Set environment variables for DB_USER, DB_PASSWORD, DB_SERVER
5. Run server on local `python run.py`

Fixes for later reference:
1. Ran `sudo apt-get install libpq-dev` to install psycopg2 on google cloud's VM

# Environment Variables
If you want to use .env file to store environment variables here is what you can do:
```bash
# navigate to project directory
cd/lionnetwork

# create .env file and enter your DB user name, password, and server link
vim .env

# extract environment variable's in db.py
from decouple import config
...
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_SERVER = config('DB_SERVER')
```
