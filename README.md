# Todo
- Thread twitter save?
- Webbinterface

# How to setup environment
1. Set these environment variables
```shell
TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET
TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET
```
2. Install PostgreSQL
3. Setup database
```shell
$ bash database/setup.sh
```
4. Install python dependencies
```shell
$ pip3 install virtualenv && virtualenv env && source env/bin/activate && pip3 install -r requirements.txt
```

5. Start datamining using your filters
```shell
bash /startup/init.sh start <filter 1> <filter 2> ...
```

6. Check which filters actually allowed by twitter
```shell
bash /startup/init.sh status
```

7. When done, stop the processes with.
```shell
bash /startup/init.sh stop
```
# Antaganden Twitters API
- En retweet är en "ren" retweet om attributet "original_tweet_retweet_count" inte är null