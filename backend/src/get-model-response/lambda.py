import json
import os
import requests
import boto3
from datetime import datetime

def get_openrouter_response(messages):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "messages": messages,
        },
    )
    response.raise_for_status()
    return response.json()


def handler(event, context):


    # Log the event argument for debugging and for use in local development.
    print(event)

    try:
        body = event.get("body", "{}")
        sessionID = body.get("sessionID")
        messages = body.get("ocrValue", [])
        userQuestion = body.get("userQuestion")



        if not userQuestion:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'userQuestion' in request body"}),
            }

        messages.append({"role": "user", "content": userQuestion})

        api_response = get_openrouter_response(messages)

        table_name = os.environ.get("FORMSESSION_TABLE_NAME")
        if not table_name:
            raise ValueError("FORMSESSION_TABLE_NAME environment variable not set")

        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(table_name)

        table.put_item(
            Item={
                "sessionId": sessionID,
                "step": 3,
                "value": api_response,
                "timestamp": datetime.utcnow().isoformat(),
                "completed": True,
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps(api_response),
            "headers": {
                "Content-Type": "application/json",
            },
        }

    except requests.exceptions.RequestException as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"API request failed: {e}"}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"An unexpected error occurred: {e}"}),
        }



