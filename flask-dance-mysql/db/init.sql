CREATE DATABASE IF NOT EXISTS your_database_name;
USE your_database_name;

-- Create your tables here
-- Example:
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);