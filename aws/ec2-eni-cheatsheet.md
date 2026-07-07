# EC2 Elastic Network Interfaces Cheatsheet

## Overview

Elastic network interfaces are logical networking components in a VPC that represent virtual network cards. You can create and configure network interfaces and attach them to instances in the same Availability Zone. The attributes of a network interface follow it as it's attached or detached from an instance and reattached to another instance. When you move a network interface from one instance to another, network traffic is redirected from the original instance to the new instance.

```bash
# List all network interfaces
aws ec2 describe-network-interfaces

# Describe a specific network interface
aws ec2 describe-network-interfaces --network-interface-ids eni-1234567890abcdef0

# Create a network interface
aws ec2 create-network-interface \
  --subnet-id subnet-1234567890abcdef0 \
  --description "My network interface"
```

## Creating Network Interfaces

Network interfaces can be created independently and later attached to instances or created during instance launch. When creating a network interface, you specify the subnet, security groups, and optionally a description and private IP address. The network interface inherits the public IPv4 addressing attribute from the subnet at creation time. You can create multiple network interfaces for advanced networking scenarios like multi-homed instances or network appliances.

```bash
# Create a network interface in a specific subnet
aws ec2 create-network-interface \
  --subnet-id subnet-1234567890abcdef0 \
  --groups sg-1234567890abcdef0 \
  --description "Web server interface"

# Create with specific private IP
aws ec2 create-network-interface \
  --subnet-id subnet-1234567890abcdef0 \
  --private-ip-address 10.0.1.50 \
  --description "Database interface"

# Create with multiple secondary private IPs
aws ec2 create-network-interface \
  --subnet-id subnet-1234567890abcdef0 \
  --secondary-private-ip-address-count 3 \
  --description "Multi-IP interface"
```

## Attaching to Instances

Network interfaces can be attached to instances in the same Availability Zone. Each instance has a primary network interface that cannot be detached, but you can attach secondary network interfaces. The maximum number of network interfaces varies by instance type. Attaching a network interface immediately connects the instance to the network with all the interface's IP addresses and security group rules applied.

```bash
# Attach a network interface to an instance
aws ec2 attach-network-interface \
  --network-interface-id eni-1234567890abcdef0 \
  --instance-id i-1234567890abcdef0 \
  --device-index 1

# Attach as the primary interface during instance launch
aws ec2 run-instances \
  --image-id ami-1234567890abcdef0 \
  --instance-type t2.micro \
  --network-interfaces '[{"DeviceIndex":0,"NetworkInterfaceId":"eni-1234567890abcdef0"}]'

# Detach a network interface
aws ec2 detach-network-interface \
  --attachment-id eni-attach-1234567890abcdef0 \
  --force
```

## Managing IP Addresses

Network interfaces support primary and secondary private IPv4 addresses, IPv6 addresses, and public IPv4 addresses. You can assign secondary private IP addresses to a network interface and associate Elastic IP addresses with them. Secondary private IP addresses can be reassigned between instances, providing flexibility for network configuration. IPv6 addresses can be assigned if your VPC and subnet are configured with IPv6 CIDR blocks.

```bash
# Assign a secondary private IP
aws ec2 assign-private-ip-addresses \
  --network-interface-id eni-1234567890abcdef0 \
  --private-ip-addresses 10.0.1.100

# Assign multiple secondary IPs
aws ec2 assign-private-ip-addresses \
  --network-interface-id eni-1234567890abcdef0 \
  --secondary-private-ip-address-count 2

# Assign an IPv6 address
aws ec2 assign-ipv6-addresses \
  --network-interface-id eni-1234567890abcdef0 \
  --ipv6-addresses 2001:db8::123

# Associate an Elastic IP
aws ec2 associate-address \
  --allocation-id eipalloc-1234567890abcdef0 \
  --network-interface-id eni-1234567890abcdef0 \
  --private-ip-address 10.0.1.50
```

## Security Groups

Network interfaces can be associated with one or more security groups that control inbound and outbound traffic. Security group rules are applied to the network interface and affect all IP addresses on that interface. You can modify security group associations at any time, and changes take effect immediately. Security groups provide stateful firewalling, meaning responses to allowed traffic are automatically permitted.

```bash
# Associate security groups with a network interface
aws ec2 modify-network-interface-attribute \
  --network-interface-id eni-1234567890abcdef0 \
  --groups sg-1234567890abcdef0 sg-0987654321fedcba0

# View security groups for a network interface
aws ec2 describe-network-interfaces \
  --network-interface-ids eni-1234567890abcdef0 \
  --query 'NetworkInterfaces[0].Groups'

# Change security group association
aws ec2 modify-network-interface-attribute \
  --network-interface-id eni-1234567890abcdef0 \
  --groups sg-new-1234567890abcdef0
```

## Source/Destination Checks

Source/destination checks ensure that an instance is either the source or destination of any traffic it receives. This feature is enabled by default and prevents instances from processing traffic that doesn't originate from or terminate at the instance. You must disable source/destination checks for instances running network address translation, routing, or firewall services. Disabling these checks allows the instance to forward traffic between network interfaces.

```bash
# Disable source/destination checks
aws ec2 modify-network-interface-attribute \
  --network-interface-id eni-1234567890abcdef0 \
  --no-source-dest-check

# Enable source/destination checks
aws ec2 modify-network-interface-attribute \
  --network-interface-id eni-1234567890abcdef0 \
  --source-dest-check

# Check source/destination check status
aws ec2 describe-network-interfaces \
  --network-interface-ids eni-1234567890abcdef0 \
  --query 'NetworkInterfaces[0].SourceDestCheck'
```

## Termination Behavior

You can configure whether a network interface should be automatically deleted when the instance it's attached to is terminated. By default, network interfaces are not deleted when the instance terminates, allowing you to reuse them. Setting the delete-on-termination attribute to true ensures cleanup when instances are terminated. This is useful for temporary instances where you want network resources cleaned up automatically.

```bash
# Enable delete on termination
aws ec2 modify-network-interface-attribute \
  --network-interface-id eni-1234567890abcdef0 \
  --attachment-id eni-attach-1234567890abcdef0 \
  --delete-on-termination

# Disable delete on termination
aws ec2 modify-network-interface-attribute \
  --network-interface-id eni-1234567890abcdef0 \
  --attachment-id eni-attach-1234567890abcdef0 \
  --no-delete-on-termination

# Check termination behavior
aws ec2 describe-network-interfaces \
  --network-interface-ids eni-1234567890abcdef0 \
  --query 'NetworkInterfaces[0].Attachment.DeleteOnTermination'
```

## Monitoring with Flow Logs

VPC flow logs can be enabled on network interfaces to capture information about IP traffic going to and from the interface. Flow logs provide visibility into network traffic patterns and can help with security auditing, troubleshooting, and compliance. Flow log data is published to CloudWatch Logs where you can analyze and query the data. Enabling flow logs does not affect network performance or availability.

```bash
# Create a flow log for a network interface
aws ec2 create-flow-logs \
  --network-interface-ids eni-1234567890abcdef0 \
  --destination-type cloud-watch-logs \
  --log-group-name my-flow-logs \
  --deliver-logs-permission-arn arn:aws:iam::123456789012:role/FlowLogsRole

# Describe flow logs for a network interface
aws ec2 describe-flow-logs \
  --filter Name=resource-id,Values=eni-1234567890abcdef0

# Delete a flow log
aws ec2 delete-flow-logs --flow-log-ids fl-1234567890abcdef0
```

## Multiple Network Interfaces

Instances can have multiple network interfaces for advanced networking scenarios like creating network appliances, managing traffic segmentation, or providing high availability. Each additional network interface must be in the same subnet as the instance or a subnet in the same Availability Zone. You can configure routing between interfaces to implement complex network topologies. Multiple interfaces are commonly used for load balancers, firewalls, and proxy servers.

```bash
# Launch instance with multiple network interfaces
aws ec2 run-instances \
  --image-id ami-1234567890abcdef0 \
  --instance-type t2.micro \
  --network-interfaces \
    '[{"DeviceIndex":0,"NetworkInterfaceId":"eni-1234567890abcdef0"}]' \
    '[{"DeviceIndex":1,"NetworkInterfaceId":"eni-0987654321fedcba0"}]'

# View all network interfaces for an instance
aws ec2 describe-instances \
  --instance-ids i-1234567890abcdef0 \
  --query 'Reservations[0].Instances[0].NetworkInterfaces'

# Add a secondary network interface to running instance
aws ec2 attach-network-interface \
  --network-interface-id eni-abcdef1234567890 \
  --instance-id i-1234567890abcdef0 \
  --device-index 2
```

## Deleting Network Interfaces

Network interfaces can be deleted when they are no longer needed, but only if they are not attached to any instance. You must detach the network interface from all instances before deletion. Deleting a network interface releases all associated IP addresses and disassociates any Elastic IP addresses. It's important to verify that the interface is not in use before deletion to avoid disrupting network connectivity.

```bash
# Check if network interface is attached
aws ec2 describe-network-interfaces \
  --network-interface-ids eni-1234567890abcdef0 \
  --query 'NetworkInterfaces[0].Attachment'

# Delete a network interface
aws ec2 delete-network-interface --network-interface-id eni-1234567890abcdef0

# Delete multiple network interfaces
aws ec2 delete-network-interface \
  --network-interface-id eni-1234567890abcdef0 \
  --network-interface-id eni-0987654321fedcba0
```

## Common ENI Use Cases

Elastic network interfaces are used for various networking scenarios including creating management networks, implementing network segmentation, and building network appliances. They enable separation of management and data traffic, improve security through network isolation, and support high availability configurations. Network interfaces are essential for complex architectures requiring multiple network paths or specialized network functions.

```bash
# Management network interface (separate from data traffic)
aws ec2 create-network-interface \
  --subnet-id subnet-mgmt-1234567890abcdef0 \
  --groups sg-mgmt-1234567890abcdef0 \
  --description "Management interface"

# Data network interface for high throughput
aws ec2 create-network-interface \
  --subnet-id subnet-data-1234567890abcdef0 \
  --groups sg-data-1234567890abcdef0 \
  --description "Data interface"

# Network appliance interface (source/dest check disabled)
aws ec2 create-network-interface \
  --subnet-id subnet-appliance-1234567890abcdef0 \
  --description "Appliance interface"
aws ec2 modify-network-interface-attribute \
  --network-interface-id eni-appliance-1234567890abcdef0 \
  --no-source-dest-check
```

## Common EC2 ENI Commands

| Command | Description |
|---------|-------------|
| `create-network-interface` | Create a new network interface |
| `describe-network-interfaces` | List or describe network interfaces |
| `attach-network-interface` | Attach interface to an instance |
| `detach-network-interface` | Detach interface from an instance |
| `delete-network-interface` | Delete a network interface |
| `assign-private-ip-addresses` | Assign secondary private IPs |
| `assign-ipv6-addresses` | Assign IPv6 addresses |
| `modify-network-interface-attribute` | Modify interface attributes |
| `associate-address` | Associate Elastic IP address |
| `create-flow-logs` | Enable VPC flow logs |
