
# AWS Auto Scaling Lab

Here is a complete, step-by-step lab guide for setting up an AWS Auto Scaling Group (ASG) using `t3.micro` instances running Amazon Linux.

In this lab, the `stress` utility will be pre-installed via User Data during launch, but you will manually SSH in to run `stress`. Once CPU usage exceeds **30%**, CloudWatch triggers a target tracking policy to spin up additional instances.

__Estimated Time to Complete__

This lab should take approximately 30 to 45 minutes from start to finish:

Phases 1 & 2 (Setup): ~10–15 minutes

Phase 3 & 4 (Trigger & Observe Scale-Out): ~10–15 minutes (Wait time for CloudWatch metrics to breach the threshold and trigger ASG)

Phase 5 & 6 (Scale-In & Teardown): ~10–15 minutes

---

## Phase 1: Security Group & Launch Template

### Step 1: Create a Security Group

1. Open the **AWS Management Console** and navigate to **EC2**.
2. In the left navigation pane, under **Network & Security**, click **Security Groups**.
3. Click **Create security group** and enter:
* **Security group name:** `asg-lab-sg`
* **Description:** `Allow SSH traffic for Auto Scaling lab`
* **VPC:** Select your Default VPC.


4. Under **Inbound rules**, click **Add rule**:
* **Type:** SSH
* **Port:** 22
* **Source:** My IP (or `0.0.0.0/0` for testing, though restricting to your IP is safer).

<b>NOTE:</b>To restrict the IP use 73.155.137.121/32

5. Click **Create security group**.

---

### Step 2: Create a Launch Template

1. In the EC2 console left menu, under **Instances**, click **Launch Templates**.
2. Click **Create launch template**:
* **Launch template name:** `asg-lab-template`
* **Template version description:** `v1 - Amazon Linux with stress`


3. **Application and OS Images (AMI):**
* Select **Amazon Linux** (Choose **Amazon Linux 2023** or **Amazon Linux 2**).


4. **Instance type:**
* Select `t3.micro`.


5. **Key pair:**
* Select your existing SSH key pair (or create one so you can SSH into the instance later).


6. **Network settings:**
* **Security groups:** Select `asg-lab-sg`.


7. **Advanced details:**
* Scroll down to the **User data** field and paste the following script to pre-install `stress`:



```bash
#!/bin/bash
# Universal User Data script for tmux and stress installation

if command -v dnf &> /dev/null; then
    # Amazon Linux 2023
    dnf update -y
    dnf install -y tmux stress || dnf install -y tmux stress-ng
else
    # Amazon Linux 2
    yum update -y
    yum install -y tmux
    amazon-linux-extras install epel -y
    yum install -y stress
fi
```


8. Click **Create launch template**.

---

## Phase 2: Create the Auto Scaling Group

1. In the EC2 console left menu, under **Auto Scaling**, click **Auto Scaling Groups**.
2. Click **Create Auto Scaling group**.

### Step 1: Choose launch template or configuration

* **Auto Scaling group name:** `asg-lab-group`
* **Launch template:** Select `asg-lab-template`.
* Click **Next**.

### Step 2: Choose instance launch options

* **VPC:** Select your Default VPC.
* **Availability Zones and subnets:** Select **at least 2 or 3 subnets** across different Availability Zones (e.g., `us-east-1a`, `us-east-1b`, `us-east-1c`).
* Click **Next**.

### Step 3: Configure advanced options

* Leave **Load balancing** set to *No load balancer* (or attached if needed, but not required for CPU metric scaling).
* Leave **Health check grace period** at `300` seconds.
* Click **Next**.

### Step 4: Configure group size and scaling policies

1. **Group size:**
* **Desired capacity:** `1`
* **Minimum capacity:** `1`
* **Maximum capacity:** `3`


2. **Scaling policies:**
* Select **Target tracking scaling policy**.
* **Scaling policy name:** `CPU-Target-50-Percent`
* **Metric type:** `Average CPU utilization`
* **Target value:** `50`
* **Instance warmup:** `60` seconds (allows new instances to stabilize quickly for testing).


3. Click **Next**, skip **Add notifications** and **Add tags**, then review and click **Create Auto Scaling group**.

---

## Phase 3: Trigger Auto Scaling (Simulate Load)

1. Navigate to **EC2 > Instances**. You will see **1 instance** starting up from your Auto Scaling Group.
2. Wait until its **Instance State** is `Running` and **Status Checks** pass (`2/2 checks passed`).
3. Copy the **Public IPv4 Address** of the running instance.
4. Open your local terminal (or Command Prompt) and SSH into the instance:
```bash
ssh -i /path/to/your-key.pem ec2-user@<YOUR-INSTANCE-PUBLIC-IP>

```
5. execute tmux. Use ctrl-b and shift-" to open to a second pane. Navigate between panes using ctrl-b and the up/down arrow keys.

6. Manually trigger the high CPU load using `stress`:
```bash
stress --cpu 2 --timeout 1200

```
*(This runs 2 CPU-bound processes for 10 minutes, forcing CPU usage near 100%).*

7. Naviage to the other pane using ctrl-b and the arrow keys. Execute top and verify stress us using 100% cpu. 

---

## Phase 4: Verify Auto Scaling Action

1. Return to the AWS EC2 Console and navigate to **Auto Scaling Groups > `asg-lab-group**`.
2. Click the **Activity** tab:
* Within **3–5 minutes**, CloudWatch will detect that average CPU usage exceeds 30%.
* You will see activity history entries indicating that the ASG is launching a 2nd (and eventually a 3rd) instance to bring the average CPU load back down.


3. Check **EC2 > Instances** to see the new `t3.micro` instances provisioning automatically.

---
## Phase 5: Reduce the CPU Load

1. Stop stress from running. 
2. Verify that the number of running instances was reduced. 
---
## Phase 6: Lab Tear Down Instructions

To ensure you do not incur unwanted AWS charges, destroy resources in the following exact order:

1. **Delete the Auto Scaling Group:**
* Go to **EC2 > Auto Scaling Groups**.
* Select `asg-lab-group`, click **Actions** > **Delete**.
* Type `delete` to confirm.
* *Deleting the ASG automatically terminates all EC2 instances managed by it.*


2. **Delete the Launch Template:**
* Go to **EC2 > Launch Templates**.
* Select `asg-lab-template`, click **Actions** > **Delete template**.
* Type `Delete` to confirm.


3. **Delete the Security Group:**
* Go to **EC2 > Security Groups**.
* Select `asg-lab-sg`, click **Actions** > **Delete security groups** (Wait a minute if instance termination is still finalizing, as the interface may be attached briefly).


4. **Verify Clean-up:**
* Go to **EC2 > Instances** and verify all instances show the `Terminated` state.

-----

# AWS Auto Scaling notes

By default, AWS Auto Scaling uses a multi-step evaluation process designed to preserve high availability and cost efficiency. It evaluates instances using the following decision tree:

### Step 1: Balance Across Availability Zones (Highest Priority)

AWS checks which Availability Zone (AZ) contains the highest number of instances.

* **If one AZ has more instances than others:** AWS targets that specific AZ to force a scale-in there first, keeping your capacity evenly balanced across zones for reliability.
* **If instances are equally spread across AZs:** AWS evaluates all unprotected instances across all zones.

---

### Step 2: Check for Outdated Configurations

Within the targeted AZ(s), AWS checks if any instances are running on older settings. It prioritizes terminating instances launched from:

1. An older **Launch Configuration** (or an older version of a Launch Template) over those running the latest template.
2. Non-standard or legacy configurations.

---

### Step 3: Check Instance Age (Oldest vs. Newest)

If all candidate instances share the exact same configuration version:

* AWS selects the **oldest instance** (the one launched first) for termination.

---

### Step 4: Random Selection (Tie-Breaker)

If multiple instances share the same configuration and creation timestamp (which can happen during sudden scale-out spikes):

* AWS selects one of those instances **at random** to terminate.

---

### Overriding the Default Behavior

You can change this behavior in your Auto Scaling Group settings under **Termination Policies**:

| Predefined Policy | How It Works |
| --- | --- |
| **`OldestInstance`** | Terminates the oldest instance in the group. Useful when gradually rolling out hardware/AMI updates. |
| **`NewestInstance`** | Terminates the newest instance. Ideal for testing new configurations without losing long-running instances. |
| **`OldestLaunchConfiguration`** | Specifically targets instances running legacy configs. |
| **`AllocationStrategy`** | Used in mixed-instance groups to maintain the cheapest ratio of Spot vs. On-Demand capacity. |

---

### How to Protect Specific Instances

If an instance is actively processing a job or storing state that shouldn't be interrupted, you can shield it:

1. **Instance Scale-In Protection:** Toggle protection on specific instances via the EC2 console or CLI to make them immune to scale-in actions.
2. **Lifecycle Hooks:** Pause instance termination for a custom time window (e.g., 5 minutes) so scripts can gracefully finish active tasks or drain connections before the EC2 shuts down.