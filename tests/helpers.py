import re
import requests
import time


def clear_typer_output(output):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    # delete ansi chars
    result = ansi_escape.sub('', output)
    # delete new line chars
    result_final = result.replace('\n', ' ')
    return result_final


CONTEXT_DATA = """contexts:
- auth:
    client_id: olympus-client1
    service_account_id: null
    url: https://...
    username: testuser
  name: olympus-api-1-uat
  project_prefix: test-OLA
  url: https://dev-olympusapi1.genomics.roche.com/v1
current-context: olympus-api-1-uat
last-modification: '2023-01-31T13:06:02.259398'"""


def find_job_url_in_string(string):
    string = string.replace('\n', '')
    url = re.search("(?P<url>https?://[^\s]+)", string).group("url")
    # check last character, if it not alnum remove it
    while not url[-1].isalnum():
        url = url[:-1]
    return url


def find_job_id_in_string(string):
    string = string.replace('\n', '')
    start = "job_id: "
    end = "job_url"
    job_id = string[string.find(start) + len(start):string.rfind(end)].strip()
    return job_id


def wait_for_job_status(job_url, status="SUCCESS"):
    # wait for job status (max 30 seconds)
    timeout = time.time() + 30
    output = ''
    while output != status:
        if time.time() > timeout:
            print("Job did not end with given status")
            break
        response = requests.get(job_url)
        assert response.status_code == 200
        output = response.json()["status"]
        # wait 0.5 second to not hit API too much
        time.sleep(0.5)