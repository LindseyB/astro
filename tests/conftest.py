import os

# Keep tests deterministic while production enforces explicit configuration.
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
