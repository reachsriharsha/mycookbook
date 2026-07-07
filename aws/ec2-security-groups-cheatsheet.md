# EC2 Security Groups Cheatsheet

## Overview

EC2 security groups act as virtual firewalls for your EC2 instances to control incoming and outgoing traffic. Inbound rules control the incoming traffic to your instance, and outbound rules control the outgoing traffic from your instance. Security groups are stateful, meaning if you send a request from your instance, the response traffic is allowed to flow in regardless of inbound rules. You can associate each instance with multiple security groups, and each security group with multiple instances. Rules are automatically applied to all instances associated with the security group.

```bash
# List all security groups
aws ec2 describe-security-groups

# Describe a specific security group
aws ec2 describe-security-groups --group-ids sg-1234567890abcdef0

# Get security group by name
aws ec2 describe-security-groups --group-names my-security-group
```

## Creating Security Groups

Security groups are created at the VPC level and contain rules that specify which traffic is allowed to reach associated instances. When you launch an instance, you can specify one or more security groups to control network access. If you don't specify a security group, Amazon EC2 uses the default security group for the VPC. You can create security groups with specific rules for different use cases like web servers, databases, or application servers.

```bash
# Create a security group
aws ec2 create-security-group \
  --group-name my-security-group \
  --description "My security group" \
  --vpc-id vpc-1234567890abcdef0

# Create a security group with tags
aws ec2 create-security-group \
  --group-name my-web-server \
  --description "Security group for web servers" \
  --vpc-id vpc-1234567890abcdef0 \
  --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=my-web-server}]'
```

## Adding Inbound Rules

Inbound rules control the traffic that can reach your EC2 instances. You can specify rules based on protocol, port range, and source IP addresses or security groups. Common inbound rules include allowing SSH (port 22), HTTP (port 80), HTTPS (port 443), and custom application ports. You can add rules to allow traffic from specific IP ranges, other security groups, or all IPs (0.0.0.0/0).

```bash
# Add SSH access from specific IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-1234567890abcdef0 \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/24

# Add HTTP access from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id sg-1234567890abcdef0 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Add access from another security group
aws ec2 authorize-security-group-ingress \
  --group-id sg-1234567890abcdef0 \
  --protocol tcp \
  --port 3306 \
  --source-group sg-0987654321fedcba0

# Add multiple ports at once
aws ec2 authorize-security-group-ingress \
  --group-id sg-1234567890abcdef0 \
  --ip-permissions 'IpProtocol=tcp,FromPort=8000,ToPort=9000,IpRanges=[{CidrIp=0.0.0.0/0}]'
```

## Adding Outbound Rules

Outbound rules control the traffic that can leave your EC2 instances. By default, security groups allow all outbound traffic, but you can restrict this for enhanced security. Outbound rules are useful when you want to limit which external services your instances can access. You can specify destination IP ranges, security groups, or specific ports for outbound traffic.

```bash
# Remove default outbound rule (allow all)
aws ec2 revoke-security-group-egress \
  --group-id sg-1234567890abcdef0 \
  --ip-permissions '[{"IpProtocol": "-1", "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}]'

# Add outbound rule for specific destination
aws ec2 authorize-security-group-egress \
  --group-id sg-1234567890abcdef0 \
  --protocol tcp \
  --port 443 \
  --cidr 10.0.0.0/16

# Allow outbound to specific security group
aws ec2 authorize-security-group-egress \
  --group-id sg-1234567890abcdef0 \
  --protocol tcp \
  --port 5432 \
  --destination-group sg-0987654321fedcba0
```

## Managing Rules

Security group rules can be modified at any time, and changes are automatically applied to all associated instances. You can add, remove, or update rules to adapt to changing security requirements. It's important to review and clean up unused rules to maintain security hygiene. Connection tracking ensures that responses to allowed inbound traffic are allowed to flow out regardless of outbound rules.

```bash
# List all rules for a security group
aws ec2 describe-security-groups --group-ids sg-1234567890abcdef0

# Remove an inbound rule
aws ec2 revoke-security-group-ingress \
  --group-id sg-1234567890abcdef0 \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/24

# Remove an outbound rule
aws ec2 revoke-security-group-egress \
  --group-id sg-1234567890abcdef0 \
  --protocol tcp \
  --port 443 \
  --cidr 10.0.0.0/16
```

## Associating with Instances

Security groups must be associated with EC2 instances to control network access. You can specify security groups when launching an instance or change them later. An instance can be associated with multiple security groups, and each security group can be associated with multiple instances. This flexibility allows you to create modular security policies for different types of workloads.

```bash
# Launch instance with security groups
aws ec2 run-instances \
  --image-id ami-1234567890abcdef0 \
  --instance-type t2.micro \
  --security-group-ids sg-1234567890abcdef0 sg-0987654321fedcba0

# Change security groups for a running instance
aws ec2 modify-instance-attribute \
  --instance-id i-1234567890abcdef0 \
  --groups sg-1234567890abcdef0 sg-0987654321fedcba0

# View security groups for an instance
aws ec2 describe-instances --instance-ids i-1234567890abcdef0 \
  --query 'Reservations[0].Instances[0].SecurityGroups'
```

## Deleting Security Groups

Security groups can be deleted when they are no longer needed, but only if they are not associated with any instances. You must first disassociate the security group from all instances before deletion. It's good practice to review dependencies before deleting security groups to avoid disrupting running workloads. The default security group cannot be deleted.

```bash
# Check if security group is in use
aws ec2 describe-network-interfaces --filters "Name=group-id,Values=sg-1234567890abcdef0"

# Delete a security group
aws ec2 delete-security-group --group-id sg-1234567890abcdef0

# Delete security group by name (not recommended, use ID)
aws ec2 delete-security-group --group-name my-security-group
```

## Common Rule Patterns

Security groups can be configured for various common scenarios like web servers, databases, or load balancers. Web servers typically need HTTP and HTTPS access from the internet, while databases should only be accessible from application tier security groups. Using security group references instead of IP addresses provides better manageability and security. These patterns help implement defense-in-depth strategies.

```bash
# Web server security group (HTTP/HTTPS from anywhere)
aws ec2 authorize-security-group-ingress \
  --group-id sg-web \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-web \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Database security group (only from app tier)
aws ec2 authorize-security-group-ingress \
  --group-id sg-db \
  --protocol tcp \
  --port 3306 \
  --source-group sg-app

# SSH from specific IP (administrative access)
aws ec2 authorize-security-group-ingress \
  --group-id sg-web \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.50/32
```

## Security Best Practices

Security groups should follow the principle of least privilege by only allowing necessary traffic. Avoid using 0.0.0.0/0 for sensitive ports like SSH or database ports unless absolutely required. Regularly audit security group rules to remove unused permissions and maintain security hygiene. Use security group references instead of hardcoded IP addresses for better manageability and automatic updates when infrastructure changes.

```bash
# Audit security groups for overly permissive rules
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?contains(IpPermissions[].IpRanges[].CidrIp, `0.0.0.0/0`)]'

# List security groups with no instances (potentially unused)
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?length(IpPermissions) == `0` && length(IpPermissionsEgress) == `1`]'

# Check for SSH access from anywhere
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?IpPermissions[?FromPort == `22` && IpRanges[?CidrIp == `0.0.0.0/0`]]]'
```

## Common EC2 Security Group Commands

| Command | Description |
|---------|-------------|
| `create-security-group` | Create a new security group |
| `describe-security-groups` | List or describe security groups |
| `authorize-security-group-ingress` | Add inbound rule |
| `revoke-security-group-ingress` | Remove inbound rule |
| `authorize-security-group-egress` | Add outbound rule |
| `revoke-security-group-egress` | Remove outbound rule |
| `delete-security-group` | Delete a security group |
| `modify-instance-attribute` | Change security groups for an instance |
