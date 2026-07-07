# AWS CloudShell Cheatsheet

## Getting Started

AWS CloudShell is a browser-based, pre-authenticated shell that you can launch directly from the AWS Management Console. You can run AWS CLI commands using your preferred shell such as Bash, PowerShell, or Z shell without downloading or installing command line tools. The compute environment is based on Amazon Linux 2023 and includes pre-installed development tools. CloudShell provides persistent storage up to 1 GB per region at no additional cost.

```bash
# Launch CloudShell from AWS Console
# Click the CloudShell icon in the console toolbar
# Or navigate to: https://console.aws.amazon.com/cloudshell/

# Check your current shell
echo $SHELL

# Switch to different shells
bash    # Switch to Bash
zsh     # Switch to Z shell
pwsh    # Switch to PowerShell
```

## Shells and Languages

CloudShell supports multiple command line shells and programming languages out of the box. You can switch seamlessly between Bash, PowerShell, and Z shell based on your preference. The environment includes pre-installed tools like git, make, pip, vim, tmux, and wget. Popular languages such as Node.js, Python, and .NET Core are pre-configured, allowing you to run projects without runtime installations.

```bash
# Check available Python version
python --version
python3 --version

# Check Node.js version
node --version
npm --version

# Check git version
git --version

# Check available shells
which bash zsh pwsh
```

## File Management

CloudShell provides persistent storage in your home directory ($HOME) that persists between sessions. You can upload and download files directly through the CloudShell interface or use command-line tools. The storage is private to you and available across CloudShell sessions in the same AWS region. Files in the home directory are retained even when the shell session ends.

```bash
# Navigate to home directory
cd ~
pwd

# List files
ls -la

# Create directories
mkdir myproject
cd myproject

# Upload files (via CloudShell UI)
# Actions -> Upload file

# Download files (via CloudShell UI)
# Select file -> Actions -> Download file
```

## AWS CLI Commands

CloudShell comes pre-authenticated with your AWS console credentials, so you can run AWS CLI commands without additional configuration. The AWS CLI version 2 is pre-installed and ready to use immediately. Your console permissions are automatically applied to CLI commands, providing seamless access to AWS services. This eliminates the need to manage access keys or configure profiles.

```bash
# List S3 buckets
aws s3 ls

# Describe EC2 instances
aws ec2 describe-instances

# List IAM users
aws iam list-users

# Get current region
aws configure get region

# Get current account ID
aws sts get-caller-identity
```

## Environment Customization

You can customize your CloudShell experience by installing additional software and modifying shell configurations. The environment supports package installation through package managers like yum, pip, and npm. You can also create shell initialization scripts to set up your preferred environment automatically. Customizations persist across sessions when stored in your home directory.

```bash
# Install packages using yum
sudo yum install package-name

# Install Python packages
pip install package-name
pip3 install package-name

# Install Node.js packages globally
sudo npm install -g package-name

# Edit bash profile for persistent customization
vim ~/.bashrc

# Edit zsh profile
vim ~/.zshrc

# Reload shell configuration
source ~/.bashrc
```

## Session Management

CloudShell sessions are automatically managed to optimize resource usage and security. Inactive sessions are stopped after a period of inactivity, and long-running sessions are recycled automatically. Safe Paste is enabled by default to protect against malicious scripts when pasting multiline text. You can manage multiple tabs and customize the interface layout to suit your workflow.

```bash
# Check session information
whoami
hostname

# Check disk usage
df -h

# Check memory usage
free -h

# Check running processes
ps aux

# Clear terminal
clear

# Exit session
exit
```

## VPC Environments

CloudShell VPC environments allow you to create a shell environment within your own VPC for enhanced network isolation. You can assign a VPC, subnet, and security groups to control network access. This feature enables CloudShell to interact with private resources in your VPC securely. VPC environments do not include persistent storage and are deleted after timeout or manual deletion.

```bash
# Check VPC environment status (if applicable)
# This is configured through the CloudShell UI
# Settings -> VPC environment settings

# Test VPC connectivity
ping private-resource-ip

# Check network interfaces
ip addr show
```

## Security Features

CloudShell includes several security features to protect your environment and data. IAM policies control which users can access CloudShell and what actions they can perform. Shell sessions have automatic restrictions to prevent resource abuse. Safe Paste requires verification before executing multiline pasted content to prevent script injection. These features work together to provide a secure shell environment.

```bash
# Check current user permissions
aws iam get-user-policy --user-name $(whoami) --policy-name policy-name

# Verify IAM permissions
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::ACCOUNT-ID:user/USERNAME --action-names "s3:ListBucket"

# Safe Paste is automatic in the UI
# When pasting multiline text, verify the content before execution
```

## Common CloudShell Actions

| Action | Description |
|--------|-------------|
| Launch CloudShell | Click CloudShell icon in AWS Console |
| Switch Shells | Use `bash`, `zsh`, or `pwsh` commands |
| Upload Files | Actions → Upload file in CloudShell UI |
| Download Files | Select file → Actions → Download |
| Install Packages | Use `yum`, `pip`, or `npm` |
| Check Region | `aws configure get region` |
| Persistent Storage | Files in `$HOME` persist between sessions |
| VPC Environment | Configure in CloudShell Settings |
