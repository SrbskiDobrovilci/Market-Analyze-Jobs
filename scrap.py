import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
import re

# Configure Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

service = Service('chromedriver.exe')  # Update this path
driver = webdriver.Chrome(service=service, options=chrome_options)

BASE_URL = "https://hh.ru"

def scrape_job_postings(num_postings=1100):
    with open('job_postings.json', 'r', encoding='utf-8') as f:
        job_data = json.load(f)
    links = [post['link'] for post in job_data]
    links = set(links)
    print(len(links))
    page = 0
    
    while len(job_data) < num_postings:
        url = f"{BASE_URL}/search/vacancy?text=программист&page={page}"
        driver.get(url)
        time.sleep(3)  # Wait for page to load
        
        # Check if we've reached the end
        if "По вашему поисковому запросу ничего не найдено" in driver.page_source:
            break
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all('div',{'data-qa' : 'vacancy-serp__vacancy vacancy-serp__vacancy_standard_plus'})
        #print(url, job_cards)
        for card in job_cards:
            if len(job_data) >= num_postings:
                break
            #print(card)
            try:
                title = card.find('span' ,{'data-qa':'serp-item__title-text'}).text.strip()
                #print(title)
                location = card.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}).text.strip()
                #print(location)
                salary = card.find('span', {'class': 'magritte-text___pbpft_3-0-32 magritte-text_style-primary___AQ7MW_3-0-32 magritte-text_typography-label-1-regular___pi3R-_3-0-32'})
                #print(salary)
                salary = salary.text.strip() if salary else "Не указана"
                link = card.find('a', { 'data-qa': 'serp-item__title'})['href'].split('?')[0]
                if  link in links: 
                    continue
                #print(link)
                # Get job description and requirements
                job_details = scrape_job_details(link)
                if not job_details:
                    continue
                
                job_data.append({
                    'title': title,
                    'location': location,
                    'salary': salary,
                    'link': link,
                    **job_details
                })
                links.append(link)

                
            except Exception as e:
                print(f"Error processing card: {e}")
                continue
        print(len(job_data))
        page += 1
        save_data(job_data)
        time.sleep(2)  # Be polite
    
    driver.quit()
    return job_data

def scrape_job_details(job_url):
    try:
        driver.get(job_url)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Get description
        description = soup.find('div', {'data-qa': 'vacancy-description'})
        if not description:
            return None
            
        description = description.text.strip()
        
        # Extract skills and requirements
        skills = extract_skills(description)
        
        # Get experience requirement
        experience = soup.find('span', {'data-qa': 'vacancy-experience'})
        experience = experience.text.strip() if experience else "Не указан"
        
        # Get employment type
        employment = soup.find('span', {'data-qa': 'vacancy-view-employment-mode'})
        employment = employment.text.strip() if employment else "Не указан"
        
        return {
            'description': description,
            'skills': skills,
            'experience': experience,
            'employment': employment
        }
        
    except Exception as e:
        print(f"Error scraping job details: {e}")
        return None

def extract_skills(description):
    # Common IT skills to look for
    IT_SKILLS = [
        'Python', 'Java', 'JavaScript', 'C#', 'C++', 'SQL', 'Git', 'Docker', 
        'Kubernetes', 'AWS', 'Azure', 'GCP', 'Linux', 'Windows', 'MacOS',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring',
        'Machine Learning', 'AI', 'Data Science', 'Big Data', 'Hadoop',
        'Spark', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
        'CI/CD', 'Jenkins', 'Ansible', 'Terraform', 'Agile', 'Scrum', 'Kanban'
    ]
    
    # Normalize the description
    desc_lower = description.lower()
    
    found_skills = []
    for skill in IT_SKILLS:
        # Check both exact match and lowercase match
        if re.search(rf'\b{re.escape(skill)}\b', description, re.IGNORECASE):
            found_skills.append(skill)
    
    # Extract programming languages
    languages = ['Python', 'Java', 'JavaScript', 'C#', 'C++', 'Ruby', 'PHP', 'Go', 'Rust', 'Swift', 'Kotlin']
    found_languages = [lang for lang in languages if re.search(rf'\b{re.escape(lang)}\b', description, re.IGNORECASE)]
    
    # Extract education requirements
    education = []
    if re.search(r'высшее образование', desc_lower):
        education.append('Higher Education')
    if re.search(r'техническое образование', desc_lower):
        education.append('Technical Education')
    
    return {
        'skills': found_skills,
        'languages': found_languages,
        'education': education
    }

def save_data(data, filename='job_postings.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print("Starting scraping...")
    jobs = scrape_job_postings(num_postings=1100)
    save_data(jobs)
    print(f"Scraped {len(jobs)} job postings")