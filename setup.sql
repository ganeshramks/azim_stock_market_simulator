CREATE USER IF NOT EXISTS 'azim'@'localhost' IDENTIFIED BY 'azim123';
CREATE DATABASE IF NOT EXISTS azim;
GRANT ALL PRIVILEGES ON azim.* TO 'azim'@'localhost';

USE azim;
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS trades;
DROP TABLE IF EXISTS portfolios;
DROP TABLE IF EXISTS stock_prices;
SET FOREIGN_KEY_CHECKS=1;

CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email_id VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    cash_balance FLOAT DEFAULT 0.0,
    current_ts DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ACTIVE', 'DELETED') NOT NULL,
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS trades (
    id INT PRIMARY KEY AUTO_INCREMENT,
    portfolio_id INT NOT NULL,
    stock_symbol VARCHAR(10) NOT NULL,
    qty INT NOT NULL,
    price FLOAT NOT NULL,
    side ENUM('BUY', 'SELL') NOT NULL,
    execution_ts DATETIME NOT NULL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

CREATE TABLE IF NOT EXISTS stock_prices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    stock_symbol VARCHAR(10) NOT NULL,
    price FLOAT NOT NULL,
    timestamp DATETIME NOT NULL,
    INDEX (stock_symbol),
    INDEX (timestamp)
);

-- Test user setup

CREATE USER IF NOT EXISTS 'azim_test'@'localhost' IDENTIFIED BY 'azim_test_123';
CREATE DATABASE IF NOT EXISTS azim_test;
GRANT ALL PRIVILEGES ON azim_test.* TO 'azim_test'@'localhost';