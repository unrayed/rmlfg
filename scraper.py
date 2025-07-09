from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def get_rematchtracker_rank(steam_id):
    chrome_driver_path = r"C:\Users\green\Desktop\rmverify bot\chromedriver.exe"  # change to your path

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    url = f"https://www.rematchtracker.com/player/steam/{steam_id}"
    driver.get(url)

    time.sleep(5)  # wait for JS to load

    try:
        rank_el = driver.find_element(By.CSS_SELECTOR, "div.text-lg.font-bold.text-white.mb-1.svelte-bvxqti")
        rank = rank_el.text
    except Exception:
        rank = "Rank info not found."

    driver.quit()
    return rank