Todo:
- [x] Implement .env variables
- [ ] Improve folder structure
- [x] Rename celery app
- [x] Add Flower
- [ ] Add Postgres backend
- [x] Add container names
- [x] .env vars in settings
- [ ] Make container root folder PROJECT_NAME
- [ ] Celery config (/usr/local/lib/python3.11/site-packages/celery/platforms.py:829: SecurityWarning: You're running the worker with superuser privileges: this is absolutely not recommended!)
- [ ] Redis (Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf)
- [ ] Update prompt schemas to handle "backed by" or "investors" so they're not extracted as company names

prompts:


The next phase will be to implement scaping of the different websites found in the initial AI processing phase. The websites in the JSON output will be scaped and the data temporarily stored in a database. The data collected will be later sent to GTP 4 for further analysis (using AIService). 

Help me understand the next steps of the project before specifying implementation code. 

A few assumptions:

- I believe scrapegraph is the best library to use. 
- Since these tasks will take some time, the use of Celery is recommended.
- Celery and Redis are already implemented in this project.

Questions
- Should we use Redis for data storage?
- What would you recommend as the best workflow?
- What is the recommended updates to file structure?

