# Autoscaling Lab Budget

Here is the step-by-step console guide to setting up cost tracking, budget alerts, and real-time expenditure monitoring for your Auto Scaling Group lab using the AWS Management Console.

---

## Phase 1: Set Up a Cost Guardrail in AWS Budgets

Setting up a budget alert in the console ensures AWS emails you if your spending approaches or exceeds a set threshold (e.g., $1.00).

---

### Step 1: Create a $1.00 Monthly Cost Budget

1. In the top search bar of the AWS Management Console, type **Billing and Cost Management** and select it.
2. In the left navigation pane under **Cost Management**, click **Budgets**.
3. Click **Create budget**:
* **Budget setup:** Choose **Use a template (simplified)**.
* **Templates:** Select **Zero spend budget** (if you want alerts on any charge above $0) OR select **Custom budget** to set a specific limit.


4. If choosing **Custom budget**:
* Select **Cost budget - Recommended** and click **Next**.
* **Budget name:** `ASG-Lab-Cost-Guardrail`
* **Period:** Select **Monthly**.
* **Budget effective dates:** Recurring budget.
* **Budgeted amount:** Enter `1.00` (USD).
* Click **Next**.



### Step 2: Configure Email Alerts

1. Click **Add alert threshold**:
* **Threshold:** Enter `80` (% of budgeted amount = $0.80).
* **Trigger:** Actual cost.
* **Notification recipients:** Enter your email address.


2. Click **Next**, review the configuration, and click **Create budget**.

---

## Phase 2: Estimate Cost Pre-Deployment Using AWS Pricing Calculator

You can use the official web-based calculator to model the lab costs before spinning up resources.

1. Open a browser tab to [calculator.aws](https://www.google.com/search?q=https://calculator.aws/%23/).
2. Click **Create estimate**.
3. Search for **Amazon EC2** and click **Configure**:
* **Description:** `ASG Lab Instances`
* **Region:** Select your target region (e.g., *US East (N. Virginia)*).
* **EC2 instance specifications:**
* Operating System: **Linux**
* Quantity: **1** (Baseline instance)
* Instance Type: Select **t3.micro**


* **Payment options:** Select **On-Demand**.
* **EBS Storage:** Choose **General Purpose SSD (gp3)** and set volume size to **8 GB**.


4. Click **Save and add service**.
5. The summary page will display the hourly and monthly baseline cost (~$0.27/day for 1 instance).

---

## Phase 3: Track Real-Time Spending in AWS Cost Explorer

After your Auto Scaling Group lab runs for a few hours, cost data flows into AWS Cost Explorer for detailed analysis.

1. In the AWS Management Console, navigate back to **Billing and Cost Management**.
2. In the left navigation pane under **Cost Management**, click **Cost Explorer**.
3. If this is your first time opening Cost Explorer, click **Enable Cost Explorer** *(Note: It can take up to 24 hours for historical data to populate if previously disabled)*.
4. Once enabled:
* Set **Granularity** to **Daily** or **Hourly**.
* Under **Dimension** on the right panel, select **Service**.
* Look for **Amazon Elastic Compute Cloud - Compute** to inspect the exact charges accrued by your `t3.micro` instances.



---

## Phase 4: Cleaning Up the Budget

Once you finish testing and teardown of the ASG lab, remove the budget guardrail to avoid unnecessary alert emails:

1. Go to **Billing and Cost Management > Budgets**.
2. Select **ASG-Lab-Cost-Guardrail**.
3. Click **Delete** and confirm.