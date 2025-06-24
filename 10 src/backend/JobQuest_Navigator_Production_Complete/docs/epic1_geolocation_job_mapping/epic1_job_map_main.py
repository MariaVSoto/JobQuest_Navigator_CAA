import requests
import csv
import os
from math import radians, cos, sin, asin, sqrt
#import time

# Set your Adzuna and Google API keys
APP_ID = os.getenv('ADZUNA_APP_ID', '3aea9429')
APP_KEY = os.getenv('ADZUNA_APP_KEY', '47c6c2410fe3c75a1a1e7e90eb21fa95')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

# Haversine formula to calculate distance between two lat/lon points (in km)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# Get user's city and coordinates from IP
user_ip_info = requests.get('https://ipinfo.io/json').json()
user_city = user_ip_info.get('city', '').lower()
user_loc = user_ip_info.get('loc', '0,0')
user_lat, user_lon = map(float, user_loc.split(','))
print(f"Detected user city: {user_city}, coordinates: {user_lat}, {user_lon}")

# Fetch jobs from Adzuna
API_URL = f"https://api.adzuna.com/v1/api/jobs/gb/search/1?app_id={APP_ID}&app_key={APP_KEY}"
PARAMS = {
    'results_per_page': 50,
    'content-type': 'application/json',
}
response = requests.get(API_URL, params=PARAMS)
response.raise_for_status()
data = response.json()
jobs = data.get('results', [])

# Geocode a location string to lat/lon using Google Geocoding API
def geocode_location(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address, 'key': GOOGLE_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=10)
        results = resp.json().get('results')
        if results:
            location = results[0]['geometry']['location']
            return location['lat'], location['lng']
    except Exception as e:
        print(f"Geocoding error for '{address}': {e}")
    return None, None

# # Find company office location in the city using Google Places API
# def find_company_location(company, city):
#     if not company or not city:
#         return None, None, None
#     query = f"{company} {city}"
#     url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
#     params = {
#         'query': query,
#         'key': GOOGLE_API_KEY
#     }
#     try:
#         resp = requests.get(url, params=params, timeout=10)
#         results = resp.json().get('results', [])
#         if results:
#             place = results[0]
#             address = place.get('formatted_address')
#             lat = place['geometry']['location']['lat']
#             lng = place['geometry']['location']['lng']
#             return address, lat, lng
#     except Exception as e:
#         print(f"Places API error for '{query}': {e}")
#     return None, None, None

# Process jobs: filter by city, geocode, calculate distance
output_jobs = []
for idx, job in enumerate(jobs):
    location_str = job.get('location', {}).get('display_name', '')
    company = job.get('company', {}).get('display_name', '')
    if user_city and user_city in location_str.lower():
        # Try to get lat/lon from Adzuna data if available
        lat = job.get('latitude')
        lon = job.get('longitude')
        if lat is None or lon is None:
            lat, lon = geocode_location(location_str)
        if lat is not None and lon is not None:
            distance = haversine(user_lat, user_lon, lat, lon)
        else:
            distance = ''
        # 注释掉公司Google Places定位部分
        #comp_addr, comp_lat, comp_lon = find_company_location(company, user_city)
        output_jobs.append({
            'id': job.get('id', ''),
            'title': job.get('title', ''),
            'company': company,
            'location': location_str,
            'created': job.get('created', ''),
            'description': job.get('description', ''),
            'redirect_url': job.get('redirect_url', ''),
            'salary_min': job.get('salary_min', ''),
            'salary_max': job.get('salary_max', ''),
            'latitude': lat,
            'longitude': lon,
            'distance_km': distance,
            'company_address': '',
            'company_latitude': '',
            'company_longitude': ''
        })

# Write results to CSV
FIELDS = [
    'id', 'title', 'company', 'location', 'created', 'description', 'redirect_url',
    'salary_min', 'salary_max', 'latitude', 'longitude', 'distance_km',
    'company_address', 'company_latitude', 'company_longitude'
]
csv_file = 'epic1_jobs_with_company_location.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    for job in output_jobs:
        writer.writerow(job)

print(f"Found {len(output_jobs)} jobs in your city (without company Google Places info). Results saved to {csv_file}") 