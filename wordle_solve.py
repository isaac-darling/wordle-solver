# February 2022
# Write an app to solve the Wordle puzzle efficiently

import datetime
import json
import time

import twitter
import pyperclip
from datastructures.priority_queue import PriorityQueue
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

def init() -> None:
    """Define global variables"""
    global SERVICE, OPTIONS
    global ANSWERS, DOM_QUERY, STATS

    SERVICE = Service("C:\Program Files (x86)/chromedriver.exe")
    OPTIONS = webdriver.ChromeOptions()
    OPTIONS.add_argument("start-maximized")
    OPTIONS.add_experimental_option("excludeSwitches", ["enable-logging"])

    with open("wordlist/answers.txt", "r") as f:
        ANSWERS = json.load(f)
    with open("wordlist/queries.json", "r") as f:
        DOM_QUERY = json.load(f)
    with open("wordlist/letter_stats.json", "r") as f:
        STATS = json.load(f)

def get_priority(word: str, *, info: dict[str: set[tuple[int, str]]] | None = None) -> float:
    """Determine how valuable a word in the queue is to guess"""
    if info is None:
        info = {"absent": set(), "present": set(), "correct": set()}

    if info["present"] or info["correct"]:
        info["absent"] = {clue for clue in info["absent"] if clue[1] not in list(zip(*(info["present"] | info["correct"])))[1]}

    if any(clue[1] in word for clue in info["absent"]) or any(clue[1] not in word for clue in info["present"] | info["correct"]):
        return 0

    value = 0
    seen = set()
    for i, char in enumerate(word):
        for j, c in info["present"]:
            if char == c and i == j:
                return 0
        for j, c in info["correct"]:
            if i == j and char != c:
                return 0
        if char not in seen:
            value += STATS[char]
            seen.add(char)

    return value

def solve() -> None:
    """Use statistics to attempt to solve the Wordle puzzle"""
    queue = PriorityQueue([(word, get_priority(word)) for word in ANSWERS])
    attempt = 0

    with webdriver.Chrome(service=SERVICE, options=OPTIONS) as driver:
        driver.get("https://www.nytimes.com/games/wordle/index.html")
        time.sleep(0.5)
        driver.execute_script(DOM_QUERY["close_button"]).click()
        time.sleep(0.5)

        while attempt < 6:
            ActionChains(driver).send_keys(f"{queue.get()}\n").perform()
            time.sleep(2)

            row = driver.execute_script(DOM_QUERY["row_divs"])[attempt]
            if row.get_attribute("win") is not None:
                break

            clues = {"absent": set(), "present": set(), "correct": set()}
            for i, tile in enumerate(row.shadow_root.find_elements(By.CSS_SELECTOR, "game-tile")):
                clues[tile.get_attribute("evaluation")].add((i, tile.get_attribute("letter")))

            queue = PriorityQueue([(item[0], get_priority(item[0], info=clues)) for item in queue])
            queue.drop()
            attempt += 1
        time.sleep(3)
        driver.execute_script(DOM_QUERY["share_button"]).click()
    twitter.tweet_result(pyperclip.paste())

def cheat() -> None:
    """Wordle simply increments through the answer list, which is easy to exploit"""
    days_since_ref = datetime.date.today() - datetime.date(2022, 2, 12)
    idx = days_since_ref.days + 238 # 238 was the index on the above date
    idx = idx % len(ANSWERS)

    with webdriver.Chrome(service=SERVICE, options=OPTIONS) as driver:
        driver.get("https://www.nytimes.com/games/wordle/index.html")
        time.sleep(0.5)
        driver.execute_script(DOM_QUERY["close_button"]).click()
        time.sleep(0.5)
        ActionChains(driver).send_keys(f"{ANSWERS[idx]}\n").perform()
        time.sleep(5)
        driver.execute_script(DOM_QUERY["share_button"]).click()
    twitter.tweet_result(pyperclip.paste())

def main() -> None:
    """Code execution starts here"""
    init()
    solve()
    #cheat()

if __name__=="__main__":
    main()
