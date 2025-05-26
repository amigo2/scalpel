#!/usr/bin/env bash
set -euo pipefail

# 1) Build the frontend (emits into frontend/dist)
cd frontend
npm install
npm run build
cd ..

# 2) Copy the build output into the backend’s frontend/build folder
#    (or whatever folder your FastAPI expects—here we’ll keep using src/app/frontend/build)
DEST_DIR=src/app/frontend/build

echo "Cleaning out old frontend build at $DEST_DIR"
rm -rf "$DEST_DIR"
mkdir -p "$DEST_DIR"

echo "Copying new build artifacts to $DEST_DIR"
cp -R frontend/dist/* "$DEST_DIR/"

echo "✅ Frontend built and deployed to $DEST_DIR"
