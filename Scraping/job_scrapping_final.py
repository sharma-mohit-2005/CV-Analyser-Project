# job_scrapping_final.ipynb

import requests
import csv
from bs4 import BeautifulSoup
import time

# Read job links
with open('job_links.txt', 'r') as file:
    links = [link.strip() for link in file if link.strip()]

# Prepare CSV file
csv_file = open('job_details.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)

# Write header
csv_writer.writerow(["Job Title", "Company Name", "Location", "Start Date", "CTC (Annual)", "Experience", "Apply By", "Skills Required", "Perks"])

# Function to extract job details
def extract_job_data(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract data safely
        job_title_tag = soup.find('div', class_='heading_4_5 profile')
        job_title = job_title_tag.text.strip() if job_title_tag else 'N/A'

        company_name_tag = soup.find('div', class_='heading_6 company_name')
        company_name = company_name_tag.find('a').text.strip() if company_name_tag and company_name_tag.find('a') else 'N/A'

        location_tag = soup.find('p', id='location_names')
        location = location_tag.text.strip().replace("\n", " ").strip() if location_tag else 'N/A'

        start_date_tag = soup.find('div', id='start-date-first')
        start_date = start_date_tag.text.strip() if start_date_tag else 'N/A'

        ctc_tag = soup.find('div', class_='item_body salary')
        ctc = ctc_tag.text.strip() if ctc_tag else 'N/A'

        experience_tag = soup.find('div', class_='item_body desktop-text')
        experience = experience_tag.text.strip() if experience_tag else 'N/A'

        apply_by_tag = soup.find('div', class_='other_detail_item_row')
        apply_by = apply_by_tag.find_all('div', class_='item_body')[-1].text.strip() if apply_by_tag else 'N/A'

        skills_required = ', '.join([skill.text.strip() for skill in soup.find_all('span', class_='round_tabs')]) or 'N/A'

        perks_tag = soup.find('div', class_='round_tabs_container')
        perks = ', '.join([perk.text.strip() for perk in perks_tag.find_all('span', class_='round_tabs')]) if perks_tag else 'N/A'

        return [job_title, company_name, location, start_date, ctc, experience, apply_by, skills_required, perks]

    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

# Loop through links and scrape data
counter = 0
for index, link in enumerate(links):
    data = extract_job_data(link)
    if data:
        csv_writer.writerow(data)
        counter += 1

    if counter % 10 == 0 and counter != 0:
        print(f"Processed {counter} jobs, waiting to prevent errors...")
        time.sleep(5)

csv_file.close()
print("Job scraping completed and saved to 'job_details.csv'!")
