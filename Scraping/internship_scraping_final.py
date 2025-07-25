# internship_scraping_final.ipynb

import requests
import csv
from bs4 import BeautifulSoup
import time

# Read internship links
with open('internship_links.txt', 'r') as file:
    internship_links = [link.strip() for link in file.readlines() if link.strip()]

# Prepare CSV file
with open('internship_details.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Internship Title", "Company Name", "Location", "Start Date", "Duration", "Stipend", "Apply By", "Skills Required", "Perks"])

    def extract_internship_data(url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract Title
            internship_title_tag = soup.find('div', class_='heading_4_5 profile')
            internship_title = internship_title_tag.text.strip() if internship_title_tag else 'N/A'

            # Company Name
            company_tag = soup.find('div', class_='heading_6 company_name')
            company_name = company_tag.text.strip().replace("\n", " ") if company_tag else 'N/A'

            # Location
            location_tag = soup.find('div', id='location_names')
            location = location_tag.text.strip().replace("\n", " ") if location_tag else 'N/A'

            # Details
            details = soup.find_all('div', class_='item_body')
            start_date = details[0].text.strip() if len(details) > 0 else 'N/A'
            duration = details[1].text.strip() if len(details) > 1 else 'N/A'
            stipend = details[2].text.strip() if len(details) > 2 else 'N/A'
            apply_by = details[3].text.strip() if len(details) > 3 else 'N/A'

            # Skills
            skills_required = ', '.join(skill.text.strip() for skill in soup.find_all('span', class_='round_tabs')) or 'N/A'

            # Perks
            perks_tag = soup.find('div', class_='perks_container')
            perks = ', '.join(perk.text.strip() for perk in perks_tag.find_all('span', class_='round_tabs')) if perks_tag else 'N/A'

            return [internship_title, company_name, location, start_date, duration, stipend, apply_by, skills_required, perks]

        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None

    # Scrape each internship
    counter = 0
    for index, link in enumerate(internship_links):
        data = extract_internship_data(link)
        if data:
            csv_writer.writerow(data)
            counter += 1

        if counter % 10 == 0 and counter != 0:
            print(f"Processed {counter} internships, taking a short break...")
            time.sleep(5)

print("Internship scraping completed!")
