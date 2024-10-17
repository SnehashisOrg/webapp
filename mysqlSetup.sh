#!/bin/bash

set -e

# Set database names
export MYSQL_DATABASE=csye6225
export TEST_MYSQL_DATABASE=test_db

# Start and enable MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Create user, set password, and create databases
# sudo mysql -e "CREATE USER IF NOT EXISTS 'ubuntu'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password123';"
sudo mysql -e "CREATE USER IF NOT EXISTS 'ubuntu'@'localhost';"
sudo mysql -e "ALTER USER 'ubuntu'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password123';"
sudo mysql -e "FLUSH PRIVILEGES;"
sudo systemctl restart mysql

sudo mysql -e "CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE};"
sudo mysql -e "CREATE DATABASE IF NOT EXISTS ${TEST_MYSQL_DATABASE};"
sudo mysql -e "GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE}.* TO 'ubuntu'@'localhost';"
sudo mysql -e "GRANT ALL PRIVILEGES ON ${TEST_MYSQL_DATABASE}.* TO 'ubuntu'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# sudo mysql -e "CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE};"
# sudo mysql -e "CREATE DATABASE IF NOT EXISTS ${TEST_MYSQL_DATABASE};"

# # Grant privileges
# sudo mysql -e "GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE}.* TO 'ubuntu'@'localhost';"
# sudo mysql -e "GRANT ALL PRIVILEGES ON ${TEST_MYSQL_DATABASE}.* TO 'ubuntu'@'localhost';"
# sudo mysql -e "FLUSH PRIVILEGES;"

# # Restart MySQL to apply changes
# sudo systemctl restart mysql

# echo "MySQL setup completed successfully."