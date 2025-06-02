# How to Import Adzuna Job Data into MySQL with Docker

This guide explains how to set up a MySQL database using Docker and import job data from the Adzuna API into MySQL using a Python script. It is suitable for local development and testing.

---

## 1. Create MySQL Docker Container

### 1.1 Create `docker-compose.yml`
In your project root directory (e.g., `/Users/kevinwang/Documents/10 Capstone`), create a file named `docker-compose.yml` with the following content:

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    container_name: jobquest-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: jobquest
      MYSQL_USER: jobuser
      MYSQL_PASSWORD: jobpass
    ports:
      - "3306:3306"
    volumes:
      - ./mysql_data:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password
```

### 1.2 Start MySQL Container
Run the following command in your terminal:

```bash
docker-compose up -d
```

This will start MySQL on your local port 3306.

---

## 2. Install Python Dependencies

Make sure you have Python 3 installed. Then install the required packages:

```bash
pip install pymysql requests
```

---

## 3. Configure Database Connection

The Python script (`src/epic1_job_to_mysql.py`) uses the following default settings:

```python
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'jobuser')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'jobpass')
MYSQL_DB = os.getenv('MYSQL_DB', 'jobquest')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
```

You can change these via environment variables if needed.

---

## 4. Run the Import Script

### 4.1 Import Directly from Adzuna API

Run the following command:

```bash
python3 src/epic1_job_to_mysql.py
```

The script will:
- Fetch job data from the Adzuna API (3 pages, 50 jobs per page)
- Create the `jobs` table if it does not exist
- Truncate the table before import
- Insert all job records into MySQL

### 4.2 Check Import Results

You can use a MySQL client (DBeaver, TablePlus, etc.) or the command line:

```bash
docker exec -it jobquest-mysql mysql -ujobuser -pjobpass jobquest
```

Then run:

```sql
SELECT COUNT(*) FROM jobs;
SELECT * FROM jobs LIMIT 5;
```

---

## 5. Troubleshooting

- **Port in use**: If 3306 is occupied, change to `3307:3306` in `docker-compose.yml` and set `MYSQL_PORT=3307` in your script.
- **Missing dependencies**: Run `pip install pymysql requests`.
- **API Key issues**: Check your Adzuna `APP_ID` and `APP_KEY`.
- **MySQL connection errors**: Ensure the container is running and credentials match.

---

## 6. (Optional) Import from CSV

If you want to import from a CSV file, use a script like `insert_jobs_to_mysql.py` and set the `CSV_FILE` variable to your CSV path.

---

## Summary

1. `docker-compose up -d` to start MySQL
2. `pip install pymysql requests` to install dependencies
3. `python3 src/epic1_job_to_mysql.py` to import data

If you encounter any issues, check the troubleshooting section or contact the project maintainer.
