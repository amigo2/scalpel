#!/usr/bin/env bash
set -euo pipefail

# --- CONFIGURATION — override via env if you like ---
AWS_PROFILE=${AWS_PROFILE:-bistro_agent}
AWS_REGION=${AWS_REGION:-eu-west-2}
ECR_URI=${ECR_URI:-929423420164.dkr.ecr.eu-west-2.amazonaws.com/scalpel}
LAMBDA_NAME=${LAMBDA_NAME:-scalpel-backend}

# --- 1. Build the image for Lambda (amd64 + classic v2 manifest) ---
# Enable BuildKit so --platform works on Apple Silicon
export DOCKER_BUILDKIT=1

# Option A: regular build with BuildKit
# docker build \
#   --platform linux/amd64 \
#   -t scalpel:latest \
#   .

# Option B: use Docker Buildx (uncomment if you prefer)
docker buildx create --use --bootstrap
docker buildx build \
  --platform linux/amd64 \
  --load \
  -t scalpel:latest \
  .

# --- 2. Tag & push to ECR ---
docker tag scalpel:latest "${ECR_URI}:latest"

aws --profile "$AWS_PROFILE" --region "$AWS_REGION" ecr get-login-password \
  | docker login --username AWS --password-stdin "${ECR_URI%/*}"

docker push "${ECR_URI}:latest"

# --- 3. Update Lambda to pull new image ---
aws --profile "$AWS_PROFILE" --region "$AWS_REGION" lambda update-function-code \
  --function-name "$LAMBDA_NAME" \
  --image-uri "${ECR_URI}:latest"

echo "🚀 Deployed ${ECR_URI}:latest → Lambda ${LAMBDA_NAME}"
