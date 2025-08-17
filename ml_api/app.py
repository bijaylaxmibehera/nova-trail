from flask import Flask, request, jsonify
import spacy
import requests
from difflib import get_close_matches
import os
from dotenv import load_dotenv

# ---------------- CONFIG ----------------
load_dotenv()

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

# Predefined skills 
KNOWN_SKILLS = {
    "python","java","c++","react","node","express","mongodb","sql",
    "mysql","pandas","numpy","ml","machine learning","deep learning",
    "docker","git","html","css","javascript","typescript",
    "power bi","tableau","django","flask"
}

# JSearch API (RapidAPI) for job search in realtime
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"

# Coursera API (Open catalog)
COURSERA_URL = "https://api.coursera.org/api/courses.v1"

# ---------------- UTILS ----------------
def extract_skills(text: str):
    """Extract relevant skills from text using NLP + fuzzy match."""
    doc = nlp(text.lower())
    found = set()
    for token in doc:
        match = get_close_matches(token.text, KNOWN_SKILLS, n=1, cutoff=0.8)
        if match:
            found.add(match[0])
    return found

def fetch_coursera_courses(skill, limit=3):
    """Fetch courses from Coursera (fallback: scraping public catalog)."""
    try:
        url = f"https://www.coursera.org/api/courses.v1?q=search&query={skill}&limit={limit}"
        response = requests.get(url)
        results = []
        if response.status_code == 200:
            data = response.json()
            for c in data.get("elements", []):
                results.append({
                    "title": c.get("name"),
                    "platform": "Coursera",
                    "url": f"https://www.coursera.org/learn/{c.get('slug')}"
                })
        # fallback if Coursera returns empty
        if not results:
            results.append({
                "title": f"Top {skill} course on Udemy",
                "platform": "Udemy",
                "url": f"https://www.udemy.com/courses/search/?q={skill}"
            })
        return results
    except Exception as e:
        # final fallback
        return [{
            "title": f"Browse {skill} courses",
            "platform": "Coursera",
            "url": f"https://www.coursera.org/search?query={skill}"
        }]


def recommend_courses(missing_skills):
    """Get course recommendations for each missing skill."""
    all_recs = []
    for skill in missing_skills:
        all_recs.extend(fetch_coursera_courses(skill))
    return all_recs

def fetch_internships(skills, location="India", limit=5):
    """Fetch internships from JSearch API (RapidAPI)."""
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    internships = []
    for skill in skills:
        params = {
            "query": f"{skill} internship in {location}",
            "page": "1",
            "num_pages": "1"
        }
        response = requests.get(JSEARCH_URL, headers=headers, params=params)
        if response.status_code == 200:
            jobs = response.json().get("data", [])
            for job in jobs[:limit]:
                internships.append({
                    "title": job.get("job_title"),
                    "company": job.get("employer_name"),
                    "location": job.get("job_city"),
                    "url": job.get("job_apply_link"),
                    "skill": skill
                })
    return internships

# ---------------- API ----------------
@app.route("/analyze-job", methods=["POST"])
def analyze_job():
    data = request.get_json(force=True)
    resume = data.get("resume", "")
    job_posting = data.get("job_posting", "")
    location = data.get("location", "India")

    resume_skills = extract_skills(resume)
    job_skills = extract_skills(job_posting)
    missing_skills = job_skills - resume_skills

    # Real course recommendations from Coursera
    course_recs = recommend_courses(missing_skills)

    # Real internship recommendations from JSearch
    internship_recs = fetch_internships(missing_skills, location)

    return jsonify({
        "resume_skills": list(resume_skills),
        "job_required_skills": list(job_skills),
        "missing_skills": list(missing_skills),
        "course_recommendations": course_recs,
        "internship_recommendations": internship_recs
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(port=5001, debug=True)
