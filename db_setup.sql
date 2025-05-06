CREATE DATABASE IF NOT EXISTS inventory;
USE inventory;

CREATE TABLE Product (
  product_id VARCHAR(10) PRIMARY KEY,
  name VARCHAR(100),
  quantity INT,
  price DECIMAL(10,2)
);

CREATE TABLE Location (
  location_id VARCHAR(10) PRIMARY KEY,
  name VARCHAR(100)
);

CREATE TABLE ProductMovement (
  movement_id INT AUTO_INCREMENT PRIMARY KEY,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  product_id VARCHAR(10),
  from_location VARCHAR(10),
  to_location VARCHAR(10),
  qty INT,
  FOREIGN KEY (product_id) REFERENCES Product(product_id),
  FOREIGN KEY (from_location) REFERENCES Location(location_id),
  FOREIGN KEY (to_location) REFERENCES Location(location_id)
);
