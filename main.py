import configparser
from flask import Flask, render_template, request
import json
import requests
from requests.models import PreparedRequest
from common import database
from models.base import User, Repo, RepoStatus
from cryptography.fernet import Fernet

app = Flask(__name__, template_folder="views")
db_session = None
crypto_instance = None

@app.route("/")
def index():
    base_url = "https://github.com/login/oauth/authorize"

    query_params = {
        "client_id":client_id,
        "scope":"user,repo"
    }

    req = PreparedRequest()
    req.prepare_url(base_url, query_params)

    return render_template("index.html", url=req.url)

@app.route("/callback")
def callback():
    session_code = request.args.get('code', '')
    query_params = {
        "client_id":client_id,
        "client_secret":client_secret,
        "code":session_code
    }
    
    req = PreparedRequest()
    req.prepare_url("https://github.com/login/oauth/access_token", query_params)
    response = requests.post(req.url, headers={
        "Accept": "application/json"
    })
    
    if response.status_code == 200:
        print(response.text)
        response_body = response.json()
        access_token = response_body["access_token"]
        if access_token == None or access_token == "":
            return
        response_user = requests.post("https://api.github.com/user", headers={
            "Accept":"application/vnd.github+json",
            "Authorization": f"Bearer {access_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        })

        if response_user.status_code == 200:
            response_user_body = response_user.json()
            id = response_user_body["id"]
            username = response_user_body["login"]
            name = response_user_body["name"]
            email = response_user_body["email"]
            encrypted_access_token = crypto_instance.encrypt(access_token.encode())
            new_user = User(id=id, username=username, name=name, email=email, access_token=encrypted_access_token)
            db_session.add(new_user)
            db_session.commit()
    else:
        app.logger.error("failed user login")

    response_body = json.loads(response.text)
    print(response)

    return render_template("callback.html")

@app.route("/user/repo")
def repo():
    username = request.args.get('username', '')
    user = db_session.query(User).filter(User.username == username).first()
    if user == None:
        return
    
    decrypted_access_token = crypto_instance.decrypt(user.access_token).decode()
    
    response_repo = requests.get(f"https://api.github.com/users/{username}/repos", headers={
        "Accept":"application/vnd.github+json",
        "Authorization": f"Bearer {decrypted_access_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    })

    if response_repo.status_code == 200:
        response_repo_json = response_repo.json()
        for repo in response_repo_json:
            id = repo["id"]
            name = repo["name"]
            stars = repo["stargazers_count"]
            status = RepoStatus.private if repo["private"] is True else RepoStatus.public
            user_id = user.id
            new_repo = Repo(id=id, name=name, stars=stars, status=status, user_id=user_id)
            db_session.add(new_repo)
            db_session.commit()
    else:
        app.logger.error("failed to fetch repo")
    



if __name__ == "__main__":
    # Read config.ini file
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    # Initialise DB session
    db_creds = config["DATABASE"]
    db_conn = database.DatabaseConnection(host=db_creds["DB_HOST"], port=int(db_creds["DB_PORT"]), user=db_creds["DB_USER"], password=db_creds["DB_PASS"], database=db_creds["DB_NAME"])
    db_session = db_conn.get_session()

    # Initialise crypto instance
    access_secret = config["APP"]["ACCESS_SECRET"]
    crypto_instance = Fernet(str(access_secret))

    # Migrate tables
    if db_creds["ENABLE_MIGRATION"] is True:
        db_conn.drop_all_tables()
        db_conn.create_tables()

    # Gather all environment variables from config.ini file
    global client_id
    client_id = config["APP"]["CLIENT_ID"]
    global client_secret
    client_secret = config["APP"]["CLIENT_SECRET"]

    # Start HTTP Server
    app.run(host='127.0.0.1', port=config["APP"]["PORT"])



    # requests.get("https://github.com/login/oauth/authorize", params={"scope":"user:email", "client_id": client_id})