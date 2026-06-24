-- database.sql
-- Run this file FIRST in MySQL to create the database and table

-- 1. Create the database
CREATE DATABASE IF NOT EXISTS login_system;

-- 2. Use it
USE login_system;

-- 3. Create the users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- That's it! The table is ready to store users.
-- 'password' will store a HASHED password, never plain text.
