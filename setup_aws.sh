#!/bin/bash
echo "--- AWS Setup for Trending Dashboard ---"
echo "To run this stack, we need your AWS Credentials."
echo "These will be saved to local .env files only."

read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
read -p "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
read -p "AWS Region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

# 1. Update Worker .env
echo "Creating worker/.env..."
cat > worker/.env <<EOF
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
AWS_REGION=$AWS_REGION
EOF

# 2. Update Web .env.local
echo "Creating web/.env.local..."
cat > web/.env.local <<EOF
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
AWS_REGION=$AWS_REGION
EOF

# 3. Provision Table
echo "--- Provisioning DynamoDB Table ---"
cd worker
source venv/bin/activate
python provision_dynamo.py

if [ $? -eq 0 ]; then
    echo "--- Provisioning Success ---"
    echo "You can now run:"
    echo "  1. Worker: cd worker && python main.py"
    echo "  2. Web: cd web && npm run dev"
else
   echo "--- Provisioning Failed ---"
   echo "Check your credentials and try again."
fi
