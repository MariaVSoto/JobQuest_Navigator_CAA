from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import json
import requests
import logging
import os
from .skill_extractor import SkillExtractor
from .models import Skill, Certification, JobRole
import pymysql

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

skill_extractor = SkillExtractor()

# JSearch API configuration
RAPIDAPI_KEY = "95119f8c32msh4755b0c295ab03cp11b64bjsn30489b553ac9"
RAPIDAPI_HOST = "jsearch.p.rapidapi.com"

def home(request):
    return render(request, 'skill_analysis/test.html')

@csrf_exempt
def analyze_skills(request):
    if request.method == 'POST':
        try:
            # Log the incoming request
            logger.debug("Received analyze_skills request")
            
            data = json.loads(request.body)
            resume_text = data.get('resume_text', '')
            target_role = data.get('target_role', '')
            location = data.get('location', 'united states')

            if not resume_text:
                return JsonResponse({'status': 'error', 'message': 'Resume text is required'}, status=400)
            if not target_role:
                return JsonResponse({'status': 'error', 'message': 'Target role is required'}, status=400)

            # Extract skills from resume
            logger.debug("Extracting skills from resume")
            resume_skills = skill_extractor.extract_skills(resume_text)
            logger.debug(f"Found resume skills: {resume_skills}")
            
            # Get job descriptions
            logger.debug(f"Fetching job descriptions for role: {target_role}")
            job_descriptions = fetch_job_descriptions(target_role, location)
            if not job_descriptions:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No job descriptions found for the given role'
                }, status=404)
            
            # Build role profile from job descriptions
            logger.debug("Building role skill profile")
            role_profile = skill_extractor.build_role_skill_profile(job_descriptions)
            
            # Extract skills from job descriptions
            logger.debug("Extracting skills from job descriptions")
            job_skills = skill_extractor.extract_skills('\n\n'.join(job_descriptions))
            logger.debug(f"Found job skills: {job_skills}")
            
            # Get missing skills
            missing_skills = set(job_skills) - set(resume_skills)
            
            # Get certifications with role context
            logger.debug("Getting certifications with role context")
            certifications = skill_extractor.get_certifications(
                list(missing_skills),
                role_profile=role_profile
            )

            # Prepare response with certification recommendations
            response_data = {
                'status': 'success',
                'recommended_certifications': [
                    {
                        'name': cert['name'],
                        'description': cert['description'],
                        'url': cert['link'],
                        'matched_skills': cert['matched_skills'],
                        'relevance_score': cert['relevance_score']
                    }
                    for cert in certifications
                ]
            }

            logger.debug(f"Sending response: {response_data}")
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': f'Error processing request: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'}, status=405)

def fetch_job_descriptions(target_role, location):
    """Fetch job descriptions using JSearch API"""
    try:
        url = "https://jsearch.p.rapidapi.com/search"
        querystring = {
            "query": f"{target_role} in {location}",
            "num_pages": "1",
            "page": "1"
        }
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }
        
        logger.debug(f"Making API request to JSearch for role: {target_role}")
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"Received response from JSearch API: {data}")
        
        if 'data' in data:
            job_descriptions = [job['job_description'] for job in data['data']]
            logger.debug(f"Found {len(job_descriptions)} job descriptions")
            return job_descriptions
        else:
            logger.warning("No job data found in API response")
            return []
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching job descriptions from API: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in fetch_job_descriptions: {str(e)}")
        return []

@csrf_exempt
def roadmap_for_job(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            job_id = data.get('job_id')
            resume_text = data.get('resume_text', '')
            target_role = data.get('target_role', '')
            if not resume_text:
                return JsonResponse({'status': 'error', 'message': 'resume_text is required'}, status=400)

            # Extract resume skills
            resume_skills = skill_extractor.extract_skills(resume_text)

            # Connect to MySQL
            MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
            MYSQL_USER = os.getenv('MYSQL_USER', 'jobuser')
            MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'jobpass')
            MYSQL_DB = os.getenv('MYSQL_DB', 'jobquest')
            MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
            conn = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                port=MYSQL_PORT,
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            description = None
            # Prefer job_id if provided
            if job_id:
                cursor.execute('SELECT description FROM jobs WHERE id=%s', (job_id,))
                row = cursor.fetchone()
                if row:
                    description = row[0]
            # If no job_id, try to find a job by target_role
            elif target_role:
                cursor.execute('SELECT description FROM jobs WHERE title LIKE %s LIMIT 1', (f"%{target_role}%",))
                row = cursor.fetchone()
                if row:
                    description = row[0]
            cursor.close()
            conn.close()
            if not description:
                return JsonResponse({'status': 'error', 'message': 'No matching job found for the given job_id or target_role'}, status=404)

            # Always extract skills from the job description on the fly
            job_skills = skill_extractor.extract_skills(description)

            # Advanced: combine and deduplicate skills
            all_skills = list(set(job_skills + resume_skills))
            # Optionally, build a role profile from job description
            role_profile = skill_extractor.build_role_skill_profile([description])
            # Get certifications with advanced matching and job title for domain filtering
            certifications = skill_extractor.get_certifications(all_skills, role_profile=role_profile, job_title=(target_role or ''))

            response_data = {
                'status': 'success',
                'job_skills': job_skills,
                'resume_skills': resume_skills,
                'recommended_certifications': [
                    {
                        'name': cert['name'],
                        'description': cert['description'],
                        'url': cert['link'],
                        'matched_skills': cert['matched_skills'],
                        'relevance_score': cert['relevance_score']
                    }
                    for cert in certifications
                ]
            }
            return JsonResponse(response_data)
        except Exception as e:
            logger.error(f"Error in roadmap_for_job: {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'}, status=405)

@require_GET
def search_jobs(request):
    title = request.GET.get('title', '')
    if not title:
        return JsonResponse({'status': 'error', 'message': 'Missing title parameter'}, status=400)
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'jobuser')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'jobpass')
    MYSQL_DB = os.getenv('MYSQL_DB', 'jobquest')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    conn = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    # Use LIKE for partial match, limit to 20 results
    cursor.execute("SELECT id, title, company, location FROM jobs WHERE title LIKE %s LIMIT 20", (f"%{title}%",))
    jobs = [
        {'id': row[0], 'title': row[1], 'company': row[2], 'location': row[3]}
        for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()
    return JsonResponse(jobs, safe=False)