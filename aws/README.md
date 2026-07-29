# AWS Knowledge Base

This directory contains concise cheat sheets and reference guides for various AWS services. Each service has its own markdown file with practical examples and common operations.

## Table of Contents

- [IAM (Identity and Access Management)](#iam-identity-and-access-management)
- [CloudShell](#cloudshell)
- [EC2 Security Groups](#ec2-security-groups)
- [EC2 Fleet and Spot Fleet](#ec2-fleet-and-spot-fleet)
- [EC2 Elastic Network Interfaces](#ec2-elastic-network-interfaces)
- [EBS (Elastic Block Store)](#ebs-elastic-block-store)
- [EFS (Elastic File System)](#efs-elastic-file-system)
- [EBS vs EFS: When to Use Which Storage Solution](#ebs-vs-efs-when-to-use-which-storage-solution)

---

## IAM (Identity and Access Management)

AWS Identity and Access Management (IAM) is a web service that helps you securely control access to AWS resources. With IAM, you can manage permissions that control which AWS resources users can access. You use IAM to control who is authenticated (signed in) and authorized (has permissions) to use resources. IAM provides the infrastructure necessary to control authentication and authorization for your AWS accounts.

**See:** [IAM Cheatsheet](./iam-cheatsheet.md)

---

## CloudShell

AWS CloudShell is a browser-based, pre-authenticated shell that you can launch directly from the AWS Management Console. You can run AWS CLI commands using your preferred shell such as Bash, PowerShell, or Z shell without downloading or installing command line tools. The compute environment is based on Amazon Linux 2023 and includes pre-installed development tools. CloudShell provides persistent storage up to 1 GB per region at no additional cost.

**See:** [CloudShell Cheatsheet](./cloudshell-cheatsheet.md)

---

## EC2 Security Groups

EC2 security groups act as virtual firewalls for your EC2 instances to control incoming and outgoing traffic. Inbound rules control the incoming traffic to your instance, and outbound rules control the outgoing traffic from your instance. Security groups are stateful, meaning if you send a request from your instance, the response traffic is allowed to flow in regardless of inbound rules. You can associate each instance with multiple security groups, and each security group with multiple instances. Rules are automatically applied to all instances associated with the security group.

**See:** [EC2 Security Groups Cheatsheet](./ec2-security-groups-cheatsheet.md)

---

## EC2 Fleet and Spot Fleet

EC2 Fleet and Spot Fleet are designed to launch a fleet of tens, hundreds, or thousands of Amazon EC2 instances in a single operation. Each instance in a fleet is configured by a launch template or a set of launch parameters that you configure manually at launch. Fleets provide features that maximize cost savings and optimize availability and performance when running applications on multiple EC2 instances. A fleet can launch multiple instance types, Availability Zones, and purchase options to increase flexibility and reduce costs.

**See:** [EC2 Fleet and Spot Fleet Cheatsheet](./ec2-fleets-cheatsheet.md)

---

## EC2 Elastic Network Interfaces

Elastic network interfaces are logical networking components in a VPC that represent virtual network cards. You can create and configure network interfaces and attach them to instances in the same Availability Zone. The attributes of a network interface follow it as it's attached or detached from an instance and reattached to another instance. When you move a network interface from one instance to another, network traffic is redirected from the original instance to the new instance.

**See:** [EC2 Elastic Network Interfaces Cheatsheet](./ec2-eni-cheatsheet.md)

---

## EBS (Elastic Block Store)

Amazon Elastic Block Store (EBS) provides scalable, high-performance block storage resources for use with Amazon EC2 instances. EBS volumes function like raw, unformatted block devices that can be mounted as devices on instances. With EBS, you can create storage volumes and attach them to EC2 instances, use them like local hard drives, create point-in-time snapshots for backup and recovery, and dynamically scale storage capacity and performance without downtime.

**See:** [EBS Cheatsheet](./ebs-cheatsheet.md)

---

## EFS (Elastic File System)

Amazon Elastic File System (EFS) provides serverless, fully elastic file storage that scales automatically as you add and remove files. EFS supports the Network File System version 4 (NFSv4.1 and NFSv4.0) protocol and can be accessed concurrently from multiple AWS compute services including EC2, ECS, EKS, Lambda, and Fargate. The service offers Regional and One Zone file system types with different performance modes and throughput options to meet various workload requirements.

**See:** [EFS Cheatsheet](./efs-cheatsheet.md)

---

## EBS vs EFS: When to Use Which Storage Solution

### Quick Comparison

| Feature | EBS (Elastic Block Store) | EFS (Elastic File System) |
|---------|---------------------------|----------------------------|
| **Storage Type** | Block storage | File storage (NFS) |
| **Access Pattern** | Single EC2 instance (except Multi-Attach) | Multiple instances concurrently |
| **Protocol** | Raw block device | NFSv4.1/NFSv4.0 |
| **Scalability** | Manual scaling (Elastic Volumes) | Automatic scaling |
| **Performance** | High IOPS, low latency | Good throughput, higher latency |
| **Durability** | 99.999% - 99.8% (varies by type) | 99.999999999% (11 9s) |
| **Use Cases** | Databases, file systems, boot volumes | Shared storage, content management |

### When to Use EBS

#### **Database Storage**
- **Primary databases** (MySQL, PostgreSQL, Oracle)
- **NoSQL databases** (MongoDB, Cassandra)
- **Data warehouses** requiring high IOPS
- **Reason**: Low latency, high IOPS, consistent performance

#### **Operating System and Boot Volumes**
- **Root volumes** for EC2 instances
- **System drives** requiring fast boot times
- **Application installations** needing local storage performance
- **Reason**: Direct attachment, fastest access, required for boot

#### **High-Performance Computing (HPC)**
- **Scientific simulations** requiring fast I/O
- **Financial modeling** with intensive calculations
- **Real-time analytics** needing low latency
- **Reason**: Predictable performance, high IOPS capabilities

#### **Single-Instance Applications**
- **Legacy applications** not designed for shared storage
- **Monolithic applications** with local storage dependencies
- **Development environments** for individual developers
- **Reason**: Simple attachment model, no sharing complexity

#### **Backup and Archival (with Snapshots)**
- **Point-in-time backups** of critical data
- **Disaster recovery** across regions
- **Compliance archiving** with specific retention needs
- **Reason**: Snapshot functionality, cross-region replication

### When to Use EFS

#### **Web Content and Media Serving**
- **Content management systems** (WordPress, Drupal)
- **Media libraries** shared across web servers
- **Static website assets** for load-balanced applications
- **Reason**: Multiple web servers can access same content simultaneously

#### **Shared Application Data**
- **Configuration files** shared across environments
- **Application logs** centralized from multiple instances
- **Shared libraries** and common code repositories
- **Reason**: Concurrent access, automatic scaling, POSIX compliance

#### **Container and Microservices Storage**
- **Kubernetes persistent volumes** for stateful applications
- **Docker container shared storage** across hosts
- **Microservices** needing shared configuration or data
- **Reason**: Multi-mount capability, container orchestration support

#### **Big Data and Analytics**
- **Data lakes** for analytics workloads
- **ETL processing** with shared input/output data
- **Machine learning** training data accessible from multiple instances
- **Reason**: Petabyte scaling, concurrent access from multiple compute nodes

#### **Development and Testing**
- **Shared development environments** for teams
- **CI/CD pipelines** with shared artifacts
- **Testing environments** needing consistent data sets
- **Reason**: Easy sharing, automatic scaling, cost-effective for variable workloads

#### **Backup and Disaster Recovery**
- **Centralized backup destination** from multiple sources
- **Cross-region replication** for disaster recovery
- **Long-term archival** with lifecycle policies
- **Reason**: Automatic scaling, built-in replication, lifecycle management

### Hybrid Use Cases

#### **Database with Shared Storage Needs**
- **EBS**: Primary database storage (high performance)
- **EFS**: Backup destination, shared configuration files
- **Example**: MySQL on EBS with backups stored on EFS

#### **Web Applications**
- **EBS**: Operating system, application binaries, local cache
- **EFS**: User uploads, shared content, session data
- **Example**: E-commerce site with product images on EFS

#### **Analytics Workloads**
- **EBS**: High-performance scratch space for processing
- **EFS**: Input data sets, results storage, shared libraries
- **Example**: Spark cluster with input data on EFS, temp processing on EBS

### Decision Framework

#### Choose EBS When:
- ✅ **Single instance access** is sufficient
- ✅ **High IOPS** and low latency are critical
- ✅ **Predictable performance** is required
- ✅ **Boot volumes** or system drives are needed
- ✅ **Database storage** requiring consistent performance
- ✅ **Legacy applications** not supporting shared storage

#### Choose EFS When:
- ✅ **Multiple instances** need concurrent access
- ✅ **Automatic scaling** is preferred over manual management
- ✅ **Shared storage** across applications or services
- ✅ **POSIX file system** semantics are required
- ✅ **Variable workloads** with unpredictable storage needs
- ✅ **Cost optimization** for infrequently accessed data (IA storage class)

### Cost Considerations

#### EBS Cost Factors
- **Storage provisioned** (pay for allocated space)
- **IOPS provisioned** (io1/io2 volumes)
- **Snapshot storage** (incremental backups)
- **Data transfer** (cross-AZ)

#### EFS Cost Factors
- **Storage used** (pay for actual usage)
- **Throughput mode** (Elastic vs Provisioned)
- **Storage class** (Standard vs IA)
- **Access charges** (for IA storage class)

### Performance Comparison

#### EBS Performance Characteristics
- **Latency**: ~1ms (optimized for low latency)
- **IOPS**: Up to 256,000 (io2 Block Express)
- **Throughput**: Up to 4,000 MiB/s
- **Consistency**: Predictable, dedicated performance

#### EFS Performance Characteristics
- **Latency**: ~1ms+ (network overhead)
- **IOPS**: Up to 250,000+ (with Elastic throughput)
- **Throughput**: Up to 20-60 GiBps (Regional)
- **Consistency**: Variable based on concurrent access

### Migration Considerations

#### Moving from EBS to EFS
- **Assess concurrency needs**: Multiple instance access requirements
- **Application compatibility**: NFS protocol support
- **Performance requirements**: Latency sensitivity analysis
- **Cost analysis**: Usage patterns and storage class optimization

#### Moving from EFS to EBS
- **Single instance requirement**: Eliminate shared access needs
- **Performance optimization**: Need for higher IOPS or lower latency
- **Application constraints**: Block device requirements
- **Snapshot needs**: Point-in-time backup requirements
