from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, time
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import json


def is_within_timeframe(tweet_datetime):
    """Check if tweet is within last 4 months up to last night 12 AM"""
    now = datetime.now()
    last_night = now.replace(hour=0, minute=0, second=0, microsecond=0)
    four_months_ago = last_night - timedelta(days=120)
    return four_months_ago <= tweet_datetime <= last_night


def is_older_than_4_months(tweet_datetime):
    """Check if tweet is older than 4 months"""
    four_months_ago = datetime.now() - timedelta(days=120)
    return tweet_datetime < four_months_ago


options = uc.ChromeOptions()
options.add_argument('--no-first-run')
options.add_argument('--disable-blink-features=AutomationControlled')
driver = uc.Chrome(options=options)

driver.get("https://x.com/home")

WebDriverWait(driver, 40).until(
    EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']"))
).send_keys("softwarepattern9@gmail.com")

driver.find_element(By.XPATH, "//span[contains(text(),'Next')]").click()
sleep(5)

try:
    driver.find_element(By.XPATH, "//span[contains(text(),'Next')]")
    print("Username verification required. Entering username...")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@inputmode='text']"))
    ).send_keys("software69857")
    driver.find_element(By.XPATH, "//span[contains(text(),'Next')]").click()
    sleep(5)
except:
    print("No username verification needed.")

WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, "//input[contains(@autocomplete,'assword')]"))
).send_keys("#676F924c")

driver.find_element(By.XPATH, "//span[contains(text(),'Log in')]").click()
sleep(10)

search_box = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']"))
)
search_box.send_keys("geonews_english")
search_box.send_keys(Keys.ENTER)

WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, "People"))).click()
sleep(2)

WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'@geonews_english')]"))
).click()
sleep(5)

tweets = {}
processed_tweets = set()
scroll_start = time()
should_stop = False

print("Scraping ALL tweets from last 4 months up to last night 12 AM...")

#Currently it will run for 10 min's.
while not should_stop and time() - scroll_start < 600:  # Here you can remove the time limit and make sure of scraper running for all 4 months by change removing >  and time() - scroll_start < 7200  < this line from condtion
    articles = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")

    for article in articles:
        try:
            tweet_text = article.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
            time_elem = article.find_element(By.XPATH, ".//time")
            tweet_datetime = datetime.fromisoformat(time_elem.get_attribute("datetime").replace('Z', '+00:00')).replace(
                tzinfo=None)

            tweet_id = f"{tweet_text[:50]}_{tweet_datetime.isoformat()}"

            # Skip if tweet is already processed
            if tweet_id in processed_tweets:
                continue

            processed_tweets.add(tweet_id)

            if is_older_than_4_months(tweet_datetime):
                print(f"Reached tweet older than 4 months: {tweet_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                print("Stopping scraper as goal completed!")
                should_stop = True
                break

            if is_within_timeframe(tweet_datetime):
                tweets[tweet_id] = {
                    "text": tweet_text,
                    "timestamp": tweet_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    "datetime_iso": tweet_datetime.isoformat()
                }

        except Exception as e:
            continue

    if should_stop:
        break

    driver.execute_script("window.scrollBy(0, 1000);")
    sleep(2)

    if len(tweets) % 50 == 0 and len(tweets) > 0:
        print(f"Progress: {len(tweets)} tweets collected...")

tweet_list = list(tweets.values())
tweet_list.sort(key=lambda x: x["datetime_iso"], reverse=True)

filename = f"geonews_tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump({
        "scrape_date": datetime.now().isoformat(),
        "total_tweets": len(tweet_list),
        "timeframe": "Last 4 months up to 29th July",
        "tweets": tweet_list
    }, f, indent=2, ensure_ascii=False)

print(f"\nSCRAPING COMPLETED!")
print(f"Total tweets collected: {len(tweet_list)}")
print(f"Saved to: {filename}")
print("=" * 80)

for i, tweet in enumerate(tweet_list[:30], 1):
    print(f"{i}. Time: {tweet['timestamp']}")
    print(f"   Text: {tweet['text'][:120]}{'...' if len(tweet['text']) > 120 else ''}")
    print("-" * 70)

if len(tweet_list) > 30:
    print(f"\nand {len(tweet_list) - 30} more tweets in the JSON file!")

print(f"All {len(tweet_list)} tweets saved in '{filename}'")

try:
    driver.quit()
except:
    pass