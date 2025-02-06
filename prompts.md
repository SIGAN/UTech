Initial, Simplified
-----
I am building new event planner application called "Eve". Eve should be very simple app, we need to support event and event comments entities. 
Event Fields: id (integer), title, description, place, start_time, end_time, food (string), drinks (string), program, parking_info, music, theme, age_restrictions. 
EventComment Fields: id, event_id, user_id, message, rating (integer, default 0). 
Folder structure: "/workspace/eve", "/workspace/eve/data" (SQLite database, give broad RW access to both FOLDER and DATABASE file), "/workspace/eve/backend", "/workspace/eve/frontend". Use thin folder structure. backend folder should contain directly backend code. Frontend - the frontend code, do not nest deep.
Backend should be Python 3.11, FastAPI, SqlAlchemy, Sqlite, and built using packages with __init__.py. 
Frontend should be angular and angular material with deeppurple-amber theme as default. 
Use embedded SQLite for persistance. 
Frontend uses HTTP port 2020, Backend uses HTTP port 2021. HTTPS is not supported. 
User authenticated by providing just email (no password!), session is just UUID and maintained in database, session expires in 8 hours, session id is stored in localStorage, session is passed as auth header. 
All backend endpoints require session, except login (which is available). 
Backend should use "use case" pattern, where controllers take care of HTTP and API concerns, while "use case" take care of business logic, and we should be able to call use cases even from console app. 
Only author can edit or delete entities, so use authorEmail field in all entities. 
UI home page should have list of upcoming events, my events. UI should allow full CRUD. CORS. 
All dates are in UTC in backend, frontend is responsible to convert to/from UTC. 
Please prepare and keep updated README.md with all tech details, archiutecture, design, pre-requisites, install, build, run instructions, application business logic, database schema and folder structure, additionally LLM should be able to fully gather entire context using this file, also humans should be able to use this file to start development. 
Do not use in-memory SQLite, even for tests. 
Please init database first and assign permissions. 
Check/define schema, Check/Define Backend, Run/Build unit tests, Run/Build API testing script (output actions, expectations, and re-read and output modified entity after each action). In the end it should cleanup everything (but eve.db file must always stay!).
Make sure to ask before upgrading any framework or any approach change. 
All scripts must run within context of "/workspace/eve", so that all SQLite database paths are "data/eve.db", thus all scripts must be stored in the root "/workspace/eve". Do not hardcode "/workspace/eve", just always store and start scripts at "/workspace/eve".

Follow up
-----
Context: 
I am building new event planner application called "Eve". It is in "/workspace/eve", please read README.md to acquire full context, you must follow what is documented. 
Please init database first and assign permissions. Run unit tests, run API testing script (output actions, expectations, and re-read and output modified entity after each action). 
Please update README.md once something changes and completed. 
PORTS MUST BE: Frontend - 2020, Backend - 2021. 
All scripts must be in eve folder AND it should run the rest from the context of "/workspace/eve". All database paths are "data/eve.db". Do not hardcode "/workspace/eve", just always store and start scripts at "/workspace/eve". 
Ask for explicit permission to change any existing approach, framework. 
All time MUST BE is in UTC on the backend (database, API backend), all API clients and frontend converts to/from local. 
Use sudo to install global packages/tools. Identify current OS. 
Other python and node processes are running, please kill only Eve processes.
Keep e2e test timeouts as-is, if something fails - it is not timeout.
Use backend, frontend, and test logs to identify issues with e2e tests.
Use setup.sh to start.
Task: ...

