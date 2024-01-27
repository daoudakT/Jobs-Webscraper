import csv
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_webpage_html(url:str)-> str:
   # Type GET request
   response = requests.get(url)
   # Accessing the content of the response 
   webpage_html = response.text
   
   return webpage_html

def get_info_via_icon(soup:BeautifulSoup, icon_name:str)-> str:
    try:
        info = soup.find('i', {"name":icon_name}).parent.text
    except AttributeError:
        info = ''
    
    return info
        
def get_info_from_offer(soup, offer_link)-> list:
    
    ### Accessing diferent elements on the page
    job_title = soup.find('h2').text
    contract_type = get_info_via_icon(soup,'contract')
    job_location = get_info_via_icon(soup,'location')
    salary = get_info_via_icon(soup,'salary')
    start_date = get_info_via_icon(soup,'clock')
    remote_work = get_info_via_icon(soup,'remote')
    education_level = get_info_via_icon(soup,'education_level')
    experience_needed = get_info_via_icon(soup,'suitcase')
    compagny_name = soup.find('div', class_='sc-bXCLTC jYvPbE').text

    # Organizing columns names in a list
    column_names = ['Titre', 'Contrat', 'Localisation', 'Salary', 'Start Date', 'Télétravail', 'Etudes', 'Experience', 'Compagny']
    # Organizing variables in a list 
    job_data = [job_title, contract_type, job_location, salary, start_date, remote_work, education_level, experience_needed, compagny_name]
    
    return job_data, column_names

def add_line_to_csv(new_line:list, columns:list, csv_path:str):
    # Opening a file
    with open(csv_path, 'a', encoding='utf-8', newline='') as csv_file:
        # Create a writer object
        writer = csv.writer(csv_file)
        # Add a line with columns
        if csv_file.tell() == 0:
            writer.writerow(columns)
        # Add data for the offre
        writer.writerow(new_line)
        
def scrape_data_from_job_offer(offer_link:str, job_offers_csv_path:str):
    # Get the HTML code of the webpage
    webpage_html = get_webpage_html(offer_link)
    # Initialize a BS object
    soup = BeautifulSoup(webpage_html, "lxml")
    # Getting info from job offer 
    job_data, column_names = get_info_from_offer(soup, offer_link)
    # Save results to csv
    add_line_to_csv(job_data, column_names, job_offers_csv_path)


# Intialize a Chrome object
#driver = webdriver.Chrome(r'c:/Users/daoud/Desktop/Moudoski/Défi/Projet_jobs_webscraper/drivers/chromedriver.exe')
#options = webdriver.ChromeOptions()
# Ajoutez des options au besoin
#driver = webdriver.Chrome(executable_path=r'c:/Users/daoud/Desktop/Moudoski/Défi/Projet_jobs_webscraper/drivers/chromedriver.exe', options=options)
def get_dynamic_page_content(target_url:str)-> str:
    
    # Intialize a Chrome object
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    # Accessing the target url
    driver.get(target_url)

    # Wait for 5 seconds
    time.sleep(5)

    # Store the content of the webpage
    page_content = driver.page_source

    driver.quit()
    
    return page_content

def get_job_links_list(soup:BeautifulSoup):
    #find the ordered list 
    job_list = soup.find('ol', class_="sc-1wqurwm-0 cCiCwl ais-Hits-list")
    
    # Create an empty list for links
    job_links = []
    
    # Iterate over the jobs list 
    for job in job_list.find_all('li'):
        job_links.append(f"https://www.welcometothejungle.com{job.find('a').get('href')}")
    
    return job_links

def scrape_job_offer_data_from_keywords(keywords:str, csv_path:str):
    # Get search page dynamic content with selenium
    search_page_content = get_dynamic_page_content(f"https://www.welcometothejungle.com/fr/jobs?&query={keywords.split()[0]}%20{keywords.split()[1]}")

    # Initialize a BS object
    soup = BeautifulSoup(search_page_content, "lxml")

    # Get job links from the search page BS  object
    job_links = get_job_links_list(soup)

    # Loop over the links to fill the csv 
    for i, job_offer in enumerate(job_links):
        print(i, job_offer)
        scrape_data_from_job_offer(job_offer, csv_path)
        time.sleep(1)

keywords = "Développeur Python"
csv_path = "jobl_offres.csv"
# fill up csv
scrape_job_offer_data_from_keywords(keywords, csv_path)

# 
# 
# 
# 
# 
# job_offer_list = ["https://www.welcometothejungle.com/fr/companies/datascientest/jobs/custumer-success-manager-h-f-stage_puteaux?q=011dba3582a54e3bef6bb0a10181085c&o=3ea98bb2-d117-4cdf-aaaf-c969046fda2f",
                 # "https://www.welcometothejungle.com/fr/companies/margo/jobs/margo-analytics-data-scientist-h-f_paris",
                 # "https://www.welcometothejungle.com/fr/companies/tata-consultancy-services/jobs/stagiaire-developpeur-python-oriente-frameworks-ai-h-f_puteaux?q=71730fd2b908590ff22b85d287cd8a3d&o=c589c8ef-7318-4836-af6a-6b63df6fba03"]

#
# 
# for offer_link in job_offer_list:
   # scrape_data_from_job_offer(offer_link, 'jobs_offers.csv')
