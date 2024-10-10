# CSYE6225: Network Structures & Cloud Computing

## Assignment 03 

### Updates to the assignment are as follows:
<b>1. Branch protection rule:</b> <i>applied on main branch of <b>Org repo</b>; enforced PR check no merge on failed check - <b style="color:green">verified ✅</b></i></br>
<b>2. GitHub Actions:</b> <i>created and tested for the repo; runs all the pytest unit test cases; creates test mysql database for testing - <b style="color:green">verified ✅</b></i></br>

### Assignment Stack
<b>1. Server:</b> <i>Ubuntu 24.04 LTS</i></br>
<b>2. Programming Language:</b> <i>Python</i></br>
<b>3. Database:</b> <i>MySQL</i></br>
<b>4. ORM:</b> <i>SQLAlchemy</i></br>
<b>5. UI Framework:</b> <i>N/A</i></br>
<b>6. CSS:</b> <i>N/A</i></br>
<b>7. Unit Test:</b> <i>pytest</i></br>

#### Prerequisites to run:

<i>1. Python should be installed in your system</i></br>
<i>2. MySQL Community Server should be installed, after that you can download MySQL Workbench ease of accessing different MySQL resources</i></br>
<i>3. You can install Postman so as to test the API endpoints seamlessly</i></br>
<i>4. Should have git installed in your system</i></br>

#### Steps to run this on Droplet
<i>1. Clone this repo in your local, use the below commands in your terminal:</i>
```
git clone <github_repo_link>
cd <github_repo>
```

<i>2. SSH into the digital ocean droplet from terminal and copy the files from github unzipped folder</i>
```
ssh digitaloceanhost
mkdir csye6225
scp <local-dir> -d digitalocean:/root/csye6225/
```

<i>3. Install the necessary packages</i>
```
sudo apt update

sudo apt install -y mysql-server

sudo apt install -y python3
sudo apt install -y python3-pip

sudo apt install -y python3-venv

sudo apt install -y unzip
```

<i>4. unzip the assignment files</i>
```
cd csye6225
unzip <assignment_file_name.zip> -d <path_to_unzip>
```

<i>5. create virtual environment and install python packages</i>
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

<i>6. setup mysql root password</i>
```
# to check if mysql is active or not

sudo systemctl status mysql
sudo mysql

#Replace your_secure_password with a strong password of your choice.

ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_secure_password';

FLUSH PRIVILEGES;
EXIT;

sudo systemctl restart mysql

Test the Connection
mysql -u root -p
```

<i>7. check the firewall settings for droplet</i>
```
sudo ufw status

# if not active, enable it active
sudo ufw enable

sudo ufw allow 8000

```

<i>8. run the python server</i>
```
python app.py
```
#### Steps to run this locally:
<i>1. Clone this repo in your local, use the below commands in your terminal:</i>
```
git clone <github_repo_link>
cd <github_repo>
```

<i>2. Run the below command in the terminal to install the python packages:</i>
```
pip install -r requirements.txt
```

<i>3. Create a .env file in the repo, and add the values for database credentials</i>

<i>4. Run the app.py file, uvicorn will run the FastAPI server</i>
```
python app.py
```

<i>5. Use Postman to validate the API endpoints.</i>

<i>6. To check for the status <b>503: Service Unavailable</b>, stop the MySQL server instance and hit the API from Postman</i>
