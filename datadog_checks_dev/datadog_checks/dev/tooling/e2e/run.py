# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from ..._env import E2E_ENV_VAR_PREFIX, E2E_SET_UP, E2E_TEAR_DOWN
from ...subprocess import run_command
from ...utils import chdir, get_ci_env_vars, path_join
from ..commands.console import echo_debug
from ..constants import get_root
from .format import parse_config_from_result


def _execute(check, command, env_vars):
    if E2E_TEAR_DOWN in env_vars:
        operation = 'starting'
    else:
        operation = 'stopping'

    with chdir(path_join(get_root(), check), env_vars=env_vars):
        echo_debug('%s env with env_vars: %s' % (operation, env_vars), cr=True, indent=True)
        echo_debug('%s env with command: %s' % (operation, command), indent=True)
        result = run_command(command, capture=True)
        echo_debug('command result stdout: %s' % result.stdout, indent=True)
        echo_debug('command result stderr: %s' % result.stderr, indent=True)

    return result


def start_environment(check, env):
    command = 'tox --develop -e {}'.format(env)
    env_vars = {
        E2E_TEAR_DOWN: 'false',
        'PYTEST_ADDOPTS': '--benchmark-skip --exitfirst',
        'TOX_TESTENV_PASSENV': '{} USERNAME PYTEST_ADDOPTS {}'.format(E2E_TEAR_DOWN, ' '.join(get_ci_env_vars())),
    }

    result = _execute(check, command, env_vars)
    return parse_config_from_result(env, result)


def stop_environment(check, env, metadata=None):
    command = 'tox --develop -e {}'.format(env)
    env_vars = {
        E2E_SET_UP: 'false',
        'PYTEST_ADDOPTS': '--benchmark-skip --exitfirst',
        'TOX_TESTENV_PASSENV': '{}* {} USERNAME PYTEST_ADDOPTS {}'.format(
            E2E_ENV_VAR_PREFIX, E2E_SET_UP, ' '.join(get_ci_env_vars())
        ),
    }
    env_vars.update((metadata or {}).get('env_vars', {}))

    result = _execute(check, command, env_vars)
    return parse_config_from_result(env, result)
