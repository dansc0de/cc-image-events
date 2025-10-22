# Event-Driven Image Processing - Lambda Architecture Project

# ![Pitt Panthers](https://upload.wikimedia.org/wikipedia/commons/4/44/Pitt_Panthers_wordmark.svg)
## Introduction to Cloud Computing - University of Pittsburgh

## Project Overview

This project demonstrates event-driven architecture using AWS services. You will build a serverless image processing pipeline that automatically processes images uploaded to S3 using AWS Lambda functions triggered via SNS topics.

## Architecture

```
S3 Bucket Upload (with prefix routing)
    └─> SNS Topic
        ├─> /resize/* → Resize Lambda → /processed/resize/
        ├─> /greyscale/* → Greyscale Lambda → /processed/greyscale/
        └─> /exif/* → EXIF Lambda → /processed/exif/
```

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy-lambda.yml    # GitHub Actions workflow for ECR deployment
├── lambdas/
│   ├── resize/
│   │   ├── Dockerfile
│   │   ├── handler.py
│   │   └── pyproject.toml
│   ├── greyscale/
│   │   ├── Dockerfile
│   │   ├── handler.py
│   │   └── pyproject.toml
│   └── exif/
│       ├── Dockerfile
│       ├── handler.py
│       └── pyproject.toml
└── README.md
```

## Prerequisites

- AWS Account
- GitHub Account
- Basic knowledge of Python 3.13
- Understanding of Docker containers
- AWS CLI installed and configured (for local testing)

## Documentation

- [Local Development Guide](./local-dev.md) - Learn how to develop and test your Lambda functions locally

## Setup Instructions

### 1. AWS Infrastructure Setup

#### Create ECR Repositories

Create three ECR repositories for your Lambda functions:

```bash
aws ecr create-repository --repository-name resize-lambda --region us-east-1
aws ecr create-repository --repository-name greyscale-lambda --region us-east-1
aws ecr create-repository --repository-name exif-lambda --region us-east-1
```

#### Create S3 Bucket

```bash
aws s3 mb s3://<your-pitt-username>
```

Create the required folders:

```bash
aws s3api put-object --bucket dpm79-assignment3 --key resize/
aws s3api put-object --bucket dpm79-assignment3 --key greyscale/
aws s3api put-object --bucket dpm79-assignment3 --key exif/
aws s3api put-object --bucket dpm79-assignment3 --key processed/resize/
aws s3api put-object --bucket dpm79-assignment3 --key processed/greyscale/
aws s3api put-object --bucket dpm79-assignment3 --key processed/exif/
```

#### Create SNS Topic

```bash
aws sns create-topic --name image-processing-topic --region us-east-1
```

#### Configure S3 Event Notifications

Add S3 event notification to trigger SNS when objects are uploaded:

```bash
aws s3api put-bucket-notification-configuration \
  --bucket your-image-processing-bucket-<your-pitt-username> \
  --notification-configuration file://s3-notification-config.json
```

Create `s3-notification-config.json`:

```json
{
  "TopicConfigurations": [
    {
      "TopicArn": "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:image-processing-topic",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "resize/"
            }
          ]
        }
      }
    },
    {
      "TopicArn": "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:image-processing-topic",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "greyscale/"
            }
          ]
        }
      }
    },
    {
      "TopicArn": "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:image-processing-topic",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "exif/"
            }
          ]
        }
      }
    }
  ]
}
```

#### Create Lambda Functions

Create three Lambda functions using container images:

```bash
aws lambda create-function \
  --function-name resize-lambda \
  --package-type Image \
  --code ImageUri=YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/resize-lambda:latest \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --region us-east-1

aws lambda create-function \
  --function-name greyscale-lambda \
  --package-type Image \
  --code ImageUri=YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/greyscale-lambda:latest \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --region us-east-1

aws lambda create-function \
  --function-name exif-lambda \
  --package-type Image \
  --code ImageUri=YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/exif-lambda:latest \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --region us-east-1
```

#### Subscribe Lambdas to SNS Topic

Create SNS filter policies to route messages based on S3 object prefix:

For resize-lambda:
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:image-processing-topic \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:resize-lambda \
  --attributes '{"FilterPolicy":"{\"key\":[{\"prefix\":\"resize/\"}]}"}'
```

Repeat for greyscale-lambda and exif-lambda with their respective prefixes.

Add Lambda permissions to allow SNS to invoke:

```bash
aws lambda add-permission \
  --function-name resize-lambda \
  --statement-id sns-invoke \
  --action lambda:InvokeFunction \
  --principal sns.amazonaws.com \
  --source-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:image-processing-topic
```

Repeat for other Lambda functions.

### 2. GitHub Actions Setup

#### Configure OIDC for GitHub Actions

1. Create an IAM OIDC identity provider for GitHub
2. Create an IAM role with trust policy for GitHub Actions
3. Attach policies for ECR and Lambda access

#### Add GitHub Secrets

Add the following secrets to your GitHub repository:

- `AWS_ROLE_ARN`: The ARN of the IAM role for GitHub Actions

Go to Settings > Secrets and variables > Actions > New repository secret

### 3. Local Development with uv

Install uv (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install dependencies for a Lambda function:

```bash
cd lambdas/resize
uv pip install -r pyproject.toml
```

### 4. Deploy Lambda Functions

Push your code to the `main` branch to trigger the GitHub Actions workflow:

```bash
git add .
git commit -m "Initial lambda implementation"
git push origin main
```

The workflow will:
1. Build Docker images for each Lambda function
2. Push images to ECR
3. Update Lambda functions with new images

## Implementation Tasks

### Task 1: Implement Resize Lambda

Edit `lambdas/resize/handler.py` to:
1. Parse the SNS event to extract S3 bucket and object key
2. Download the image from S3
3. Resize the image (choose appropriate dimensions)
4. Upload the processed image to `/processed/resize/`

Add required dependencies to `lambdas/resize/pyproject.toml` (e.g., Pillow for image processing)

### Task 2: Implement Greyscale Lambda

Edit `lambdas/greyscale/handler.py` to:
1. Parse the SNS event
2. Download the image
3. Convert to greyscale
4. Upload to `/processed/greyscale/`

### Task 3: Implement EXIF Lambda

Edit `lambdas/exif/handler.py` to:
1. Parse the SNS event
2. Download the image
3. Extract EXIF metadata
4. Save metadata as JSON to `/processed/exif/`

## Testing

Upload test images to your S3 bucket with the appropriate prefix:

```bash
# Test resize
aws s3 cp test-image.jpg s3://your-image-processing-bucket-<your-pitt-username>/resize/test-image.jpg

# Test greyscale
aws s3 cp test-image.jpg s3://your-image-processing-bucket-<your-pitt-username>/greyscale/test-image.jpg

# Test EXIF
aws s3 cp test-image.jpg s3://your-image-processing-bucket-<your-pitt-username>/exif/test-image.jpg
```

Check CloudWatch Logs for each Lambda function to verify execution.

## Grading Requirements

### Make S3 Bucket Public (for Grading Only)

**WARNING: Only do this for grading purposes. Never make production buckets public.**

Add bucket policy to make objects publicly readable:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-image-processing-bucket-<your-pitt-username>/*"
    }
  ]
}
```

Apply the policy:

```bash
aws s3api put-bucket-policy \
  --bucket your-image-processing-bucket-<your-pitt-username> \
  --policy file://bucket-policy.json
```

Disable "Block Public Access":

```bash
aws s3api put-public-access-block \
  --bucket your-image-processing-bucket-<your-pitt-username> \
  --public-access-block-configuration \
  "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```

## Submission

Submit the following:
1. GitHub repository URL with your implementation
2. S3 bucket name (public for grading)
3. AWS region used
4. Screenshots of:
   - CloudWatch logs showing Lambda executions
   - S3 bucket showing processed files
   - SNS topic subscriptions

## Troubleshooting

### Lambda Not Triggering

- Check CloudWatch Logs for SNS and Lambda
- Verify SNS topic has Lambda subscriptions
- Check Lambda permissions allow SNS invocation
- Verify S3 event notifications are configured correctly

### Docker Build Fails

- Ensure pyproject.toml is valid
- Check that all dependencies are compatible with Python 3.13
- Verify Dockerfile syntax

### GitHub Actions Fails

- Check AWS_ROLE_ARN secret is set correctly
- Verify IAM role has necessary permissions
- Check ECR repositories exist

## Resources

- [AWS Lambda with Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [AWS SNS Filtering](https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering.html)
- [GitHub Actions AWS Credentials](https://github.com/aws-actions/configure-aws-credentials)

## License

This project template is for educational purposes.
