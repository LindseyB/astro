import os
import subprocess
import sys
from collections.abc import Mapping


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run_import_routes_with_env(env: Mapping[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, '-c', 'import routes'],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_routes_import_fails_without_secret_key():
    env = os.environ.copy()
    env.pop('SECRET_KEY', None)
    env['FLASK_ENV'] = 'production'
    env.pop('FLASK_DEBUG', None)

    result = _run_import_routes_with_env(env)

    assert result.returncode != 0
    assert 'SECRET_KEY environment variable is required at startup.' in result.stderr


def test_routes_import_succeeds_with_secret_key():
    env = os.environ.copy()
    env['SECRET_KEY'] = 'integration-test-secret-key'
    env['FLASK_ENV'] = 'production'
    env.pop('FLASK_DEBUG', None)

    result = _run_import_routes_with_env(env)

    assert result.returncode == 0
