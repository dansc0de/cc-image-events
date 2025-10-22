# Local Development Guide

This guide will help you set up and test your Lambda functions locally before deploying to AWS.

## Prerequisites

- Python 3.13 installed
- Docker Desktop installed
- uv package manager installed
- AWS CLI installed and configured

## Installing uv

If you don't have uv installed, install it using:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Windows users:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Setting Up Your Development Environment

### 1. Navigate to a Lambda Function Directory

```bash
cd lambdas/resize  # or greyscale, or exif
```

### 2. Add Dependencies to pyproject.toml

Edit your `pyproject.toml` to include the dependencies you need. For example:

```toml
[project]
name = "resize-lambda"
version = "0.1.0"
description = "Lambda function to resize images"
requires-python = ">=3.13"
dependencies = [
    "pillow>=10.0.0",
    "boto3>=1.28.0"
]
```

### 3. Create a Virtual Environment and Install Dependencies

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### 4. Implement Your Lambda Handler

Edit `handler.py` to implement your image processing logic. The handler should:
- Parse the SNS event to get S3 bucket and object key
- Download the image from S3
- Process the image (resize/greyscale/extract EXIF)
- Upload the result to the processed folder

## Local Testing

### Method 1: Test with Mock Events (Quick Testing)

Create a test event file `test-event.json`:

```json
{
  "Records": [
    {
      "EventSource": "aws:sns",
      "EventVersion": "1.0",
      "EventSubscriptionArn": "arn:aws:sns:us-east-1:123456789012:image-processing-topic:12345678-1234-1234-1234-123456789012",
      "Sns": {
        "Type": "Notification",
        "MessageId": "12345678-1234-1234-1234-123456789012",
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:image-processing-topic",
        "Subject": "Amazon S3 Notification",
        "Message": "{\"Records\":[{\"eventVersion\":\"2.1\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2024-01-01T12:00:00.000Z\",\"eventName\":\"ObjectCreated:Put\",\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"test-config\",\"bucket\":{\"name\":\"your-bucket-name\",\"arn\":\"arn:aws:s3:::your-bucket-name\"},\"object\":{\"key\":\"resize/test-image.jpg\",\"size\":1024}}}]}",
        "Timestamp": "2024-01-01T12:00:00.000Z"
      }
    }
  ]
}
```

Create a simple test script `test_local.py`:

```python
import json
from handler import resize_handler  # Change based on your function

# Load test event
with open('test-event.json', 'r') as f:
    event = json.load(f)

# Mock context
class Context:
    function_name = "test-function"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    aws_request_id = "test-request-id"

# Test the handler
result = resize_handler(event, Context())
print(json.dumps(result, indent=2))
```

Run the test:

```bash
python test_local.py
```

### Method 2: Test with Docker (Most Realistic)

Build and test your Lambda container locally to ensure it works exactly as it will in AWS:

```bash
# Build the Docker image
docker build -t resize-lambda:test .

# Run the container
docker run -p 9000:8080 resize-lambda:test

# In another terminal, invoke the function with a test event
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d @test-event.json
```

This method is closest to how your Lambda will run in production since it uses the actual Docker container.

## Debugging Tips

### Enable Verbose Logging

Add print statements throughout your code to understand what's happening:

```python
def resize_handler(event, context):
    print("Lambda function started")
    print(f"Event received: {json.dumps(event)}")

    # Your processing code here
    print("Starting image processing...")
    print("Image processing complete")

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
```

### Use Python Debugger

Add breakpoints in your code:

```python
import pdb

def resize_handler(event, context):
    pdb.set_trace()  # Debugger will stop here
    # Your code
```

### Check Event Structure

Always print the event first to understand its structure:

```python
def resize_handler(event, context):
    print("Full event:")
    print(json.dumps(event, indent=2, default=str))
```

## Common Issues

### Import Errors

If you get import errors, make sure your virtual environment is activated and dependencies are installed:

```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e .
```

### AWS Credentials

For local testing with actual S3 buckets, ensure your AWS credentials are configured:

```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Docker Build Failures

If Docker build fails:
1. Check that `pyproject.toml` is valid
2. Ensure `uv.lock` file exists (run `uv lock` to generate it)
3. Verify Docker is running

## Best Practices

1. **Test with small images first** - Use small test images (< 1MB) to speed up development
2. **Handle errors gracefully** - Always include try/except blocks
3. **Log everything** - Use print statements liberally (they become CloudWatch logs in production)
4. **Test edge cases** - Try different image formats (JPG, PNG, WEBP), sizes, and corrupted files
5. **Clean up resources** - Close file handles and clean up temporary files
6. **Use environment variables** - Don't hardcode bucket names or other configuration values
7. **Test the Docker image locally** - Always test with Docker before pushing to ensure it works in Lambda

## Development Workflow

Recommended workflow for developing your Lambda functions:

1. **Write code** - Implement your handler logic
2. **Test locally with Python** - Quick iteration using `test_local.py`
3. **Test with Docker** - Verify container works correctly
4. **Commit and push** - GitHub Actions will deploy to ECR
5. **Test in AWS** - Upload a file to S3 and check CloudWatch Logs
6. **Iterate** - Fix issues and repeat

## Next Steps

Once your function works locally:
1. Ensure all dependencies are listed in `pyproject.toml`
2. Run `uv lock` to generate/update the lock file
3. Commit your changes to git
4. Push to GitHub to trigger the deployment workflow
5. Monitor CloudWatch Logs for the deployed function
6. Test with actual S3 uploads

## Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [Python Pillow Documentation](https://pillow.readthedocs.io/)
- [AWS Lambda Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [Docker Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
