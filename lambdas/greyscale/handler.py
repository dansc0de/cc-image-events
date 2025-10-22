import json

def greyscale_handler(event, context):
    """
    Greyscale Lambda - TODO: Implement greyscale conversion logic
    """
    print("Greyscale Lambda triggered")
    print("Event received:")
    print(json.dumps(event, indent=2))

    return {
        'statusCode': 200,
        'body': json.dumps('Greyscale Lambda executed successfully')
    }
