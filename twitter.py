# February 2022
# Use the Twitter API to tweet out the result of an attempted Wordle solve

import tweepy
import json

def tweet_result(result: str) -> None:
    with open("twitter/twitter_keys.json", "r") as f:
        keys = json.load(f)

    client = tweepy.Client(
        consumer_key=keys["API_Key"],
        consumer_secret=keys["API_Secret"],
        access_token=keys["Access"],
        access_token_secret=keys["Access_Secret"]
    )

    text = f"[WordleBot Speaking]\n{result}"
    client.create_tweet(text=text)

def main() -> None:
    tweet_result("WordleBot test...")

if __name__=="__main__":
    main()
