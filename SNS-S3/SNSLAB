# SNS Lab

This hands-on lab guides you through setting up an automated notification system: when a file is uploaded to an Amazon S3 bucket, an Amazon SNS topic fires an email alert to a subscriber.

---
## 1. IAM Groups & Required Permissions

### Minimum Required Permissions

* **S3 Users:** `s3:PutObject`, `s3:GetObject`, `s3:ListBucket`, `s3:GetBucketNotification`, `s3:PutBucketNotification`.
* **SNS Users:** `sns:CreateTopic`, `sns:Subscribe`, `sns:Publish`, `sns:SetTopicAttributes`, `sns:GetTopicAttributes`.
* **S3 Service Principal (Resource-Based Policy):** S3 itself requires `sns:Publish` access targeting the specific SNS topic resource.

### Step-by-Step IAM Group Setup

1. Open the **IAM Console** and navigate to **User groups** > **Create group**.
2. **Create `S3_USER_GROUP**`:
* Group Name: `S3_USER_GROUP`
* Under **Attach permissions policies**, search for and select `AmazonS3FullAccess` (or attach an inline policy restricting actions to `s3:PutObject` and `s3:GetBucketNotification`).
* Click **Create Group**.


3. **Create `SNS_USER_GROUP**`:
* Group Name: `SNS_USER_GROUP`
* Under **Attach permissions policies**, search for and select `AmazonSNSFullAccess`.
* Click **Create Group**.


4. Add your working IAM user to both groups so you have the necessary administrative access for the rest of the lab.

---

## 2. Configure SNS Topic & Access Policy

*Note: S3 requires the SNS topic and subscription to exist before configuring bucket event notifications.*

1. Open the **Amazon SNS Console** and select **Topics** > **Create topic**.
2. Select **Standard** as the topic type.
3. Enter `s3-file-upload-topic` as the **Name**.
4. Expand **Access policy** and update the JSON structure so S3 has permission to publish to this topic:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "SNS:Publish",
      "Resource": "arn:aws:sns:YOUR-REGION:YOUR-ACCOUNT-ID:s3-file-upload-topic",
      "Condition": {
        "ArnLike": {
          "aws:SourceArn": "arn:aws:s3:::YOUR-BUCKET-NAME"
        }
      }
    }
  ]
}

```

*(Replace `YOUR-REGION`, `YOUR-ACCOUNT-ID`, and `YOUR-BUCKET-NAME` with your actual AWS values.)*

5. Click **Create topic**. Copy the generated **Topic ARN**.
6. Under the **Subscriptions** tab of your new topic, click **Create subscription**:
* **Protocol:** Email
* **Endpoint:** Enter your email address.
* Click **Create subscription**.

7. Check your email inbox and click **Confirm subscription** inside the confirmation email sent by AWS.

__NOTE:__ If the email address entered was incorrect you cannot remove the subscription. If there is no response to the email, AWS will delete it after 72 hours.

---

## 3. Set Up S3 Bucket & Event Notifications

1. Open the **Amazon S3 Console** and click **Create bucket**.
2. Enter a globally unique **Bucket name** (e.g., `lab-upload-notifier-12345`) and select your region.
3. Keep default settings (Block Public Access enabled, KMS or Amazon S3 encryption enabled) and click **Create bucket**.
4. Select your newly created bucket from the list and open the **Properties** tab.
5. Scroll down to **Event notifications** and click **Create event notification**.
6. Configure the event settings:
* **Event name:** `s3-upload-notification`
* **Event types:** Under *Object creation*, check **All object create events** (`s3:ObjectCreated:*`).
* **Destination:** Scroll to the bottom and select **SNS topic**.
* **Specify SNS topic:** Choose **Select from your SNS topics** and pick `s3-file-upload-topic` (or paste the Topic ARN).


7. Click **Save changes**.

---

## Verification & Testing

1. Go to your S3 bucket's **Objects** tab and click **Upload**.
2. Select any sample file from your computer and complete the upload.
3. Check your email inbox. Within a few seconds, you will receive an SNS email containing a JSON payload detailing the bucket name, uploaded object key, and file size.

Adding a cleanup section ensures you do not incur unnecessary charges or leave stray resources in your AWS environment.

---

## 4. Lab Cleanup Instructions

Follow these steps in exact order to delete all resources created during this lab.

### Step 1: Empty and Delete the S3 Bucket

1. Open the **Amazon S3 Console**.
2. Select the bucket you created (`s3-file-upload-topic` or your unique bucket name).
3. Click **Empty** at the top of the list, type `permanently delete` in the confirmation box, and click **Empty**.
4. Once the bucket is empty, return to the **Buckets** list.
5. Select your bucket again, click **Delete**, type the name of the bucket to confirm, and click **Delete bucket**.

### Step 2: Delete the SNS Topic and Subscriptions

1. Open the **Amazon SNS Console** and click **Topics** from the left navigation menu.
2. Select `s3-file-upload-topic` and click **Delete**.
3. Type `delete me` (or the requested confirmation phrase) and click **Delete**.
4. Select **Subscriptions** from the left menu.
5. Locate any subscriptions tied to your email address, select them, and click **Delete** > **Delete**.

### Step 3: Remove IAM User Groups

1. Open the **IAM Console** and select **User groups**.
2. Select `S3_USER_GROUP` and `SNS_USER_GROUP`.
3. Click **Delete** and confirm removal.