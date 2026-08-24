Here is the updated **Elastic Load Balancing Lab** revised to incorporate **AWS Launch Templates** for standardizing instance deployment.

---

## Elastic Load Balancing (ELB) Lab with Launch Templates

This hands-on lab takes you through deploying an AWS Application Load Balancer (ALB) across two Amazon EC2 web instances in different Availability Zones (AZs), using a Launch Template to standardize instance configurations.

### Prerequisites

* An AWS Account with access to the AWS Management Console.
* The Default VPC active in your selected AWS Region.

---

### Step 1: Create a Security Group

You need a security group that allows incoming public web traffic.

1. Open the **Amazon EC2 Console**.
2. In the left navigation pane, choose **Security Groups** under **Network & Security**.
3. Click **Create security group**.
4. Configure the settings:
* **Security group name:** `web-server-sg`
* **Description:** `Allow HTTP traffic`
* **VPC:** Select your default VPC


5. Under **Inbound rules**, click **Add rule**:
* **Type:** HTTP (Port 80)
* **Source:** Anywhere-IPv4 (`0.0.0.0/0`)


6. Click **Create security group**.

---

### Step 2: Create a Launch Template

A launch template defines the hardware, AMI, and security configuration for your web servers.

1. In the EC2 Console, select **Launch Templates** under **Instances** in the left navigation pane.
2. Click **Create launch template**.
3. Configure the general details:
* **Launch template name:** `web-server-template`
* **Template version description:** `Initial base template for web servers`
* Check **Auto Scaling guidance** (optional, but good practice for reuse).


4. Configure **Application and OS Images (Amazon Machine Image)**:
* Select **Amazon Linux 2023 AMI**.


5. Configure **Instance type**:
* Select `t2.micro` (or `t3.micro` depending on region availability).


6. Configure **Key pair**:
* Select **Don't include in launch template**.


7. Under **Network settings**:
* **Firewall (security groups):** Select **Select existing security group** and choose `web-server-sg`.


8. Expand **Advanced details** at the bottom, scroll to **User data**, and paste the baseline script:
```bash
#!/bin/bash
dnf update -y
dnf install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from Web Server</h1>" > /var/www/html/index.html

```


9. Click **Create launch template**.

---

### Step 3: Launch Two EC2 Web Instances from the Template

Launch servers into distinct Availability Zones using your template.

#### Launch Instance 1:

1. In the left navigation, choose **Launch Templates**.
2. Select `web-server-template` and click **Actions** -> **Launch instance from template**.
3. Configure the instance:
* **Name:** `web-server-1`


4. Under **Network settings**:
* **Subnet:** Select the first available subnet (e.g., `us-east-1a`).


5. Expand **Advanced details**, scroll to **User data**, and replace the placeholder text with:
```bash
#!/bin/bash
dnf update -y
dnf install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from Web Server 1</h1>" > /var/www/html/index.html

```


6. Click **Launch instance**.

#### Launch Instance 2:

1. Return to **Launch Templates**, select `web-server-template`, and click **Actions** -> **Launch instance from template**.
2. Configure the instance:
* **Name:** `web-server-2`


3. Under **Network settings**:
* **Subnet:** Select a **different** subnet/AZ from Instance 1 (e.g., `us-east-1b`).


4. Expand **Advanced details**, scroll to **User data**, and update the script response to:
```bash
#!/bin/bash
dnf update -y
dnf install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from Web Server 2</h1>" > /var/www/html/index.html

```


5. Click **Launch instance**.

---

### Step 4: Create a Target Group

1. In the left navigation, under **Load Balancing**, click **Target Groups**.
2. Click **Create target group**.
3. Select target type: **Instances**.
4. Configure target group settings:
* **Target group name:** `web-alb-tg`
* **Protocol:** HTTP (Port 80)
* **VPC:** Select your default VPC


5. Click **Next**.
6. Under **Register targets**:
* Select both `web-server-1` and `web-server-2`.
* Click **Include as pending below**.


7. Click **Create target group**.

---

### Step 5: Deploy the Application Load Balancer

1. In the left navigation, under **Load Balancing**, click **Load Balancers**.
2. Click **Create load balancer**.
3. Under **Application Load Balancer**, click **Create**.
4. Complete the configuration:
* **Load balancer name:** `web-alb`
* **Scheme:** Internet-facing
* **IP address type:** IPv4


5. Under **Network mapping**:
* **VPC:** Select your default VPC.
* **Mappings:** Select at least two Availability Zones and their corresponding subnets where your instances reside.


6. Under **Security groups**:
* Remove the default security group.
* Select `web-server-sg`.


7. Under **Listeners and routing**:
* **Protocol:** HTTP (Port 80)
* **Default action:** Forward to `web-alb-tg`.


8. Click **Create load balancer**.

---

### Step 6: Test Load Balancing

1. Wait for the Load Balancer provisioning status to change to **Active**.
2. Select `web-alb` and copy the **DNS name** from the details pane.
3. Paste the DNS name into a web browser tab and press Enter. You will see: `Hello from Web Server 1` (or `Server 2`).
4. Refresh the page multiple times. The message will alternate between **Web Server 1** and **Web Server 2**, confirming round-robin load distribution.

---

### Step 7: Clean Up Resources

To avoid unnecessary AWS charges, delete resources in this sequence:

1. **Load Balancer:** Go to **Load Balancers**, select `web-alb`, and choose **Actions** -> **Delete**.
2. **Target Group:** Go to **Target Groups**, select `web-alb-tg`, and choose **Actions** -> **Delete**.
3. **EC2 Instances:** Go to **Instances**, select both web servers, and choose **Instance state** -> **Terminate instance**.
4. **Launch Template:** Go to **Launch Templates**, select `web-server-template`, and choose **Actions** -> **Delete template**.
5. **Security Group:** Go to **Security Groups**, select `web-server-sg`, and choose **Actions** -> **Delete security group**.