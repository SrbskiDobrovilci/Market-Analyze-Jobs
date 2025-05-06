import json
from collections import Counter
import pandas as pd

def analyze_job_data(filename='job_postings.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Analyze skills
    all_skills = []
    all_languages = []
    all_education = []
    experience_levels = []
    
    for job in data:
        all_skills.extend(job['skills']['skills'])
        all_languages.extend(job['skills']['languages'])
        all_education.extend(job['skills']['education'])
        experience_levels.append(job['experience'])
    
    # Count frequencies
    skill_counts = Counter(all_skills)
    language_counts = Counter(all_languages)
    education_counts = Counter(all_education)
    experience_counts = Counter(experience_levels)
    
    # Prepare data for visualization
    top_skills = pd.DataFrame(skill_counts.most_common(20), columns=['Skill', 'Count'])
    top_languages = pd.DataFrame(language_counts.most_common(), columns=['Language', 'Count'])
    education_data = pd.DataFrame(education_counts.most_common(), columns=['Education', 'Count'])
    experience_data = pd.DataFrame(experience_counts.most_common(), columns=['Experience', 'Count'])
    
    # Save processed data
    top_skills.to_csv('top_skills.csv', index=False)
    top_languages.to_csv('top_languages.csv', index=False)
    education_data.to_csv('education_data.csv', index=False)
    experience_data.to_csv('experience_data.csv', index=False)
    
    return {
        'skills': top_skills,
        'languages': top_languages,
        'education': education_data,
        'experience': experience_data
    }

if __name__ == "__main__":
    analyze_job_data()