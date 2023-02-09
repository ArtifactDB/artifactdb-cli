import re


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
  url: https://...
current-context: olympus-api-1-uat
last-modification: '2023-01-31T13:06:02.259398'"""
