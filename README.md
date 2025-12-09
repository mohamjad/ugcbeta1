ugc intelligence backend

production-ready transparent architecture for social media trend detection. this backend system provides a completely transparent non-black-box solution for detecting early-stage social media trends across tiktok xiaohongshu rednote and other platforms. unlike traditional ml-heavy approaches that obscure their logic this system makes every decision visible traceable and adjustable.

the system works by ingesting posts from multiple platforms normalizing them into a consistent format then applying temporal windows to focus on recent content. posts get clustered using rule-based hashtag analysis which groups related content without any ml black boxes. clusters get validated through multi-factor checks looking at creator diversity cross-platform presence and regional spread. validated trends get turned into proof tiles with actionable insights complete evidence and urgency recommendations.

all metrics use transparent formulas documented in the code. engagement rate is likes plus comments plus shares divided by views. velocity score is total engagement divided by hours since first seen. creator diversity is unique creators divided by total posts. cluster health combines diversity engagement and velocity with configurable weights. validation confidence comes from creator count and region spread.

installation is straightforward. create a virtual environment install requirements copy the example config and env files then edit them with your settings. initialize the database with the init script then run main.py. the server starts on port 8000 and api docs are available at the docs endpoint.

configuration happens through config.yaml and environment variables. you can adjust time window durations clustering thresholds validation parameters and platform-specific settings. everything is documented and has sensible defaults.

api endpoints include posting posts for ingestion running the discovery pipeline getting proof tiles fetching trend details and checking system health. all endpoints have request validation error handling and proper response models.

for development run the test suite with pytest. the codebase is structured cleanly with separation between core business logic data access api layer and utilities. everything is type hinted and error handling is comprehensive.

the system scales horizontally through stateless api design separate ingestion and processing services and proper database indexing. caching support exists through redis though it's optional. the architecture supports partitioning by platform and time window as data grows.

transparency is built into every layer. all metric formulas are documented in code. clustering rules are explicit and adjustable. validation thresholds are configurable. proof tiles include complete evidence chains. logging happens at every decision point so you can trace exactly why a trend was flagged or why a cluster was formed.

this is proprietary software built for production use with proper error handling logging and deployment tooling.
