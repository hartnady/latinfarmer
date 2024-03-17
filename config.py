# Database setup
username = "YOUR_MYSQL_USERNAME_HERE"
password = "YOUR_MYSQL_PASSWORD_HERE"
hostname = f"{username}.mysql.pythonanywhere-services.com"
databasename = f"{username}$default"

SQLALCHEMY_DATABASE_URI = (
    f"mysql://{username}:{password}@{hostname}/{databasename}"
)
SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 299}
SQLALCHEMY_TRACK_MODIFICATIONS = False 

OPEN_AI_KEY = 'YOUR_OPEN_AI_KEY_HERE'
