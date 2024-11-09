import requests
import time

from app import app


REQUEST_HEADERS = {
        "accept": "application/json",
        "x-apikey": app.config['VIRUS_TOTAL_KEY']
        }


def get_analysis_information(file_id, iteration_number=0):
    if iteration_number > 30:
        return None

    url = f"https://www.virustotal.com/api/v3/analyses/{file_id}"
    response = requests.get(url, headers=REQUEST_HEADERS)
    response_json = response.json()
    if "error" not in response_json and response_json["data"]["attributes"]["status"] == "completed":
        response_useful_json = response_json["data"]["attributes"]
        return response_useful_json
    else:
        time.sleep(0.7)
        return get_analysis_information(file_id, iteration_number + 1)


def is_file_dangerous(file_bytes, mime_type, filename="some_filename"):
    url = "https://www.virustotal.com/api/v3/files"
    files = {"file": (filename, file_bytes, mime_type)}
    response = requests.post(url, files=files, headers=REQUEST_HEADERS)
    response_json = response.json()
    file_id = response_json["data"]["id"]

    is_dangerous = True
    analysis = get_analysis_information(file_id)
    if not analysis:
        return is_dangerous

    if analysis['stats']['malicious'] + analysis['stats']['suspicious'] > 5:
        return is_dangerous
    else:
        is_dangerous = False
        return is_dangerous
