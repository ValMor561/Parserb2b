import requests
from bs4 import BeautifulSoup
import json

url = 'https://b2b.xcom.ru/catalog'
response = requests.get(url)

if response.status_code == 200:

    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.title.string

    links = soup.find_all('a')
    
    data = []
    for link in links:
        if "/catalog/" in link.get('href'):
            new_str = link.get('href').replace("/catalog/", "")
            if new_str.count("/") > 2:
                continue
            if new_str.endswith("/"):
                new_str = new_str[:-1]
            data.append(new_str)
    
    file_path = "catalogs.json"
    with open(file_path, "w", encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False)

else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)
