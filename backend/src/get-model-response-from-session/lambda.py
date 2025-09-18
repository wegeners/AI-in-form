import json
def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))
    print("get model response from session lambda")

    return {}
