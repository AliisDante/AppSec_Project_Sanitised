import datetime
import json

from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user

import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb://localhost/"
client = MongoClient(uri, server_api=ServerApi('1'))

# create database
reports_db = client["reports"]

from app import app


class Activity:
    def __init__(self, name):
        self.name = name

# generate report for the previous week
test_activities = [Activity("Biking"), Activity("Bus")]
@app.route("/calculator")
@login_required
def get_calculator():
    return render_template("calculator/emission_tracker.html", activities=test_activities, current_user=current_user)

# use report to show result
@app.route("/calculator/results")
@login_required
def get_results():
    # fetch reports by user in the past month
    # get the hightest emission activity of the 3 highest category in the past month, emissions in the past month by week
    return render_template("calculator/emission_report.html", current_user=current_user)

# calculator api

# sample data
"""
{
    "activities": [
            {
                "item":"public mrt",
                "category":"transport",
                "emission":25
            },
            {
                "item":"chicken rice",
                "category":"food",
                "emission":35
            },
            {
                "item":"second hand shoes",
                "category":"shopping",
                "emission":5
            },
            {
                "item":"bus",
                "category":"transport",
                "emission":35
            },
            {
                "item":"bubble tea",
                "category":"food",
                "emission":10
            },
            {
                "item":"new clothes",
                "category":"shopping",
                "emission":55
            }
    ]
}
"""

# secured version

# API9:2023 - Improper Inventory Management
# Solution: Proper API documentation
@app.route("/calculator/api/v2")
@login_required
def get_documentation():
    return render_template("calculator/api_documentation.html")


""" activitiy_format = {
    "activities": [
        {
            "item": str,
            "category": str,
            "emission": int
        }
    ]
} """


# extra new feature
@app.route("/calculator/api/v2/share", methods=['POST'])
@login_required
def post_calculate_claim_v2():
    print("reach")

    # check if can claim
    rep_data = list(reports_db[f"week-{weeks_since_epoch()}"].find({
        "username": current_user.username
    }).sort("report id", -1))

    # return errors
    submit = len(rep_data)
    if not submit:
        return {
            "code": -2,
            "comment": "You have not submitted!"
        }

    claim = rep_data[0]["claimed"]
    if claim:
        return {
            "code": -1,
            "comment": "Points already claimed!"
        }

    # if can, calculate how much


    # increment points
    awarded = 0
    last_week_total = 0

    last_week_total += rep_data[0]["categories"]["food"]["total emission"]
    last_week_total += rep_data[0]["categories"]["transport"]["total emission"]
    last_week_total += rep_data[0]["categories"]["shopping"]["total emission"]

    previous_3_weeks_total = 0
    hits = 0

    for i in range(1,5):
        if i != weeks_since_epoch():
            rep_data = list(reports_db[f"week-{i}"].find({
                "username": current_user.username
            }).sort("report id", -1))

            if len(rep_data) != 0:
                hits += 1
                previous_3_weeks_total += rep_data[0]["categories"]["food"]["total emission"]
                previous_3_weeks_total += rep_data[0]["categories"]["transport"]["total emission"]
                previous_3_weeks_total += rep_data[0]["categories"]["shopping"]["total emission"]

    print(previous_3_weeks_total)

    if hits == 0 or previous_3_weeks_total/hits == 0:  
        return {
            "code": -3,
            "comment": "You have not submitted in the last 3 weeks!"
        }

    percent_diff = (last_week_total/(previous_3_weeks_total/hits))*100
    print(percent_diff)

    if percent_diff < 100:
        awarded = (percent_diff//10)*20
        print(awarded)
        current_user.points += awarded

        reports_db[f"week-{weeks_since_epoch()}"].update_one({"report id":rep_data[0]["report id"]},{"$set":{"claimed":1}})
    return {
        "code": 1,
        "comment": "Successfully claimed points!"
    }

# API4:2023 - Unrestricted Resource Consumption
# Solution: limit enforced
@app.route("/calculator/api/v2/submit", methods=['POST'])
@login_required
def post_calculate_submit_v2():
    # check if submit before, if have then cannot
    activities = request.get_json()

    if " ".join(list(activities.keys())).find('activities') == -1:
        return {
            "report_id": -1,
            "comment": "Bad query passed, no activity key found!"
        }

    activities = activities["activities"]
    print(activities)

    if str(activities).find("$") != -1:
        return {
            "report_id": -1,
            "comment": "Bad query passed, attempt to use query selectors!"
        }

    next_id = reports_db[f"week-{weeks_since_epoch()}"].count_documents({})+1

    summary = {
        "report id": next_id,
        "username":current_user.username,
        "data submitted":datetime.datetime.today().isoformat(),
        "claimed": 0,
        "categories":{
            "food": {
                "highest item":"",
                "highest emission":0,
                "total emission":0
            },
            "transport": {
                "highest item":"",
                "highest emission":0,
                "total emission":0
            },
            "shopping": {
                "highest item":"",
                "highest emission":0,
                "total emission":0
            }
        }
    }

    if not (type(activities) is list):
        return {
                "report_id": -1,
                "comment": "Bad query passed, activity should be a list!"
        }

    for activity in activities:
            
        if " ".join(list(activity.keys())).find('item') == -1 or " ".join(list(activity.keys())).find('category') == -1 or " ".join(list(activity.keys())).find('emission') == -1:
            return {
                "report_id": -1,
                "comment": "Bad query passed, each object in activity list should have the following keys - item, category, emission!"
            }

        print(activity)
        if activity["category"] not in ["food","transport","shopping"]:
            continue
            
        # insecure miscongiuration
        # don't validate, so it crash and in debug mode

        # add to total for category
        summary["categories"][activity["category"]]["total emission"] += activity["emission"]

        # check if is highest, then update if needed
        if summary["categories"][activity["category"]]["highest emission"] < activity["emission"]:
            summary["categories"][activity["category"]]["highest emission"] = activity["emission"]
            summary["categories"][activity["category"]]["highest item"] = activity["item"]

    # total emission

    # store data
    print(weeks_since_epoch())
    print(summary)

    # should i use the sql database? hmmmm
    # oh i can use mongo

    # sample data
    # 4 clusters, 1 for a week
    # each cluster have records which are the week's reports

    # check if have submit before
    # only if no or its many weeks ago

    finding_records = list(reports_db[f"week-{weeks_since_epoch()}"].find({"username": current_user.username}).sort("report id", -1))

    if len(finding_records) == 0 or days_old(finding_records[0]["data submitted"][0:10]) > 14:
        reports_db[f"week-{weeks_since_epoch()}"].insert_one(summary)
        return {
            "report_id": next_id,
            "comment": "Successfully processed your emission activities!"
        }
    else:
        return {
            "report_id": -1,
            "comment": "You have already submitted last week's emissions!"
        }

def days_old(date_time):
  now = datetime.datetime.now().date()
  delta = now - datetime.date.fromisoformat(date_time)
  return delta.days

# API1:2023 - Broken Object Level Authorization
# Solution: Make sure user has permission to access report
@app.route("/calculator/api/v2/report/id/<id>")
@login_required
def get_calculate_report_by_id_v2(id):
    if id.find("-") == -1:
        return {
            "status": "invalid format, can't find a dash!"
        }
    
    try:
        print(id.split("-"))
        week, seq = id.split("-")
        print(week)
        week, seq = int(week), int(seq)
        print(week, seq)
    except:
        return {
            "status": "invalid format, give two integers seperated by a dash!"
        }
    
    if week < 1 or week > 4:
        return {
            "status": "invalid format, first integer can only be from zero to four!"
        }

    # zero already means no have so should not query db
    if seq == 0:
        return {
            "status": "invalid, no report for week"
        }

    # try to locate data
    print(reports_db[f"week-{week}"].count_documents({}))
    rep_data = list(reports_db[f"week-{week}"].find({
        "report id": int(seq)    
    }))

    print(rep_data)

    # return data
    req_response = {
        "categories": {
                "food": {
                    "highest item": "",
                    "highest emission": 0,
                    "total emission": 0
                },
                "transport": {
                    "highest item": "",
                    "highest emission": 0,
                    "total emission": 0
                },
                "shopping": {
                    "highest item": "",
                    "highest emission": 0,
                    "total emission": 0
                }
        }
    }
        
    # if have, check permission
    if len(rep_data) != 0 and current_user.username == rep_data[0]["username"]:
        req_response["categories"] = rep_data[0]["categories"]
        return req_response
    elif len(rep_data) == 0 or current_user.username != rep_data[0]["username"]:
        # permission denied
        return {
            "status": "invalid, permission denied"
        }
    else:
        return {
            "status": "invalid, can't find report"
        }

# Get list of reports generated by username in the past month
@app.route("/calculator/api/v2/report/username/<username>")
@login_required
def get_calculate_report_id_by_username_v2(username):
    rep_ids = []

    # look through each cluster for recent
    for i in range(1,5):
        rep_data = list(reports_db[f"week-{i}"].find({
            "username": username    
        }).sort("report id", -1))

        if len(rep_data) == 0:
            rep_ids.append(f"{i}-0")
        else:
            rep_ids.append(f'{i}-{rep_data[0]["report id"]}')

    # week-id, -0 means not found

    # check if actual user
    if current_user.username != username:
        return {
            "ids": ["1-0","2-0","3-0","4-0"]
        }
    else:
        return {
            "ids": rep_ids
        }




# insecure version

# API9:2023 - Improper Inventory Management
# Problem: No documentation

"""
sample data
{
    "categories": {
        "food": {
            "highest item":"chichen rice",
            "highest emission":25,
            "total emission":25
        },
        "transport": {
            "highest item":"travel from jurong to nyp",
            "highest emission":10,
            "total emission":10
        },
        "shopping": {
            "highest item":"buy shoe",
            "highest emission":200,
            "total emission":200
        }
    }
}
"""


# API4:2023 - Unrestricted Resource Consumption
# Problem: no limits
@app.route("/calculator/api/v1/submit", methods=['POST'])
@login_required
def post_calculate_submit_v1():
    if app.debug:
        activities = request.get_json()
        print(activities)

        next_id = reports_db[f"week-{weeks_since_epoch()}"].count_documents({})+1

        summary = {
            "report id": next_id,
            "username":current_user.username,
            "data submitted":datetime.datetime.today().isoformat(),
            "claimed": 0,
            "categories":{
                "food": {
                    "highest item":"",
                    "highest emission":0,
                    "total emission":0
                },
                "transport": {
                    "highest item":"",
                    "highest emission":0,
                    "total emission":0
                },
                "shopping": {
                    "highest item":"",
                    "highest emission":0,
                    "total emission":0
                }
            }
        }


        # server side calculations
        """  
        for activity in activities:
            print(activity)
            if activity["category"] not in ["food","transport","shopping"]:
                continue
            
            # insecure miscongiuration
            # don't validate, so it crash and in debug mode

            # add to total for category
            summary["categories"][activity["category"]]["total emission"] += activity["emission"]

            # check if is highest, then update if needed
            if summary["categories"][activity["category"]]["highest emission"] < activity["emission"]:
                summary["categories"][activity["category"]]["highest emission"] = activity["emission"]
                summary["categories"][activity["category"]]["highest item"] = activity["item"]
         """
        # total emission

        # store data
        print(weeks_since_epoch())
        print(summary)

        # should i use the sql database? hmmmm
        # oh i can use mongo

        # sample data
        # 4 clusters, 1 for a week
        # each cluster have records which are the week's reports

        # working code
        # create the report
        reports_db[f"week-{weeks_since_epoch()}"].insert_one(summary)

        # do a update vulnerable to query injection
        # fill up with potentially dangerious use input

        # working code
        reports_db[f"week-{weeks_since_epoch()}"].update_one({
            "report id":next_id
        },{
            "$set":activities
        })

        # experimenting
        """         reports_db[f"week-{weeks_since_epoch()}"].update_one({"report id":next_id},{"$set":{"activities":activities["activities"]}}) """

        return {
            "status code": 0,
            "report_id": next_id,
            "comment": "Successfully processed your emission activities!"
        }
    
# API1:2023 - Broken Object Level Authorization
# Problem: doesn't check if user owns the report
@app.route("/calculator/api/v1/report/id/<id>")
@login_required
def get_calculate_report_by_id_v1(id):
    if app.debug:

        week, seq = id.split("-")
        print(week, seq)

        # try to locate data
        # working code
        """         
        print(reports_db[f"week-{week}"].count_documents({}))
        rep_data = list(reports_db[f"week-{week}"].find({
            "report id": int(seq)    
        }))
         """

        # experiment
        # where selector not supported

        """
        rep_data = list(reports_db[f"week-{week}"].find({ "$where":  "this['report id'] == '"+id+"' && this.username == '"+current_user.username+"'" }))
        """

        # testing injection attack
        # example payload
        # 4-1,"username":"target"
        query = json.loads('{"username":"'+current_user.username+'","report id":'+seq+'}')
        rep_data = list(reports_db[f"week-{week}"].find(query))



        # if have, read data
        print(rep_data)

        # return data
        req_response = {
                "categories": {
                    "food": {
                        "highest item": "",
                        "highest emission": 0,
                        "total emission": 0
                    },
                    "transport": {
                        "highest item": "",
                        "highest emission": 0,
                        "total emission": 0
                    },
                    "shopping": {
                        "highest item": "",
                        "highest emission": 0,
                        "total emission": 0
                    }
                }
        }
        if len(rep_data) != 0:
            req_response["categories"] = rep_data[0]["categories"]
            return req_response
        else:
            return {
                "status": "invalid or access denied!"
            }

# Get list of reports generated by username in the past month by week
@app.route("/calculator/api/v1/report/username/<username>")
@login_required
def get_calculate_report_id_by_username_v1(username):
    if app.debug:
        rep_ids = []

        # look through each cluster for recent
        for i in range(1,5):
            query = json.loads('{"username":"'+username+'"}')

            rep_data = list(reports_db[f"week-{i}"].find(query).sort("report id", -1))

            if len(rep_data) == 0:
                rep_ids.append(f"{i}-0")
            else:
                rep_ids.append(f'{i}-{rep_data[0]["report id"]}')

        # week-id, -0 means not found
        return rep_ids


# "backdoor" to overwrite past reports for demo
# wait i don't need a backdoor, i can just make v1 vulnerable to deserialzation!

# useful function
def weeks_since_epoch(date=datetime.datetime.today()):
  epoch = datetime.datetime.utcfromtimestamp(0)
  delta = date - epoch
  weeks = delta.days // 7
  return (weeks%4)+1

# summary list of issues done by jun hao
# - insecure config
# - improper inventory management
# - unsafe consumption of resources
# - broken object level authorisation
