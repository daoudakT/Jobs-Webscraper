import csv

import requests
from bs4 import BeautifulSoup



# Type GET request
r = requests.get("https://www.welcometothejungle.com/fr/companies/datascientest/jobs/custumer-success-manager-h-f-stage_puteaux?q=011dba3582a54e3bef6bb0a10181085c&o=3ea98bb2-d117-4cdf-aaaf-c969046fda2f")

# Printing object type - response 
# print("Type :", type(r))

# Printing Status Code 
#print("Status Code :", r.status_code)

# Printing the content of the response
#print(r.text)

# Storing the content of the response 
webpage_html = r.text

# Initailize a BS object
soup = BeautifulSoup(webpage_html, "lxml")

# Using prettify to format HTML code
#print(soup.prettify())

# Getting a level 1 title tag
#print(soup.h2.text)
#print(soup.find_all('h2'))

# Accessing contract Icon
#contract_icon = soup.find('i', {'name':"contract"})
#print("Job Location:", soup.find('i', {"name":"location"}).parent.text)
# Getting the contract text
#print(contract_icon.parent.text)

# Accessing different elements on the page
job_title = soup.find('h2').text
contract_type = soup.find('i', {'name':"contract"}).parent.text
job_location = soup.find('i', {'name':"location"}).parent.text
remote_work = soup.find('i', {'name':"remote"}).parent.text
#education_level = soup.find('i', {'name':"education_level"}).parent.text
experience_needed = soup.find('i', {'name':"suitcase"}).parent.text

compagny_name = soup.find('div', class_='sc-bXCLTC jYvPbE').text

#print(job_title)
print(job_title)
print(contract_type)
print(job_location)
print(remote_work)
print(experience_needed)
print(compagny_name)


# Organizing columns names in a list
column_names = ['Titre', 'Contrat', 'Localisation', 'Télétravail', 'Experience', 'Compagny']
# Organizing variables in a list 
job_data = [job_title, contract_type, job_location, remote_work, experience_needed, compagny_name]
# Joining elements of the list in a string
#job_data = ','.join(job_data)

# Opening a file 
#csv_file = open('job_offres.csv', 'a', encoding='utf-8', newline='')
#with open('job_offres.csv', 'a', encoding='utf-8', newline='') as csv_file:
    # Add a line with columns (if needed)
    #if csv_file.tell() == 0:
        #csv_file.write(','.join(column_names))
    # Adding text at the end of file
    #csv_file.write('\n' + job_data)
    # Close automatically the file 
    #csv_file.close()
with open('job_offres.csv', 'a', encoding='utf-8', newline='') as csv_file:
    # Create a writer object
    writer = csv.writer(csv_file)
    # Add a line with columns
    if csv_file.tell() == 0:
        writer.writerow(column_names)
    # Add data for the offre
    writer.writerow(job_data)