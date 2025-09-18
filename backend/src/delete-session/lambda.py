import os
import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

def handler(event, context):
    session_id = event.get("session_id")
    if not session_id:
        return {"error": "Missing session_id"}

    table_name = (
        os.environ.get("FORMSESSION_TABLE_NAME")
    )
    if not table_name:
        return {"error": "Table name not configured"}

    try:
        ddb = boto3.resource("dynamodb")
        table = ddb.Table(table_name)

        deleted_count = 0
        last_evaluated_key = None
        while True:
            if last_evaluated_key:
                response = table.query(
                    KeyConditionExpression=Key("session_id").eq(session_id),
                    ExclusiveStartKey=last_evaluated_key,
                )
            else:
                response = table.query(
                    KeyConditionExpression=Key("session_id").eq(session_id)
                )
            items = response.get("Items", [])

            with table.batch_writer() as batch:
                for item in items:
                    key = {
                        "session_id": session_id,
                        "step": item["step"]
                    }
                    batch.delete_item(Key=key)
                    deleted_count += 1

            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

        return {"deleted": deleted_count, "session_id": session_id}
    except ClientError as e:
        return {"error": e.response['Error'].get('Message', str(e))}
    except Exception as e:
        return {"error": str(e)}
