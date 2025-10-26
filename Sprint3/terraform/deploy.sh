#!/bin/bash

# Deploy script for the microservices project
# This script handles the deployment workflow

set -e  # Exit on any error

echo "🚀 Starting deployment process..."

# Check if we're in the right directory
if [ ! -d "stacks/apps" ]; then
    echo "❌ Error: This script should be run from the terraform directory"
    exit 1
fi

# Initialize Terraform if needed
if [ ! -d "stacks/apps/.terraform" ]; then
    echo "📋 Initializing Terraform..."
    cd stacks/apps && terraform init -upgrade
    cd ../..
fi

# Plan the deployment
echo "📋 Planning Terraform deployment..."
cd stacks/apps
terraform plan -var-file="../../environments/student/apps/terraform.tfvars"

# Apply the configuration
echo "🏗️  Applying Terraform configuration..."
terraform apply -auto-approve -var-file="../../environments/student/apps/terraform.tfvars"

echo "✅ Deployment completed successfully!"
