import json
import sys

# import random
import requests


def slack_bot(CPUUtil, RAMUtil):
    url = "https://hooks.slack.com/services/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"
    message = "CPU Usage: " + CPUUtil + "%" + "\n Memory Usage: " + RAMUtil + "%"
    title = f"Server Status Test"
    slack_data = {
        "attachments": [
            {
                "color": "#9733EE",
                "fields": [
                    {
                        "title": title,
                        "value": message,
                        "short": "false",
                    }
                ],
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {"Content-Type": "application/json", "Content-Length": byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)


if __name__ == "__main__":
    slack_bot()
