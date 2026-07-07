# EC2 Fleet and Spot Fleet Cheatsheet

## Overview

EC2 Fleet and Spot Fleet are designed to launch a fleet of tens, hundreds, or thousands of Amazon EC2 instances in a single operation. Each instance in a fleet is configured by a launch template or a set of launch parameters that you configure manually at launch. Fleets provide features that maximize cost savings and optimize availability and performance when running applications on multiple EC2 instances. A fleet can launch multiple instance types, Availability Zones, and purchase options to increase flexibility and reduce costs.

```bash
# Create an EC2 Fleet
aws ec2 create-fleet \
  --launch-template-configs file://config.json \
  --target-capacity-specification TotalTargetCapacity=10,DefaultTargetCapacityType=on-demand

# Describe a fleet
aws ec2 describe-fleets --fleet-ids fleet-1234567890abcdef0

# Delete a fleet
aws ec2 delete-fleets --fleet-ids fleet-1234567890abcdef0 --terminate-instances
```

## Fleet Types

EC2 Fleet offers different types to suit various workload requirements. The `instant` type provisions capacity synchronously and is ideal for batch processing jobs that require immediate availability. The `maintain` type continuously maintains the target capacity and automatically replaces instances that are interrupted or terminated. The `request` type is a one-time request that doesn't maintain capacity after the initial launch. Choosing the right fleet type depends on whether you need persistent capacity or one-time batch processing.

```bash
# Create an instant fleet (synchronous, for batch jobs)
aws ec2 create-fleet \
  --fleet-type instant \
  --launch-template-configs file://config.json \
  --target-capacity-specification TotalTargetCapacity=100,DefaultTargetCapacityType=spot

# Create a maintain fleet (persistent capacity)
aws ec2 create-fleet \
  --fleet-type maintain \
  --launch-template-configs file://config.json \
  --target-capacity-specification TotalTargetCapacity=10,DefaultTargetCapacityType=on-demand

# Create a request fleet (one-time request)
aws ec2 create-fleet \
  --fleet-type request \
  --launch-template-configs file://config.json \
  --target-capacity-specification TotalTargetCapacity=50,DefaultTargetCapacityType=spot
```

## Launch Templates

Launch templates simplify fleet configuration by predefining instance parameters like instance type, AMI, key pair, and security groups. Using launch templates ensures consistency across fleet launches and makes it easier to update configurations. You can specify multiple launch template configurations in a single fleet to launch different instance types or configurations. Launch templates can be versioned, allowing you to track changes and roll back to previous configurations if needed.

```bash
# Create a launch template
aws ec2 create-launch-template \
  --launch-template-name my-template \
  --launch-template-data file://template-data.json

# Create a fleet using launch template
aws ec2 create-fleet \
  --launch-template-configs 'LaunchTemplateSpecification={LaunchTemplateId=lt-1234567890abcdef0,Version=1}' \
  --target-capacity-specification TotalTargetCapacity=10

# Use multiple launch template configurations
aws ec2 create-fleet \
  --launch-template-configs \
    'LaunchTemplateSpecification={LaunchTemplateId=lt-1234567890abcdef0,Version=1},Overrides={InstanceType=t2.micro}' \
    'LaunchTemplateSpecification={LaunchTemplateId=lt-1234567890abcdef0,Version=1},Overrides={InstanceType=t3.micro}'
```

## Target Capacity

Target capacity specifies the total number of units (instances, vCPUs, or memory units) that the fleet should maintain. You can specify the default target capacity type as on-demand, spot, or a combination of both. The fleet automatically provisions and maintains the requested capacity based on your configuration. You can also split capacity between on-demand and spot instances to optimize costs while maintaining availability for critical workloads.

```bash
# Specify target capacity with on-demand as default
aws ec2 create-fleet \
  --launch-template-configs file://config.json \
  --target-capacity-specification \
    TotalTargetCapacity=20,DefaultTargetCapacityType=on-demand,OnDemandTargetCapacity=10,SpotTargetCapacity=10

# Specify target capacity using vCPU units
aws ec2 create-fleet \
  --launch-template-configs file://config.json \
  --target-capacity-specification \
    TotalTargetCapacity=100,DefaultTargetCapacityType=spot,TargetCapacityUnitType=vcpu

# Specify target capacity using memory units
aws ec2 create-fleet \
  --launch-template-configs file://config.json \
  --target-capacity-specification \
    TotalTargetCapacity=1000,DefaultTargetCapacityType=on-demand,TargetCapacityUnitType=memory-mib
```

## Instance Types and Overrides

Fleets can launch multiple instance types to avoid dependency on any single instance type availability. You can specify instance type overrides to launch different instance types within the same fleet. This flexibility increases overall availability and allows the fleet to adapt to capacity constraints. Overrides can also specify weighted capacities, subnet placement, and availability zone preferences for fine-grained control over instance placement.

```bash
# Create fleet with multiple instance type overrides
aws ec2 create-fleet \
  --launch-template-configs \
    'LaunchTemplateSpecification={LaunchTemplateId=lt-1234567890abcdef0},Overrides=[{InstanceType=t2.micro,WeightedCapacity=1},{InstanceType=t3.micro,WeightedCapacity=2}]' \
  --target-capacity-specification TotalTargetCapacity=10

# Specify availability zone in overrides
aws ec2 create-fleet \
  --launch-template-configs \
    'LaunchTemplateSpecification={LaunchTemplateId=lt-1234567890abcdef0},Overrides={InstanceType=t2.micro,AvailabilityZone=us-east-1a}' \
  --target-capacity-specification TotalTargetCapacity=5

# Specify subnet in overrides
aws ec2 create-fleet \
  --launch-template-configs \
    'LaunchTemplateSpecification={LaunchTemplateId=lt-1234567890abcdef0},Overrides={InstanceType=t2.micro,SubnetId=subnet-1234567890abcdef0}' \
  --target-capacity-specification TotalTargetCapacity=10
```

## Spot Instance Configuration

Spot Instances offer significant cost savings compared to On-Demand instances but can be interrupted with short notice. Fleets can automatically request replacement Spot capacity if your Spot Instances are interrupted. Capacity Rebalancing allows fleets to proactively replace Spot Instances that are at elevated risk of interruption. You can configure Spot allocation strategies like `lowest-price` or `capacity-optimized` to optimize for cost or availability.

```bash
# Create fleet with Spot Instances using lowest-price strategy
aws ec2 create-fleet \
  --launch-template-configs file://config.json \
  --spot-options SingleAvailabilityZone=false,SingleInstanceType=false \
  --target-capacity-specification TotalTargetCapacity=50,DefaultTargetCapacityType=spot

# Create fleet with capacity-optimized Spot strategy
aws ec2 create-fleet \
  --launch-template-configs file://config.json \
  --spot-options AllocationStrategy=capacity-optimized \
  --target-capacity-specification TotalTargetCapacity=30,DefaultTargetCapacityType=spot

# Enable capacity rebalancing for Spot Instances
aws ec2 create-fleet \
  --launch-template-configs file://config.json \
  --spot-options AllocationStrategy=capacity-optimized,InstanceInterruptionBehavior=terminate \
  --target-capacity-specification TotalTargetCapacity=20,DefaultTargetCapacityType=spot
```

## On-Demand Configuration

On-Demand Instances provide predictable pricing and guaranteed availability for critical workloads. Fleets can use On-Demand Capacity Reservations to reserve capacity in advance for your most demanding applications. You can combine On-Demand Instances with Reserved Instances and Savings Plans to maximize cost savings. The fleet automatically provisions On-Demand capacity when Spot capacity is unavailable or when specified by your capacity allocation strategy.

```bash
# Create fleet with On-Demand Capacity Reservation
aws ec2 create-fleet \
  --launch-template-configs file://config.json \
  --on-demand-options AllocationStrategy=lowest-price \
  --target-capacity-specification TotalTargetCapacity=10,DefaultTargetCapacityType=on-demand

# Use On-Demand with Capacity Reservation
aws ec2 create-fleet \
  --launch-template-configs file://config.json \
  --on-demand-options CapacityReservationOptions={UsagePreference=use-capacity-reservations-first} \
  --target-capacity-specification TotalTargetCapacity=5,DefaultTargetCapacityType=on-demand
```

## Monitoring and Management

Fleets provide monitoring capabilities to track fleet status, instance health, and capacity utilization. You can use CloudWatch metrics and events to monitor fleet performance and receive alerts on capacity changes. Fleet status indicates whether the fleet is submitted, active, deleted_terminating, deleted_terminating_instances, deleted_terminated, or failed. Understanding fleet states helps in troubleshooting and capacity planning.

```bash
# Describe fleet status
aws ec2 describe-fleets --fleet-ids fleet-1234567890abcdef0

# Describe fleet instances
aws ec2 describe-fleet-instances --fleet-id fleet-1234567890abcdef0

# Monitor fleet with CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2Spot \
  --metric-name FleetUtilization \
  --dimensions Name=FleetRequestId,Value=fleet-1234567890abcdef0 \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Average
```

## Modifying Fleets

You can modify existing fleets to adjust target capacity, change allocation strategies, or update launch template configurations. Modifying a fleet allows you to respond to changing workload demands without deleting and recreating the fleet. Changes to target capacity are applied immediately, while changes to launch template configurations may require instance replacement. Understanding how modifications affect running instances is important for maintaining application availability.

```bash
# Modify fleet target capacity
aws ec2 modify-fleet \
  --fleet-id fleet-1234567890abcdef0 \
  --target-capacity-specification TotalTargetCapacity=20

# Modify fleet spot options
aws ec2 modify-fleet \
  --fleet-id fleet-1234567890abcdef0 \
  --spot-options AllocationStrategy=capacity-optimized

# Modify fleet on-demand options
aws ec2 modify-fleet \
  --fleet-id fleet-1234567890abcdef0 \
  --on-demand-options AllocationStrategy=prioritized
```

## Common Fleet Use Cases

EC2 Fleets are commonly used for batch processing, big data workloads, container orchestration, and web serving. Batch processing jobs benefit from instant fleets that provision capacity synchronously for job completion. Web serving applications use maintain fleets to ensure consistent capacity across peak and off-peak hours. Big data workloads leverage spot instances for cost-effective scaling of compute-intensive tasks. Understanding your use case helps in selecting the appropriate fleet type and configuration.

```bash
# Batch processing fleet (instant type)
aws ec2 create-fleet \
  --fleet-type instant \
  --launch-template-configs file://batch-config.json \
  --target-capacity-specification TotalTargetCapacity=100,DefaultTargetCapacityType=spot

# Web serving fleet (maintain type)
aws ec2 create-fleet \
  --fleet-type maintain \
  --launch-template-configs file://web-config.json \
  --target-capacity-specification TotalTargetCapacity=10,DefaultTargetCapacityType=on-demand

# Big data fleet (spot optimized)
aws ec2 create-fleet \
  --fleet-type maintain \
  --launch-template-configs file://data-config.json \
  --spot-options AllocationStrategy=capacity-optimized \
  --target-capacity-specification TotalTargetCapacity=50,DefaultTargetCapacityType=spot
```

## Common EC2 Fleet Commands

| Command | Description |
|---------|-------------|
| `create-fleet` | Create a new EC2 Fleet |
| `describe-fleets` | List or describe fleets |
| `describe-fleet-instances` | List instances in a fleet |
| `modify-fleet` | Modify fleet configuration |
| `delete-fleets` | Delete fleets and optionally terminate instances |
| `create-launch-template` | Create a launch template for fleet use |
| `describe-launch-templates` | List available launch templates |
