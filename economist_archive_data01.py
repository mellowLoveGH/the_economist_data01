import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json

# given year, get all weekly editions of this year, first-page & url
# for example, 
# 'It’s not just inflation', 'https://www.economist.com/weeklyedition/2022-10-29')
def get_weekly_editions_each_year(year):
    url = 'https://www.economist.com/weeklyedition/archive?year='+str(year)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')
    items = soup.find_all(class_='headline-link')
    name_href = []
    for it in items:
        name = it.get_text().strip()
        href = it.get('href').strip()
        href = 'https://www.economist.com/weeklyedition/' + href.split('/')[-1]
        #print(name, href)
        name_href.append( (name, href) )        
    return name_href

# for the link of a essay, it always includes information about topic, date-time & essay name
# for example,
# 'https://www.economist.com//leaders/2022/10/26/rishi-sunaks-promise-of-stability-is-a-low-bar-for-britain'
def parse_link(link):
    parts = link.split('/')
    topic = parts[1]
    name = parts[-1]
    return topic, name

# get the content of certain essay by link
def get_article(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')
    #print(soup)
    first_paragraph = ""
    items = str(soup).split('\n')
    for it in items:
        if it.startswith("{\"@context\":"):
            dic_data = json.loads(it)
            if "headline" in dic_data and "articleBody" in dic_data:
                # dic_data["headline"]
                first_paragraph = dic_data["articleBody"]
                break
    #it = soup.find(class_='article__body-text article__body-text--dropcap')
    #first_paragraph = it.get_text().strip()    
    return first_paragraph

# get the data all essays of one weekly edition
# for example, 
# url = 'https://www.economist.com/weeklyedition/2022-10-29'
def get_weekly_edition(url, first_page):
    edition_time = url.split('/')[-1]
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')
    #items = soup.find_all(class_='layout-weekly-edition')
    items = soup.find_all("a")
    weekly_edition = []
    error_counter = []
    for it in items[:]:
        attributes_dic = it.attrs        
        if len(attributes_dic)==1 and 'href' in attributes_dic:
            href = it.get('href').strip()
            page_url = 'https://www.economist.com/' + href
            title = it.get_text().strip()
            topic, name = parse_link(href)
            #print(title, page_url, topic, name)
            try:
                first_paragraph = get_article(page_url)
                #print( '\t', first_paragraph )
                weekly_edition.append( (edition_time, first_page, title, page_url, topic, name, first_paragraph) )
            except:
                #print('\terror', edition_time, first_page, title, page_url, topic, name)     
                error_counter.append( (edition_time, first_page, title, page_url, topic, name) )
    #print(error_counter)
    return weekly_edition, error_counter



"""

"""

year = 2021
name_href = get_weekly_editions_each_year(year)
len(name_href)
name_href = sorted(name_href, key=lambda x: x[1])
name_href

whole_data = []
error_data = []
week_counter = 0
for k, v in name_href[:]:
    first_page, url = k, v
    weekly_edition, error_counter = get_weekly_edition(url, first_page)
    whole_data += weekly_edition
    error_data += error_counter
    week_counter += 1
    print('week_counter', week_counter)
    print( k, v )
    print( len(error_counter), len(weekly_edition), len(error_data), len(whole_data) )
col_names = ['edition_time', 'first_page', 'title', 'page_url', 'topic', 'name', 'first_paragraph']
file_name = str(year) + ".csv"
df_data = pd.DataFrame(whole_data, columns=col_names)
df_data.to_csv('C:/Users/Admin/Desktop/economist_data/'+file_name)
print( file_name )
print()
