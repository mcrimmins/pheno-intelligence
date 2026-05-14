#!/usr/bin/env python3
import os
import sys

# Test the output directory creation functionality
output_dir = "/outputs/phenology-intelligence-v1/anomaly_outputs"
print(f"Trying to create directory: {output_dir}")
print(f"Exists: {os.path.exists(output_dir)}")

# Test creating directory in workspace if needed
workspace_output = "/workspace/phenology-intelligence-v1/test_output"
os.makedirs(workspace_output, exist_ok=True)
print(f"Workspace directory test created: {workspace_output}")

# Check what paths are available
print("Current working directory:", os.getcwd())
print("Available paths:")
for item in os.listdir("/workspace/phenology-intelligence-v1/"):
    print(f"  {item}")