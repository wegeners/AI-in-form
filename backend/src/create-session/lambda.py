import json
import os
import boto3

def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    print("this is the event")
    print(json.dumps(event))

    table_name = os.environ['FORMSESSION_TABLE_NAME']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    session_id = event["sessionId"]
    #image = event['image']
    user_question = event["userQuestion"]

    table.put_item(
        Item={
            'sessionId': session_id,
            'step': 0,
            #'image': image,
            'value': user_question
        }
    )

    return event
