# Amazon EBS (Elastic Block Store) Cheat Sheet

## Overview

Amazon Elastic Block Store (EBS) provides scalable, high-performance block storage resources for use with Amazon EC2 instances. EBS volumes function like raw, unformatted block devices that can be mounted as devices on instances.

## Key Concepts

### EBS Volumes
- **Definition**: Storage volumes that attach to EC2 instances
- **Usage**: Function like local hard drives for file storage and application installation
- **Persistence**: Data persists independently of instance lifecycle
- **Attachment**: Can be attached/detached from instances dynamically

### EBS Snapshots
- **Definition**: Point-in-time backups of EBS volumes
- **Persistence**: Stored independently from the original volume
- **Restoration**: Can restore new volumes from snapshots
- **Cross-region**: Can copy snapshots across AWS regions and accounts

## Volume Types

### SSD-Backed Storage (Transactional Workloads)

#### General Purpose SSD (gp3)
- **Use Case**: Balanced price/performance for most workloads
- **Size**: 1 GiB - 16 TiB
- **IOPS**: 3,000-16,000 IOPS (baseline 3,000)
- **Throughput**: 125-1,000 MiB/s (baseline 125 MiB/s)

#### General Purpose SSD (gp2)
- **Use Case**: Previous generation general purpose
- **Size**: 1 GiB - 16 TiB
- **IOPS**: 100-16,000 IOPS (3 IOPS per GiB, min 100)
- **Throughput**: Up to 250 MiB/s

#### Provisioned IOPS SSD (io2)
- **Use Case**: High-performance, mission-critical workloads
- **Size**: 4 GiB - 16 TiB
- **IOPS**: 100-64,000 IOPS
- **Durability**: 99.999% (0.001% annual failure rate)

#### Provisioned IOPS SSD (io2 Block Express)
- **Use Case**: Highest performance SSD for large, critical workloads
- **Size**: 4 GiB - 64 TiB
- **IOPS**: 100-256,000 IOPS
- **Throughput**: Up to 4,000 MiB/s

#### Provisioned IOPS SSD (io1)
- **Use Case**: Previous generation high-performance SSD
- **Size**: 4 GiB - 16 TiB
- **IOPS**: 100-64,000 IOPS

### HDD-Backed Storage (Throughput Intensive Workloads)

#### Throughput Optimized HDD (st1)
- **Use Case**: Big data, data warehouses, log processing
- **Size**: 125 GiB - 16 TiB
- **Throughput**: Up to 500 MiB/s
- **Cannot**: Be used as boot volume

#### Cold HDD (sc1)
- **Use Case**: Infrequently accessed data, lowest cost
- **Size**: 125 GiB - 16 TiB
- **Throughput**: Up to 250 MiB/s
- **Cannot**: Be used as boot volume

## Common AWS CLI Commands

### Volume Management
```bash
# List all volumes
aws ec2 describe-volumes

# Create a volume
aws ec2 create-volume \
    --size 20 \
    --volume-type gp3 \
    --availability-zone us-east-1a

# Attach volume to instance
aws ec2 attach-volume \
    --volume-id vol-12345678 \
    --instance-id i-87654321 \
    --device /dev/sdf

# Detach volume
aws ec2 detach-volume --volume-id vol-12345678

# Delete volume
aws ec2 delete-volume --volume-id vol-12345678

# Modify volume (resize/change type)
aws ec2 modify-volume \
    --volume-id vol-12345678 \
    --size 30 \
    --volume-type gp3
```

### Snapshot Management
```bash
# Create snapshot
aws ec2 create-snapshot \
    --volume-id vol-12345678 \
    --description "My snapshot"

# List snapshots
aws ec2 describe-snapshots --owner-ids self

# Create volume from snapshot
aws ec2 create-volume \
    --snapshot-id snap-12345678 \
    --availability-zone us-east-1a

# Copy snapshot to another region
aws ec2 copy-snapshot \
    --source-region us-east-1 \
    --source-snapshot-id snap-12345678 \
    --destination-region us-west-2

# Delete snapshot
aws ec2 delete-snapshot --snapshot-id snap-12345678
```

### Encryption
```bash
# Create encrypted volume
aws ec2 create-volume \
    --size 20 \
    --volume-type gp3 \
    --availability-zone us-east-1a \
    --encrypted

# Create encrypted volume with custom KMS key
aws ec2 create-volume \
    --size 20 \
    --volume-type gp3 \
    --availability-zone us-east-1a \
    --encrypted \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012
```

## Key Features

### Elastic Volumes
- **Dynamic Scaling**: Increase size, change volume type, or adjust IOPS without downtime
- **Live Modification**: Changes applied while volume is in use
- **File System Extension**: May require OS-level commands to extend file system

### Multi-Attach
- **Availability**: Only for io1 and io2 volume types
- **Limitation**: Up to 16 Nitro-based instances in same AZ
- **Use Case**: Shared storage for clustered applications

### EBS Encryption
- **Data-at-Rest**: Encrypts data stored on volume
- **Data-in-Transit**: Encrypts data between instance and volume
- **Snapshots**: Encrypted volumes create encrypted snapshots
- **Key Management**: Uses AWS KMS for key management

### Fast Snapshot Restore (FSR)
- **Purpose**: Eliminates performance penalty when restoring from snapshots
- **Cost**: Additional charges apply
- **Availability**: Per-AZ basis

## Performance Optimization

### IOPS vs Throughput
- **IOPS**: Input/Output Operations Per Second (small, random I/O)
- **Throughput**: Amount of data transferred per second (large, sequential I/O)
- **Balance**: Choose volume type based on workload characteristics

### Instance Types
- **EBS-Optimized**: Dedicated bandwidth for EBS traffic
- **Nitro System**: Better performance and more features
- **Placement Groups**: Cluster placement for low latency

## Monitoring and Troubleshooting

### CloudWatch Metrics
```bash
# Key metrics to monitor:
# - VolumeReadOps/VolumeWriteOps
# - VolumeReadBytes/VolumeWriteBytes
# - VolumeTotalReadTime/VolumeTotalWriteTime
# - VolumeQueueLength
# - BurstBalance (for gp2 volumes)
```

### Common Issues
- **Performance**: Check IOPS/throughput limits, instance type capabilities
- **Attachment**: Verify AZ matching between volume and instance
- **Encryption**: Cannot attach encrypted volume to unsupported instance types

## Best Practices

### Security
- **Encryption**: Enable encryption for sensitive data
- **IAM Policies**: Use least privilege access
- **Snapshot Sharing**: Be cautious when sharing snapshots

### Performance
- **Pre-warming**: Initialize volumes restored from snapshots for consistent performance
- **RAID**: Consider RAID 0 for increased performance (with trade-offs)
- **Instance Types**: Use EBS-optimized instances

### Cost Optimization
- **Volume Types**: Choose appropriate type for workload
- **Snapshot Lifecycle**: Automate snapshot deletion with DLM
- **Unused Volumes**: Regularly audit and delete unused volumes
- **Snapshot Archive**: Use EBS Snapshots Archive for long-term retention

### Backup and Recovery
- **Regular Snapshots**: Automate with Amazon Data Lifecycle Manager
- **Cross-Region**: Copy critical snapshots to other regions
- **Testing**: Regularly test restore procedures

## Related Services

- **Amazon EC2**: Compute instances that use EBS volumes
- **AWS KMS**: Encryption key management
- **Amazon Data Lifecycle Manager**: Automated backup management
- **EBS Direct APIs**: Direct snapshot access for backup solutions
- **Recycle Bin**: Recovery of accidentally deleted snapshots and AMIs

## Pricing Considerations

- **Volume Storage**: Charged per GB-month provisioned
- **IOPS**: Additional charges for provisioned IOPS (io1/io2)
- **Snapshots**: Charged for actual data stored (incremental)
- **Data Transfer**: Cross-AZ and cross-region transfers
- **Fast Snapshot Restore**: Additional per-snapshot, per-AZ charges

## Limits and Quotas

- **Volume Size**: Up to 64 TiB (io2 Block Express), 16 TiB (others)
- **Attachments**: Most volumes attach to single instance (except Multi-Attach)
- **Snapshots**: No limit on number of snapshots
- **Regional**: Volumes and instances must be in same AZ
