#!/bin/bash

# Activate virtual environment
source /Users/naveen/Desktop/Flov7/.venv/bin/activate

# Set PYTHONPATH to include all service directories and shared directory
export PYTHONPATH=/Users/naveen/Desktop/Flov7/flov7-backend/ai-service:/Users/naveen/Desktop/Flov7/flov7-backend/api-gateway:/Users/naveen/Desktop/Flov7/flov7-backend/workflow-service:/Users/naveen/Desktop/Flov7/flov7-backend/shared:$PYTHONPATH

echo "Environment set up. PYTHONPATH is: $PYTHONPATH"
