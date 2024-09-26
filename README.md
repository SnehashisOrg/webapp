# CSYE6225: Network Structures & Cloud Computing

## Assignment 01

### Assignment Stack
<b>1. Server:</b> <i>Ubuntu 24.04 LTS</i>
<b>2. Programming Language:</b> <i>Python</i>
<b>3. Database:</b> <i>MySQL</i>
<b>4. ORM:</b> <i>SQLAlchemy</i>
<b>5. UI Framework:</b> <i>N/A</i>
<b>6. CSS:</b> <i>N/A</i>

#### Prerequisites to run:

<i>1. Python should be installed in your system</i>
<i>2. MySQL Community Server should be installed, after that you can download MySQL Workbench ease of accessing different MySQL resources</i>
<i>3. You can install Postman so as to test the API endpoints seamlessly</i>
<i>4. Should have git installed in your system</i>

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
