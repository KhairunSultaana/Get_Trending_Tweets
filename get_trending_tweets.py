import tweepy

# Twitter API credentials
consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
access_token = "YOUR_ACCESS_TOKEN"
access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"

# Create an instance of the Tweepy API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Get the top ten trending topics
trends = api.trends_place(1)

# Print the top ten trending tweets
for trend in trends[0]["trends"]:
    if trend["tweet_volume"] > 0:
        tweets = api.search(q=trend["name"], count=10)
        for tweet in tweets:
            print(f"{trend['name']}: {tweet.text}")
