# Amazon EFS (Elastic File System) Cheat Sheet

## Overview

Amazon Elastic File System (EFS) provides serverless, fully elastic file storage that scales automatically as you add and remove files. EFS supports the Network File System version 4 (NFSv4.1 and NFSv4.0) protocol and can be accessed from multiple AWS compute services simultaneously.

## Key Concepts

### File System Types

#### Regional (Recommended)
- **Availability**: Data stored across multiple Availability Zones
- **Durability**: 99.999999999% (11 9s)
- **Availability SLA**: 99.99%
- **Use Case**: Data requiring highest durability and availability
- **Cost**: Higher than One Zone

#### One Zone
- **Availability**: Data stored in single Availability Zone
- **Durability**: 99.999999999% (11 9s) within AZ
- **Availability SLA**: 99.99%
- **Use Case**: Cost-optimized storage for non-critical data
- **Cost**: Up to 47% lower than Regional
- **Backup**: Automatically backed up with AWS Backup

### Performance Modes

#### General Purpose (Recommended)
- **Latency**: ~1 millisecond per operation
- **IOPS**: Up to 7,000 file operations per second
- **Use Case**: Latency-sensitive applications
- **Availability**: All file system types

#### Max I/O (Legacy)
- **Latency**: Higher than General Purpose
- **IOPS**: Higher than General Purpose (>7,000)
- **Use Case**: Highly parallelized workloads (not recommended)
- **Limitations**: Not supported for One Zone or Elastic throughput

### Throughput Modes

#### Elastic (Recommended)
- **Scaling**: Automatically scales up/down based on workload
- **Performance**: Up to 20-60 GiBps read, 1-5 GiBps write (Regional)
- **Billing**: Pay for throughput used
- **Use Case**: Variable workloads

#### Provisioned
- **Performance**: Fixed throughput regardless of storage size
- **Billing**: Pay for provisioned throughput
- **Use Case**: Consistent high throughput requirements

#### Bursting (Legacy)
- **Performance**: Throughput scales with file system size
- **Burst Credits**: Accumulate credits when below baseline
- **Use Case**: Workloads with periodic high throughput needs

## Storage Classes

### Standard
- **Performance**: Lowest latency per operation
- **Use Case**: Frequently accessed data
- **Cost**: Higher storage cost

### Infrequent Access (IA)
- **Performance**: Slightly higher latency
- **Use Case**: Files accessed less than once per month
- **Cost**: Lower storage cost, access charges apply
- **Lifecycle**: Automatic transition available

## Common AWS CLI Commands

### File System Management
```bash
# Create file system
aws efs create-file-system \
    --creation-token my-token \
    --performance-mode generalPurpose \
    --throughput-mode elastic \
    --availability-zone-name us-east-1a

# List file systems
aws efs describe-file-systems

# Create Regional file system with encryption
aws efs create-file-system \
    --creation-token my-encrypted-token \
    --performance-mode generalPurpose \
    --throughput-mode elastic \
    --encrypted

# Delete file system
aws efs delete-file-system --file-system-id fs-12345678
```

### Mount Targets
```bash
# Create mount target
aws efs create-mount-target \
    --file-system-id fs-12345678 \
    --subnet-id subnet-12345678 \
    --security-groups sg-12345678

# List mount targets
aws efs describe-mount-targets --file-system-id fs-12345678

# Delete mount target
aws efs delete-mount-target --mount-target-id fsmt-12345678
```

### Access Points
```bash
# Create access point
aws efs create-access-point \
    --file-system-id fs-12345678 \
    --posix-user Uid=1001,Gid=1001 \
    --root-directory Path="/secure",CreationInfo='{OwnerUid=1001,OwnerGid=1001,Permissions=755}'

# List access points
aws efs describe-access-points --file-system-id fs-12345678

# Delete access point
aws efs delete-access-point --access-point-id fsap-12345678
```

### Lifecycle Management
```bash
# Put lifecycle configuration
aws efs put-lifecycle-configuration \
    --file-system-id fs-12345678 \
    --lifecycle-policies TransitionToIA=AFTER_30_DAYS,TransitionToPrimaryStorageClass=AFTER_1_ACCESS

# Get lifecycle configuration
aws efs describe-lifecycle-configuration --file-system-id fs-12345678
```

### Backup Policy
```bash
# Enable automatic backups
aws efs put-backup-policy \
    --file-system-id fs-12345678 \
    --backup-policy Status=ENABLED

# Get backup policy
aws efs describe-backup-policy --file-system-id fs-12345678
```

## Mounting EFS

### Using EFS Utils (Recommended)
```bash
# Install EFS utils (Amazon Linux 2)
sudo yum install -y amazon-efs-utils

# Mount using file system ID
sudo mount -t efs fs-12345678:/ /mnt/efs

# Mount with encryption in transit
sudo mount -t efs -o tls fs-12345678:/ /mnt/efs

# Mount using access point
sudo mount -t efs -o tls,accesspoint=fsap-12345678 fs-12345678:/ /mnt/efs

# Add to /etc/fstab for persistent mounting
echo "fs-12345678.efs.us-east-1.amazonaws.com:/ /mnt/efs efs defaults,_netdev,tls" >> /etc/fstab
```

### Using Standard NFS Client
```bash
# Mount using DNS name
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,intr,timeo=600 \
    fs-12345678.efs.us-east-1.amazonaws.com:/ /mnt/efs

# Mount using IP address
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,intr,timeo=600 \
    172.31.1.1:/ /mnt/efs
```

## Security and Access Control

### Network Security
```bash
# Security group rules for EFS
# Inbound: NFS (2049) from EC2 security group
# Outbound: NFS (2049) to EFS mount targets

# Example security group rule
aws ec2 authorize-security-group-ingress \
    --group-id sg-efs-mount-target \
    --protocol tcp \
    --port 2049 \
    --source-group sg-ec2-instances
```

### IAM Policies
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "elasticfilesystem:ClientMount",
                "elasticfilesystem:ClientWrite",
                "elasticfilesystem:ClientRootAccess"
            ],
            "Resource": "arn:aws:elasticfilesystem:*:*:file-system/fs-12345678"
        }
    ]
}
```

### POSIX Permissions
```bash
# Set directory permissions
sudo chmod 755 /mnt/efs/directory

# Set file ownership
sudo chown user:group /mnt/efs/file

# Create directory with specific permissions
sudo mkdir -m 755 /mnt/efs/newdir
```

## Performance Optimization

### Best Practices
- **Use EFS Utils**: Better performance than standard NFS client
- **Optimize Mount Options**: Use recommended rsize/wsize values
- **Multiple Connections**: Use multiple mount targets for higher throughput
- **File Size**: Larger files generally achieve higher throughput
- **Concurrent Access**: Multiple clients can improve aggregate performance

### Mount Options for Performance
```bash
# Optimized mount options
sudo mount -t efs -o tls,rsize=1048576,wsize=1048576,hard,intr,timeo=600 \
    fs-12345678:/ /mnt/efs
```

### Monitoring Performance
```bash
# Key CloudWatch metrics to monitor:
# - TotalIOTime: Total time for file system operations
# - DataReadIOBytes/DataWriteIOBytes: Throughput metrics
# - MetadataIOBytes: Metadata operation throughput
# - PercentIOLimit: IOPS utilization (General Purpose mode)
# - BurstCreditBalance: Available burst credits (Bursting mode)
```

## Use Cases and Patterns

### Content Management
- **Web Serving**: Shared content across multiple web servers
- **Media Processing**: Shared storage for video/image processing workflows
- **Backup Storage**: Centralized backup destination

### Big Data and Analytics
- **Data Lakes**: Shared storage for analytics workloads
- **Machine Learning**: Training data accessible from multiple instances
- **Log Aggregation**: Centralized log storage and processing

### Application Development
- **Shared Configuration**: Configuration files across environments
- **Home Directories**: User home directories in multi-user environments
- **Container Storage**: Persistent storage for containerized applications

## Integration with AWS Services

### Amazon EC2
- **Multi-AZ Access**: Mount from instances in different AZs
- **Auto Scaling**: Shared storage across scaling instances
- **Spot Instances**: Persistent storage for spot workloads

### AWS Lambda
- **Shared Libraries**: Common code and dependencies
- **Data Processing**: Access to large datasets
- **Configuration**: Shared configuration files

### Amazon ECS/EKS
- **Persistent Volumes**: Container persistent storage
- **Shared Data**: Data sharing between containers
- **StatefulSets**: Kubernetes persistent volumes

### AWS Batch
- **Job Storage**: Shared input/output data
- **Scratch Space**: Temporary processing storage
- **Results**: Persistent job results

## Cost Optimization

### Storage Classes
- **Standard**: For frequently accessed data
- **IA (Infrequent Access)**: For data accessed <1 time per month
- **Lifecycle Policies**: Automatic transition to IA after 30 days

### File System Types
- **One Zone**: Up to 47% cost savings vs Regional
- **Regional**: Higher cost but better availability

### Throughput Modes
- **Elastic**: Pay for actual usage
- **Provisioned**: Pay for reserved throughput
- **Bursting**: Good for variable workloads

## Troubleshooting

### Common Issues
```bash
# Mount timeout issues
# Check security groups, NACLs, and DNS resolution

# Permission denied
# Verify IAM policies and POSIX permissions

# Performance issues
# Check throughput mode, file system size, and mount options

# Connection issues
# Verify mount target availability and network connectivity
```

### Diagnostic Commands
```bash
# Check mount status
mount | grep efs

# Test connectivity to mount target
telnet fs-12345678.efs.us-east-1.amazonaws.com 2049

# Monitor EFS performance
iostat -x 1

# Check EFS client logs
tail -f /var/log/amazon/efs/*
```

## Limits and Quotas

### File System Limits
- **Maximum file size**: 47.9 TiB
- **Maximum directory depth**: 1,000 levels
- **Maximum files per directory**: 50 million
- **Maximum file name length**: 255 bytes

### Performance Limits
- **General Purpose IOPS**: 7,000 operations/second
- **Max I/O IOPS**: >7,000 operations/second
- **Regional throughput**: Up to 20-60 GiBps read
- **One Zone throughput**: Up to 3 GiBps read/write

### Regional Limits
- **File systems per region**: 1,000 (can be increased)
- **Mount targets per AZ**: 1 per file system
- **Access points per file system**: 1,000

## Best Practices Summary

### Security
- **Enable encryption** at rest and in transit
- **Use IAM policies** for fine-grained access control
- **Implement POSIX permissions** for file-level security
- **Use VPC endpoints** for private connectivity

### Performance
- **Choose appropriate throughput mode** based on workload
- **Use EFS Utils** for better performance
- **Optimize mount options** for your use case
- **Monitor CloudWatch metrics** for performance insights

### Cost Management
- **Use lifecycle policies** to transition to IA storage
- **Choose One Zone** for non-critical workloads
- **Monitor usage** and optimize throughput provisioning
- **Clean up unused resources** regularly

### Reliability
- **Use Regional file systems** for critical data
- **Enable automatic backups** for data protection
- **Test restore procedures** regularly
- **Monitor file system health** with CloudWatch
