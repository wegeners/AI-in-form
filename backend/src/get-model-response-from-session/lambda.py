import json
import os
import boto3
from boto3.dynamodb.conditions import Key


def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))

    session_id = event.get('queryStringParameters', {}).get('sessionId')
    table_name = os.environ.get('FORMSESSION_TABLE_NAME')

    if not session_id:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'sessionId is required'})
        }

    if not table_name:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Table name not configured'})
        }

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        response = table.query(
            KeyConditionExpression=Key('sessionId').eq(session_id)
        )

        items = response.get('Items', [])

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(items)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Could not retrieve items from DynamoDB'})
        }
