import json

def exif_handler(event, context):
    """
    EXIF Lambda - TODO: Implement EXIF data extraction logic
    """
    print("EXIF Lambda triggered")
    print("Event received:")
    print(json.dumps(event, indent=2))

    return {
        'statusCode': 200,
        'body': json.dumps('EXIF Lambda executed successfully')
    }
