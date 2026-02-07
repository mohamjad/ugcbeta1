setup guide

complete setup instructions for ugc intelligence backend. you need python three ten or higher postgresql fourteen or higher redis seven or higher if you want caching and docker with docker-compose if you want containerized deployment.

quick start begins with cloning the repository and changing into the directory. create a virtual environment activate it then install requirements from the requirements file. on windows the activation command uses backslashes instead of forward slashes.

configuration involves copying the example config and env files then editing them with your settings. in config.yaml you can adjust time windows configure clustering thresholds and set validation parameters. in the env file set your database url as a postgresql connection string set your tiktok api key if you're using that api and set your redis url if you want caching.

database setup requires postgresql to be running. create the database if it doesn't exist using createdb with the database name. then initialize the schema by running the init database script. this creates all the tables and indexes you need.

running the server is just executing main.py. the server starts on localhost port eight thousand. api docs are automatically available at the docs endpoint where fastapi generates interactive documentation.

docker deployment uses docker-compose up with the detach flag. this starts postgresql on port five four three two redis on port six three seven nine and the backend api on port eight thousand. the database gets automatically initialized on first startup so you don't need to run the init script manually.

verification happens through the health check endpoint. hit it with curl and you should get back a status of healthy with version number component statuses and current metrics. if something's wrong this will tell you.

testing uses pytest. run it from the tests directory and it will execute all test files following the pytest naming conventions.

production considerations include using connection pooling for the database proper backups regular log rotation and monitoring. enable redis for frequently accessed data to reduce database load. configure log rotation and set up monitoring dashboards. enable auth required in config.yaml for security. use a load balancer for horizontal scaling. set up health checks and alerts so you know when things break.

troubleshooting database connection errors means verifying postgresql is running checking the database url in your env file and making sure the database actually exists. import errors usually mean your virtual environment isn't activated or requirements didn't install properly so try running pip install again. port already in use means something else is using port eight thousand so either change the port in config.yaml or kill whatever process has that port.
