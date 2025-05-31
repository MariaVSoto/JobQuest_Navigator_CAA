create table jobs



CREATE TABLE jobs (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(255),
    created DATETIME,
    description TEXT,
    redirect_url TEXT,
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    latitude DOUBLE,
    longitude DOUBLE,
    distance_km DOUBLE,
    company_address VARCHAR(255),
    company_latitude DOUBLE,
    company_longitude DOUBLE
);