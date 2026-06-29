# AWS IAM Cheatsheet

## Users

IAM users represent people or applications that interact with AWS services. Each user has unique security credentials and can be assigned permissions through policies or group membership. Users can sign in to the AWS Management Console or make API calls using their access keys. Managing users individually allows for granular control over permissions and access.

```bash
# Create a new IAM user
aws iam create-user --user-name username

# List all IAM users
aws iam list-users

# Delete an IAM user
aws iam delete-user --user-name username

# Add user to a group
aws iam add-user-to-group --group-name groupname --user-name username

# Remove user from a group
aws iam remove-user-from-group --group-name groupname --user-name username
```

## Groups

IAM groups are collections of users that share similar permission requirements. Instead of attaching policies to individual users, you can attach them to groups for easier management. When a user is added to a group, they automatically inherit all permissions assigned to that group. Groups simplify permission management and ensure consistent access control across teams.

```bash
# Create a new IAM group
aws iam create-group --group-name groupname

# List all IAM groups
aws iam list-groups

# Delete an IAM group
aws iam delete-group --group-name groupname

# List users in a group
aws iam get-group --group-name groupname
```

## Roles

IAM roles are similar to users but are not associated with a specific person or have permanent credentials. Roles are used to grant temporary permissions to AWS services, applications, or users from other accounts. Roles define trust policies that specify who can assume the role and permission policies that define what actions the assumed identity can perform. Roles are essential for cross-account access and service-to-service authentication.

```bash
# Create a new IAM role
aws iam create-role --role-name rolename --assume-role-policy-document file://trust-policy.json

# List all IAM roles
aws iam list-roles

# Delete an IAM role
aws iam delete-role --role-name rolename

# Attach a policy to a role
aws iam attach-role-policy --role-name rolename --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

## Policies

IAM policies are JSON documents that define permissions for IAM identities and resources. Policies specify which AWS services and actions are allowed or denied, and can include conditions for fine-grained access control. Managed policies are standalone entities that can be attached to multiple identities, while inline policies are embedded directly into a user, group, or role. Policies follow the principle of least privilege by granting only necessary permissions.

```bash
# Create a managed policy
aws iam create-policy --policy-name policyname --policy-document file://policy.json

# List all managed policies
aws iam list-policies

# Attach a policy to a user
aws iam attach-user-policy --user-name username --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Detach a policy from a user
aws iam detach-user-policy --user-name username --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# List policies attached to a user
aws iam list-attached-user-policies --user-name username
```

## Access Keys

Access keys consist of an access key ID and a secret access key used to sign programmatic requests to AWS. These credentials allow users and applications to interact with AWS services through the API, CLI, or SDKs instead of the console. Each user can have up to two access keys, and it's important to rotate them regularly for security. Access keys should never be shared or embedded in code; use IAM roles for applications running on AWS.

```bash
# Create access key for a user
aws iam create-access-key --user-name username

# List access keys for a user
aws iam list-access-keys --user-name username

# Delete an access key
aws iam delete-access-key --access-key-id AKIAIOSFODNN7EXAMPLE --user-name username
```

## Instance Profiles

Instance profiles are containers for IAM roles that can be attached to EC2 instances. When an EC2 instance launches with an instance profile, applications running on that instance can assume the associated role to access AWS resources. This eliminates the need to store long-term credentials on the instance. Instance profiles provide a secure way to grant permissions to applications running on EC2.

```bash
# Create an instance profile
aws iam create-instance-profile --instance-profile-name profilename

# Add a role to an instance profile
aws iam add-role-to-instance-profile --instance-profile-name profilename --role-name rolename

# List instance profiles
aws iam list-instance-profiles
```

## Account Management

Account management includes tasks like setting up account aliases for easier console access and managing password policies. The account alias creates a friendly URL for signing in to the AWS Management Console. You can also retrieve account summary information to understand the resource limits and usage across your AWS account. These management tasks help maintain security and provide visibility into your IAM configuration.

```bash
# Create account alias
aws iam create-account-alias --account-alias my-alias

# List account aliases
aws iam list-account-aliases

# Get account summary
aws iam get-account-summary
```

## Policy Document Examples

Policy documents define the permissions structure using JSON with specific version and statement formats. The example policies demonstrate common patterns like granting read-only access to S3 or defining trust relationships for EC2 services. These templates can be customized to fit your specific security requirements and access patterns. Understanding policy syntax is crucial for implementing effective least privilege access controls.

### S3 Read-Only Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:Get*",
        "s3:List*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Trust Policy for EC2
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

## Common IAM Actions

IAM actions are specific permissions that can be granted or denied through policies. These actions correspond to API operations and control what users and roles can do within your AWS account. The table below lists frequently used actions for common IAM operations. Understanding these actions helps you construct precise policies that grant exactly the permissions needed.

| Action | Description |
|--------|-------------|
| `iam:CreateUser` | Create a new IAM user |
| `iam:DeleteUser` | Delete an IAM user |
| `iam:AttachUserPolicy` | Attach a managed policy to a user |
| `iam:CreateRole` | Create a new IAM role |
| `iam:PassRole` | Pass a role to an AWS service |
| `iam:GetRole` | Retrieve information about a role |
| `iam:ListRoles` | List all roles in the account |
