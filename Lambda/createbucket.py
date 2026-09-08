import boto3

def lambda_handler(event, context):
    # Create an S3 client using the IAM role
    s3_client = boto3.client('s3', region_name='YOUR_REGION')
    # Define the bucket name
    bucket_name = 'YOUR-UNIQUE-BUCKET-NAME'
    # Create the bucket
    try:
        response = s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created successfully.")
    except Exception as e:
        print(f"Error creating bucket {bucket_name}: {e}")
    # Return a success response
    return {
        'statusCode': 200,
        'body': 'Bucket created successfully.'
    }
