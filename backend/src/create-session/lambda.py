import json
import os
import boto3

def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))

    table_name = os.environ['FORMSESSION_TABLE_NAME']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    session_id = event['sessionId']
    image = event['image']

    table.put_item(
        Item={
            'sessionId': session_id,
            'step': 0,
            'image': image,
        }
    )

    return event