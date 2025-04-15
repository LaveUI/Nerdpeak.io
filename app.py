from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_mysqldb import MySQL
import bcrypt
import time
try:
    from auth import auth
except ImportError as e:
    auth = None
    print(f"Error importing 'auth' module: {e}")


app = Flask(__name__)

# Database Configuration
app.secret_key = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'vaibhav12'
app.config['MYSQL_DB'] = 'user_auth'

mysql = MySQL(app)

# Register Blueprints
if auth:
    app.register_blueprint(auth)
else:
    print("Auth blueprint is not available. Skipping registration.")


# Route for rendering the frontend
@app.route('/')
def home():
    return render_template('index1.html')

#fetch codeforeces contest

import time

def fetch_codeforces_contests():
    url = "https://codeforces.com/api/contest.list"
    response = requests.get(url)
    
    if response.status_code == 200:
        contests = response.json().get("result", [])
        
        # Get current timestamp
        current_time = int(time.time())

        upcoming = [
            {
                "name": contest["name"],
                "startTime": contest["startTimeSeconds"],
                "url": f"https://codeforces.com/contest/{contest['id']}"
            }
            for contest in contests
            if contest["phase"] == "BEFORE" and contest["startTimeSeconds"] > current_time
        ]

        return upcoming[:3]  # Return top 3 upcoming contests
    return []


# Fetch LeetCode statistics

def fetch_leetcode_stats(username):
    url = "https://leetcode.com/graphql"
    query = {
        "operationName": "getUserProfile",
        "variables": {"username": username},
        "query": """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
        }
        """
    }
    response = requests.post(url, json=query)
    data = response.json()

    if "data" in data and data["data"]["matchedUser"]:
        stats = data["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
        return {
            "totalSolved": stats[0]["count"],
            "easySolved": stats[1]["count"],
            "mediumSolved": stats[2]["count"],
            "hardSolved": stats[3]["count"]
        }
    return None

# Fetch LeetCode skills
def fetch_leetcode_skills(username):
    url = "https://leetcode.com/graphql"
    query = {
        "operationName": "getUserProfileSkills",
        "variables": {"username": username},
        "query": """
        query getUserProfileSkills($username: String!) {
            matchedUser(username: $username) {
                tagProblemCounts {
                    advanced {
                        tagName
                        problemsSolved
                    }
                    intermediate {
                        tagName
                        problemsSolved
                    }
                    fundamental {
                        tagName
                        problemsSolved
                    }
                }
            }
        }
        """
    }
    response = requests.post(url, json=query)
    data = response.json()

    skills = []
    if "data" in data and data["data"]["matchedUser"]:
        categories = ["fundamental", "intermediate", "advanced"]
        for category in categories:
            for skill in data["data"]["matchedUser"]["tagProblemCounts"].get(category, []):
                skills.append({
                    "category": category.capitalize(),
                    "name": skill["tagName"],
                    "solved": skill["problemsSolved"]
                })
    return skills

# Fetch Codeforces statistics
def fetch_codeforces_data(username):
    url = f"https://codeforces.com/api/user.info?handles={username}"
    response = requests.get(url)
    if response.status_code == 200:
        cf_data = response.json().get("result", [{}])[0]
        return {
            "rating": cf_data.get("rating", 0),
            "maxRating": cf_data.get("maxRating", 0),
            "rank": cf_data.get("rank", "Unranked"),
            "maxRank": cf_data.get("maxRank", "Unranked")
        }
    return None

# DSA Tracker API route
@app.route('/dsa_tracker', methods=['GET'])
def dsa_tracker():
    leetcode_username = request.args.get('leetcode')
    codeforces_username = request.args.get('codeforces')

    response_data = {
        "LeetCode": {"totalSolved": 0, "easySolved": 0, "mediumSolved": 0, "hardSolved": 0, "skills": []},
        "Codeforces": {"rating": 0, "maxRating": 0, "rank": "Unranked", "maxRank": "Unranked"},
        "Upcoming Contests": fetch_codeforces_contests()
    }

    if leetcode_username:
        stats = fetch_leetcode_stats(leetcode_username)
        skills = fetch_leetcode_skills(leetcode_username)
        if stats:
            response_data["LeetCode"].update(stats)
        if skills:
            response_data["LeetCode"]["skills"] = skills

    if codeforces_username:
        cf_data = fetch_codeforces_data(codeforces_username)
        if cf_data:
            response_data["Codeforces"].update(cf_data)

    return jsonify(response_data)






if __name__ == '__main__':
    app.run(debug=True)
