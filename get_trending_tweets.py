import tweepy
import os
import json
import logging
import time

# --- Configuration and Setup ---

# Set up logging for better visibility into the bot's operations
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Load API Credentials Securely ---
def load_twitter_credentials(file_path="twitter_credentials.json"):
    """
    Loads Twitter API credentials from a JSON file.
    It's highly recommended to store credentials securely and not directly in the code.
    """
    if not os.path.exists(file_path):
        logger.error(f"Credentials file not found at: {file_path}")
        raise FileNotFoundError(f"Please create a '{file_path}' file with your Twitter API keys.")
    
    with open(file_path, 'r') as f:
        credentials = json.load(f)
    
    # Validate required keys are present
    required_keys = ["consumer_key", "consumer_secret", "access_token", "access_token_secret"]
    if not all(key in credentials for key in required_keys):
        logger.error(f"Missing one or more required keys in '{file_path}'. "
                     f"Ensure it contains: {', '.join(required_keys)}")
        raise ValueError("Incomplete Twitter API credentials.")
        
    return credentials

try:
    # Load credentials from an external JSON file for security
    # Create a 'twitter_credentials.json' file in the same directory like this:
    # {
    #     "consumer_key": "YOUR_CONSUMER_KEY",
    #     "consumer_secret": "YOUR_CONSUMER_SECRET",
    #     "access_token": "YOUR_ACCESS_TOKEN",
    #     "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET"
    # }
    api_credentials = load_twitter_credentials()
    consumer_key = api_credentials["consumer_key"]
    consumer_secret = api_credentials["consumer_secret"]
    access_token = api_credentials["access_token"]
    access_token_secret = api_credentials["access_token_secret"]

    # Create an instance of the Tweepy API
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True) # Automatically waits if rate limit is hit
    logger.info("Successfully authenticated with Twitter API.")

except (FileNotFoundError, ValueError, tweepy.TweepyException) as e:
    logger.critical(f"Failed to initialize Twitter API: {e}")
    exit(1) # Exit if API initialization fails

# --- Core Logic ---

def get_trending_tweets(woeid=1, tweet_count_per_trend=10):
    """
    Fetches trending topics and then the specified number of tweets for each trend.
    
    Args:
        woeid (int): Where On Earth ID. 1 for worldwide.
                     You can find WOEIDs for specific locations online.
        tweet_count_per_trend (int): Number of tweets to fetch for each trending topic.
    """
    try:
        # Get the top trends for the given WOEID
        # api.trends_place returns a list, and the actual trends are in the first element
        trends_data = api.trends_place(woeid)
        if not trends_data or not trends_data[0].get("trends"):
            logger.warning(f"No trending data found for WOEID: {woeid}")
            return

        logger.info(f"Fetched {len(trends_data[0]['trends'])} trending topics for WOEID: {woeid}")

        for trend in trends_data[0]["trends"]:
            trend_name = trend["name"]
            # Twitter's API sometimes returns negative tweet_volume for privacy or other reasons,
            # indicating the volume is not publicly available or is very low.
            # We'll skip trends with unknown or zero volume.
            tweet_volume = trend.get("tweet_volume")
            
            if tweet_volume is None or tweet_volume <= 0:
                logger.info(f"Skipping trend '{trend_name}' due to unknown or zero tweet volume.")
                continue

            logger.info(f"\n--- Trending Topic: {trend_name} (Volume: {tweet_volume:,}) ---")
            
            try:
                # Search for tweets related to the trend
                # Use tweet_mode='extended' to get the full text of tweets
                tweets = api.search_tweets(q=trend_name, count=tweet_count_per_trend, tweet_mode='extended')
                
                if not tweets:
                    logger.info(f"No tweets found for '{trend_name}'.")
                    continue

                for tweet in tweets:
                    # Access the full text of the tweet
                    tweet_text = tweet.full_text if hasattr(tweet, 'full_text') else tweet.text
                    print(f"  Tweet: {tweet_text.replace('\n', ' ')}") # Replace newlines for cleaner output

            except tweepy.TweepyException as e:
                logger.error(f"Error searching tweets for '{trend_name}': {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred while processing trend '{trend_name}': {e}")
            
            # Add a small delay between trend searches to be mindful of rate limits
            time.sleep(1) 

    except tweepy.TweepyException as e:
        logger.critical(f"Error fetching trending topics: {e}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred in get_trending_tweets: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    logger.info("Starting Twitter trend analysis...")
    get_trending_tweets(woeid=1, tweet_count_per_trend=5) # Example: Get 5 tweets per trend
    logger.info("Twitter trend analysis completed.")
