architecture overview

transparent rule-based trend detection system with no black-box ml algorithms. the whole thing runs on explicit rules you can read and adjust rather than opaque models that hide their reasoning.

the system flows from api layer down through core business logic into the data layer. requests come into fastapi endpoints which hand off to the core modules. ingestion collects posts from platforms and normalizes them. clustering groups related content using hashtag analysis. validation checks if clusters represent real trends. proof generation turns validated trends into actionable insights. all of this sits on top of repositories that talk to postgresql with optional redis caching.

data flows like this. posts get collected from platforms and normalized into contentpost format. then they get filtered by temporal windows so you're only looking at recent content. the clustering engine groups posts by shared hashtags finding co-occurrences and merging overlapping clusters. validation checks cluster health creator counts cross-platform presence and regional spread. finally proof tiles get generated with metrics recommendations and evidence.

the clustering algorithm builds a hashtag index then finds frequent co-occurrences. it groups posts sharing significant hashtags and merges overlapping clusters using similarity calculations. health metrics get calculated for each cluster combining creator diversity engagement strength and velocity.

validation uses multi-factor checks. cluster health must be above a threshold. creator count needs to meet a minimum. cross-platform presence strengthens confidence. cross-region spread indicates real trend replication. confidence scores combine these factors into a single validation score.

all metrics use transparent formulas. engagement rate is likes plus comments plus shares divided by views. velocity is total engagement divided by hours since first seen. creator diversity is unique creators divided by total posts. cluster health weights diversity engagement and velocity together. validation confidence comes from creator count and region count normalized against thresholds.

scaling works through horizontal scaling with stateless api design separate ingestion and processing services. data can be partitioned by platform or time window. caching handles frequently accessed trends and cluster health scores. the database uses proper indexing on timestamp platform and post_id for efficient queries.

transparency features include all metric formulas documented in code clustering rules explicit and adjustable validation thresholds configurable proof tiles with complete evidence and logging at every decision point. you can trace exactly why something happened which is the whole point of avoiding black boxes.
