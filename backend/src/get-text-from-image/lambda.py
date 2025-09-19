import os
from pathlib import Path
import requests
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone

STEP_ATTRIBUTE_NAME = "step"  


def handler(event, context):
    # Validate event
    if not isinstance(event, dict):
        err = "2001 Input is not a dict"
        write_to_table(None, None, err)
        return {"error": err}

    session_id = event["Payload"]["sessionId"]
    if not session_id:
        err = "2002 session id is missing."
        write_to_table(None, None, err)
        return {"error": err}

    file_path = session_id + "-image.jpg"

    # API config
    api_key = os.environ.get("OCR_SPACE_API_KEY")
    bucket = os.environ.get("AIINFORMIMAGEBUCKET_BUCKET_NAME")

    if not api_key:
        err = "2005 Missing OCR_SPACE_API_KEY"
        write_to_table(None, session_id, err)
        return {"error": err}

    language = event.get("language") or os.environ.get("OCR_LANGUAGE") or "ger"

    payload = {
        "apikey": api_key,
        "language": language,
        "isOverlayRequired": "false",
    }


    s3 = boto3.client("s3")

    # Download to /tmp (Lambda’s writable dir)
    local_path = "/tmp/myfile.jpg"
    s3.download_file(bucket, file_path, local_path)


    # Call OCR.space
    try:
        with open(local_path, "rb") as f:
            files = {"filename": ("myfile.jpg", f)}
            resp = requests.post(
                "https://api.ocr.space/parse/image",
                files=files,
                data=payload,
                timeout=60,
            )
    except Exception as e:
        err = f"2006 Request_or_Read_Failed: {e}"
        write_to_table(None, session_id, "") # use empty string here so the next step can continue
        return {"error": err}
    # remove file from path
    #os.remove(file_path)
    s3.delete_object(Bucket=bucket, Key=file_path)

    # HTTP / JSON handling
    try:
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        err = f"2007 HTTP_or_JSON_Error: {e}"
        write_to_table(None, session_id, err)
        return {"error": err}

    if data.get("IsErroredOnProcessing"):
        err = "2008 OCR_provider_error"
        write_to_table(None, session_id, err)
        return {"error": err}


    try:
        results = data.get("ParsedResults", [])
        texts = []
        confidences = []
        for item in results:
            if not isinstance(item, dict):
                continue
            t = item.get("ParsedText", "")
            if t:
                texts.append(t)
            conf = item.get("MeanConfidenceLevel")
            if conf is not None:
                confidences.append(conf)
        text = "\n".join(texts).strip()
        mean_confidence = sum(confidences) / len(confidences) if confidences else None
    except Exception:
        err = "2009 Unexpected_OCR_response_format"
        write_to_table(None, session_id, err)
        return {"error": err}

    # On success, write value=text, fin=False
    write_to_table(text, session_id, None)

    return {"text": text}

def write_to_table(text, session_id, error):
    if not session_id:
        return  

    table_name = (
        os.environ.get("FORMSESSION_TABLE_NAME")
    )
    if not table_name:
        return  

    try:
        ddb = boto3.resource("dynamodb")
        table = ddb.Table(table_name)
        item = {
            "sessionId": session_id,
            STEP_ATTRIBUTE_NAME: 1,
            "value": (error if error else (text or "")),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "completed": bool(error),
        }
        table.put_item(Item=item)
    except ClientError as e:
        print(f"DynamoDB ClientError: {e.response['Error'].get('Message')}")
    except Exception as e:
        print(f"DynamoDB unexpected error: {e}")
