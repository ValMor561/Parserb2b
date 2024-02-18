from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import time
import json
import os
import re
from webdriver_manager.chrome import ChromeDriverManager

def init_driver():
    service = Service(ChromeDriverManager().install())
   
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('headless')
    options.add_argument('log-level=3')
    
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_count_pages(url, driver):
    driver.get(url)
    time.sleep(2)
    try:
        link_elements = driver.find_elements(By.CLASS_NAME, 'page-link')
        second_last_link = link_elements[-2]
        count_pages = second_last_link.text
    except IndexError:
        return 2   
    finally:
        driver.quit()
    return count_pages

def get_cards_from_category(path, driver):
    url = f'https://b2b.xcom.ru/catalog/{path}/?per-page=96'
    os.makedirs(path, exist_ok=True)
    count_pages = get_count_pages(url,driver)
    for page in range(1, int(count_pages)):
        url = f"https://b2b.xcom.ru/catalog/{path}/?page={page}&per-page=96"
        driver = init_driver()
        driver.get(url)
        time.sleep(2)
        try:
            product_images = driver.find_elements(By.CLASS_NAME, 'product__image')
            product_codes = driver.find_elements(By.CLASS_NAME, 'product__column_code')
            product_names = driver.find_elements(By.CLASS_NAME, 'product__column_name')
            product_descriptions = driver.find_elements(By.CLASS_NAME, 'product__description-wrap')
            product_warranties = driver.find_elements(By.CLASS_NAME, 'product__warranty')
            product_pricies = driver.find_elements(By.CLASS_NAME, 'product__column_price')

            lenght = len(product_pricies)
            for i in range(0, lenght):
                product_name = product_names[i].text.split("\n", 1)[0]
                forbidden_chars_pattern = r'[<>:"/\\|?*]'
                product_name =  re.sub(forbidden_chars_pattern, '', product_name)
                data = {
                    "photo_url": product_images[i].get_attribute('src'),
                    "product_code": product_codes[i].text,
                    "product_name" : product_name,
                    "product_description": product_descriptions[i].text,
                    "product_warranty" : product_warranties[i].text,
                    "product_price" : product_pricies[i].text
                }
                file_path = os.path.join(path, f"{product_name}.json")
                with open(file_path, "w", encoding='utf-8') as json_file:
                    json.dump(data, json_file, ensure_ascii=False)
            print(f"end https://b2b.xcom.ru/catalog/{path}/?page={page}")
        except IndexError:
            continue
        except WebDriverException as e:
            print("Произошла ошибка WebDriver:", e)
            continue


def main():
    with open('catalogs.json', 'r') as file:
        categories = json.load(file)

    for category in categories:
        driver = init_driver()
        get_cards_from_category(category, driver)
        driver.quit()

if __name__ == "__main__":
    main()