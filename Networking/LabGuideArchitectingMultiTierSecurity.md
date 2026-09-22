# Architecting Multi-Tier Security in AWS VPC

## 1. Lab Overview & Technical Architecture

The objective of this lab is to design and implement a secure, production-grade network environment within Amazon Web Services (AWS). Using a Virtual Private Cloud (VPC), you will build a 3-tier architecture that isolates sensitive database workloads from the public internet while facilitating controlled administrative access via a Bastion host.

The 3-Tier Network Design

The following table illustrates the structural design of the environment you will deploy:

Subnet Name	CIDR Block	Accessibility	Intended Workload
Public Subnet	10.0.1.0/24	Public	Bastion/Jump Host (Administrative Gateway)
Web Private Subnet	10.0.2.0/24	Private	Apache Web Server (Internal App Tier)
DB Private Subnet	10.0.3.0/24	Private	MySQL Database (Data Persistence Tier)

<b>NOTE</b>: The "So What?" – Why Multi-Tier Security Matters In a "flat" network, a single compromised server grants an attacker lateral access to your entire environment. A 3-tier architecture implements Defense in Depth. By placing the database in a dedicated private subnet with no public route, you ensure it is unreachable from the internet. Even if the web tier is compromised, the attacker must still bypass secondary firewalls (Security Groups) and stateless filters (NACLs) to reach your data.

Transition: Before constructing the network, you must establish a secure cryptographic foundation for authentication using SSH Key Pairs.

## 2. Prerequisite: Securing Your Gateway (Key Pairs & Local Environment)

To access your instances securely, you require a cryptographic key pair.

Create the Key Pair in AWS

1. Navigate to the EC2 Console.
2. In the left-hand navigation pane, under Network & Security, click Key Pairs.
3. Click ```Create key pair```.
4. Configure the following:
  * Name: ```lab-key-pair```
  * Key pair type: ```RSA```
  * Private key file format: ```.pem```
5. Click Create key pair. The file will download automatically; save it to a secure local directory (e.g., ~/.ssh/).

Prepare Your Local Environment

Open your terminal (Linux, macOS, or WSL) and execute the following sequence to prepare your key:

# 1. Set strict permissions
```
chmod 400 ~/.ssh/lab-key-pair.pem
```
# 2. Start the SSH agent
```
eval "$(ssh-agent -s)"
```
# 3. Add the key to the agent
```
ssh-add ~/.ssh/lab-key-pair.pem
```

* Why chmod 400? SSH clients reject private keys that are "too open" (readable by other users on your machine) to prevent local security leaks.
* Why ssh-agent? This allows your local machine to securely "remember" the key, enabling you to "jump" from the Bastion to private instances without manually copying your private key to the cloud.

Transition: With authentication ready, you can now build the VPC "container" where your infrastructure will reside.

## 3. Infrastructure Foundation: Building the VPC and Subnets

The AWS "VPC and more" workflow allows for the simultaneous creation of subnets, gateways, and routing tables.

1. Navigate to the VPC Console and click ```Create VPC```.
2. Select ```VPC and more```.
3. Project Details:
  * Name tag prefix: ```networking-vpc```
  * IPv4 CIDR block: ```10.0.0.0/16```
4. Subnet Configuration:
  * Number of Availability Zones (AZs): ```1```
  * Number of public subnets: ```1``` (This creates ```10.0.1.0/24```).
  * Number of private subnets: ```2``` (This creates ```10.0.2.0/24``` and ```10.0.3.0/24```).
5. Gateways:
  * NAT Gateways: Select ```1 per AZ```.
  * VPC Endpoints: ```None```.

<B>IMPORTANT</B> Cost Note: While NAT Gateways are essential for private instances to download updates (like Apache or MariaDB) securely, they incur hourly charges and data processing fees. In a production environment, always monitor NAT Gateway usage.

1. Click ```Create VPC```.

Transition: While the subnets define the "where," the next step defines the "who" regarding specific traffic access.

## 4. Access Control Layers: Security Group Configuration

Security Groups act as stateful virtual firewalls for your instances.

Navigation

1. Click the Top Search Bar in the AWS Console.
2. Type VPC and select the VPC service.
3. In the left sidebar, scroll to <b>Security</b> > <b>Security groups</b>.
4. Click <b>Create security group</b>.

<b>TIP Deep Dive</B>: 'My IP' When adding SSH rules, selecting My IP from the source dropdown automatically detects your current public IP and restricts access solely to you. If your IP changes (e.g., switching networks), you can verify it at https://checkip.amazonaws.com.

4.1. public-bastion-sg

* Description: Administrative access for the Bastion host.
* VPC: Select ```networking-vpc```.
* Inbound Rule: ```SSH``` (Port 22) | Protocol: ```TCP``` | Source: ```My IP```.

4.2. apache-web-sg

* Description: Rules for the Web Tier.
* VPC: Select ```networking-vpc```.
* Inbound Rule 1: ```HTTP``` (Port 80) | Protocol: ```TCP``` | Source: ```public-bastion-sg``` (Search for the SG ID).
* Inbound Rule 2: ```SSH``` (Port 22) | Protocol: ```TCP``` | Source: ```public-bastion-sg```.

4.3. mysql-db-sg

* Description: Rules for the Database Tier.
* VPC: Select ```networking-vpc```.
* Inbound Rule: ```MYSQL/Aurora``` (Port 3306) | Protocol: ```TCP``` | Source: ```apache-web-sg```.

Security Group Chaining: By using a Security Group ID as a source instead of an IP range, you ensure that only instances assigned to the Web group can communicate with the DB group, regardless of their specific IP addresses.

Transition: Now that the firewall rules are defined, we will deploy the instances that will live within them.

## 5. Compute Deployment: Provisioning the Multi-Tier Stack

Navigate to the EC2 Dashboard and click Launch instance to create the following three servers.

1. Public-Host (The Bastion)

* AMI: ```Amazon Linux 2023```
* Key Pair: ```lab-key-pair```
* VPC: ```networking-vpc```
* Subnet: ```Public Subnet (10.0.1.0/24)```
* Public IP: ```Enable```
* Security Group: ```public-bastion-sg```

2. Apache-Server (The Web Tier)

* AMI: ```Amazon Linux 2023```
* Key Pair: ```lab-key-pair```
* VPC: ```networking-vpc```
* Subnet: ```Web Private Subnet (10.0.2.0/24)```
* Public IP: ```Disable```
* Security Group: ```apache-web-sg```
* User Data (Advanced Details):

```bash
#!/bin/bash
dnf update -y
dnf install -y httpd mariadb105
systemctl start httpd
systemctl enable httpd
echo "<h1>Apache Web Server Active</h1>" > /var/www/html/index.html
```

3. MySQL-Server (The Database Tier)

* AMI: ```Amazon Linux 2023```
* Key Pair: ```lab-key-pair```
* VPC: ```networking-vpc```
* Subnet: ```DB Private Subnet (10.0.3.0/24)```
* Public IP: ```Disable```
* Security Group: ```mysql-db-sg```
* User Data (Advanced Details):

```bash
#!/bin/bash
dnf update -y
dnf install -y mariadb105-server
systemctl start mariadb
systemctl enable mariadb
```

Transition: Once the instances reach the "Running" state, we will prove the security paths work as intended.

## 6. Verification: Connectivity & "ProxyJump" Testing

The ProxyJump Command

To access the private instances, you must "jump" through the Bastion. Run this from your local terminal:

```
ssh -J ec2-user@[Bastion-Public-IP] ec2-user@[Apache-Private-IP]
```

Verification: Your prompt should change to [ec2-user@ip-10-0-2-x ~].

Internal Path Testing

1. Test Web Service (from Public-Host): SSH into the Public-Host and run: curl http://[Apache-Private-IP]

Expected Output: <h1>Apache Web Server Active</h1>

1. Test Database Port (from Apache-Server): From your Apache-Server SSH session, run: 
```
nc -zv [MySQL-Private-IP] 3306
```
Expected Output: 
```
Ncat: Connected to [MySQL-Private-IP]:3306.
```

Transition: These tests confirm that the stateful Security Groups are working. Now, we will test the stateless Network ACLs.

## 7. Network ACL (NACL) Testing: Stateless Packet Filtering

NACLs are stateless and process rules in strict numerical order.

1. Navigate to VPC > Subnets and select the DB Private Subnet (10.0.3.0/24).
2. Click the Network ACL tab and select the associated NACL ID.
3. Click Edit inbound rules and Add new rule:
  * Rule number: ```50``` (Lower numbers override higher numbers).
  * Type: ```Custom TCP``` | Port Range: ```3306```.
  * Source: ```[Apache-Private-IP]/32```.
  * Action: ```DENY```.
4. Test: Re-run the nc command from the Apache Server: 
```
nc -zv -w 5 [MySQL-Private-IP] 3306
```
Expected Result: ```Ncat: Connection timed out.```

1. Restore: Delete Rule 50 from the NACL to restore connectivity.

## 8. Troubleshooting & Common Pitfalls

Error Message	Probable Cause	Step-by-Step Resolution
Could not open a connection to your authentication agent	ssh-agent is not running.	

Linux/Mac: ```eval "$(ssh-agent -s)"```. 

Windows (PS Admin): ```Start-Service ssh-agent```
.
Permissions 0644 are too open	Private key file has insecure OS permissions.	

Linux/Mac: ```chmod 400 lab-key-pair.pem```.
Windows (PS): ```Use icacls.exe .\lab-key-pair.pem /inheritance:r```
followed by 
```icacls.exe .\lab-key-pair.pem /grant:r "$($env:USERNAME):F"```
.

Permission denied (publickey)	Wrong username or key not loaded.	Run ```ssh-add -l``` to verify key. Ensure you use ec2-user.

## 9. Resource Teardown & Cleanup

To avoid unnecessary AWS costs, delete resources in this order:

1. Terminate EC2 Instances: Select Public-Host, Apache-Server, and MySQL-Server > Instance State > Terminate.
2. Delete Security Groups: Wait for instances to terminate, then delete your custom SGs.
3. Delete VPC: Select networking-vpc > Actions > Delete VPC. This will clean up the subnets, Internet Gateway, and NAT Gateway automatically.

Congratulations! You have successfully architected and deployed a secure, multi-tier AWS environment using Defense in Depth principles.
