import json


def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))
    print("get model response lambda")

    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': 'You have to input you name in the box where it says NAME'
    }

    return response
