import csv
import time
from datetime import datetime
import os
from email.message import EmailMessage
import smtplib
import sys

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
    column_names = ['Date de la collection', 'Titre', 'Contrat', 'Localisation', 'Salary', 'Start Date', 'Télétravail', 'Etudes', 'Experience', 'Compagny']
    # Organizing variables in a list 
    job_data = [datetime.now().strftime("%Y-%m-%d"),job_title, contract_type, job_location, salary, start_date, remote_work, education_level, experience_needed, compagny_name]
    
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
    
    if job_list is None:
        print("Aucune liste d'offres d'emploi trouvée.")
        return []
    # Create an empty list for links
    job_links = []
    
    # Iterate over the jobs list 
    for job in job_list.find_all('li'):
        job_links.append(f"https://www.welcometothejungle.com{job.find('a').get('href')}")
    
    return job_links

def scrape_job_offer_data_from_keywords(keywords:str, csv_path:str):
    # Get search page dynamic content with selenium
    base_url = "https://www.welcometothejungle.com/fr/jobs?"
    search_query = "%20".join(keywords.split())
    search_page_content = get_dynamic_page_content(f"{base_url}&query={search_query}")
    #search_page_content = get_dynamic_page_content(f"https://www.welcometothejungle.com/fr/jobs?&query={keywords.split()[0]}%20{keywords.split()[1]}")

    # Initialize a BS object
    soup = BeautifulSoup(search_page_content, "lxml")

    # Get job links from the search page BS  object
    job_links = get_job_links_list(soup)

    # Loop over the links to fill the csv 
    for i, job_offer in enumerate(job_links):
        #print(i, job_offer)
        scrape_data_from_job_offer(job_offer, csv_path)
        time.sleep(1)
    print(f"Fin du scraping des {i} offres")

def send_email_with_csv(dest_email: str, csv_path: str, keywords: str)-> None:
    count_new = get_rid_of_duplicates(csv_path)
    msg = create_email_message(dest_email, keywords, count_new)
    msg = attach_csv_file_to_message(msg, csv_path)
    send_email(msg)

def create_email_message(dest_email: str, keywords: str, count: int)-> EmailMessage:
    msg = EmailMessage()
    # Set the header infos (sender, recipient, subject)
    #msg['From'] = "koned4490@gmail.com"
    #msg['To'] = "koned4490@gmail.com"
    msg['From'] = dest_email
    msg['To'] = dest_email
    msg['Subject'] = "Nouvelles offres d'emploi"
    # Set the body of the email
    msg.set_content(f"{count} nouvelles offres d'emploi sont apparues pour la recherche {keywords}")
    return msg

def attach_csv_file_to_message(msg: EmailMessage, csv_path:str)-> EmailMessage:
    # Open the CSV file in binary mode and read its contents
    with open(csv_path, 'rb') as f:
        job_offer_data = f.read()
    msg.add_attachment(job_offer_data, maintype='text', subtype='csv', filename=csv_path)
    
    return msg

#print(msg.as_string())
def send_email(msg:EmailMessage)-> None:
    # Send the email using SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(os.environ['EMAIL_USER'],
                os.environ['EMAIL_PASSWORD'])
        smtp.send_message(msg)
        print('Fin Email send ok')

def get_rid_of_duplicates(csv_path: str) -> int:
    new_offers_count = 0
    existing_data = set()

    # Read data from the CSV file
    with open(csv_path, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader, None)  # Skip the header
        for row in reader:
            offer = tuple(row)
            if offer not in existing_data:
                existing_data.add(offer)
                new_offers_count += 1

    # Write updated data back to the CSV file
    with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(existing_data)

    return new_offers_count

def read_arg_keywords_from_command_line():
    try:
        keywords_param = sys.argv[1].lower()
    except : 
        print('Veuillez préciser des mots-clés de recherche')
        print('Ex: scrap.py "Développeur Python"')
        sys.exit()
    
    return keywords_param

# Parameters
keywords = read_arg_keywords_from_command_line()
csv_path = f"job_offers_{keywords.replace(' ', '_')}.csv"

scrape_job_offer_data_from_keywords(keywords, csv_path)
send_email_with_csv(os.environ['EMAIL_USER'], csv_path, keywords)
