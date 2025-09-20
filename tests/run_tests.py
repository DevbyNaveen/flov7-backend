import sys
import os
import pytest

# Get the base directory (parent of tests directory)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add all service directories to sys.path
sys.path.insert(0, os.path.join(base_dir, 'ai-service'))
sys.path.insert(0, os.path.join(base_dir, 'api-gateway'))
sys.path.insert(0, os.path.join(base_dir, 'workflow-service'))
sys.path.insert(0, os.path.join(base_dir, 'shared'))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = f"{base_dir}/ai-service:{base_dir}/api-gateway:{base_dir}/workflow-service:{base_dir}/shared:{os.environ.get('PYTHONPATH', '')}"

# Run pytest with verbose output
if __name__ == '__main__':
    result = pytest.main(['-v', 'tests/unit'])
    sys.exit(result)
