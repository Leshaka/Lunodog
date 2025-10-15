CREATE USER 'lduser'@'localhost' IDENTIFIED BY 'insert-a-password-here';
CREATE DATABASE lddb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
GRANT ALL ON lddb.* TO 'lduser'@'localhost';
GRANT FILE ON *.* TO 'lduser'@'localhost';