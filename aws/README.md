# AWS Knowledge Base

This directory contains concise cheat sheets and reference guides for various AWS services. Each service has its own markdown file with practical examples and common operations.

## Table of Contents

- [IAM (Identity and Access Management)](#iam-identity-and-access-management)
- [CloudShell](#cloudshell)
- [EC2 Security Groups](#ec2-security-groups)
- [EC2 Fleet and Spot Fleet](#ec2-fleet-and-spot-fleet)

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
