import requests
import socks
import socket
from bs4 import BeautifulSoup
import re
import json
from requests.exceptions import RequestException
import time
from stem import Signal
from stem.control import Controller

#data_types=["emails","usernames","phone_numbers"]
filter=["NV","contact","confidential","database","name","702","address","email","phone","number","phone number"]
websites=["http://g7ejphhubv5idbbu3hb3wawrs5adw7tkx7yjabnf65xtzztgg4hcsqqd.onion","http://archiveiya74codqgiixo33q62qlrqtkgmcitqx5u2oeqnmn5bpcbiyd.onion"]

# Tor proxy configuration
proxy = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

def set_new_ip():
    with Controller.from_port(port=9051) as controller:
        controller.signal(Signal.NEWNYM)

    socks.set_default_proxy(proxy)
    #socket.socket = socks.socksocket

def extract_emails(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return set(re.findall(email_pattern, text))

def extract_phone_numbers(text):
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    return set(re.findall(phone_pattern, text))

def extract_usernames(text):
    username_pattern = r'\b[a-zA-Z0-9._%+-]{3,20}\b'
    return set(re.findall(username_pattern, text))

def scrape_website(url, session):
    print(f"\nConnecting to {url}...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = session.get(
                url,
                timeout=60,
                verify=False
            )
            response.raise_for_status()
            print(f"Status code: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            text=text.lower()

            if not any(word in text for word in filter):
                print("No relevant keywords found, skipping...")
                return None

            print("Extracting data...")
            
            results = {"emails": list(extract_emails(text)), "usernames": list(extract_usernames(text)), "phone_numbers": list(extract_phone_numbers(text))}
            print("Successfully retrieved content!")

            set_new_ip()
            
            return results
            
            
        except RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print("Waiting 5 seconds before retrying...")
                time.sleep(5)
            else:
                print("Max retries exceeded.")
                raise
    return None

if __name__ == "__main__":
    print("Starting to scrape websites...")
    
    jsonfile = open("results.json","w")
    jsonfile.write("{\n")

    # Create a session that will be used for all requests
    session = requests.Session()
    session.proxies = proxy
    
    all_results = {}

    # Try each website
    for website in websites:
        result = scrape_website(website, session)
        if result:
            all_results[website] = result

    print("Scraping completed.")
    if all_results:
        json.dump(all_results,jsonfile, indent=2)
    else:
        print("No data found.")
    
    print("\nScraping completed.")