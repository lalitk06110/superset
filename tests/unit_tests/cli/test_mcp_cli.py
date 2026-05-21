# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Tests for the ``superset mcp`` CLI command group."""

from unittest.mock import MagicMock, patch

import click
from click.testing import CliRunner

from superset.cli.mcp import mcp


def test_mcp_group_is_click_group():
    """The ``mcp`` object is a Click group so it can hold sub-commands."""
    assert isinstance(mcp, click.Group)


def test_mcp_group_has_run_subcommand():
    """The ``run`` sub-command is registered under the ``mcp`` group."""
    assert "run" in mcp.commands


def test_run_subcommand_accepts_host_port_debug():
    """``superset mcp run`` accepts --host, --port, and --debug options."""
    run_cmd = mcp.commands["run"]
    param_names = [p.name for p in run_cmd.params]
    assert "host" in param_names
    assert "port" in param_names
    assert "debug" in param_names


def test_run_delegates_to_run_server():
    """``superset mcp run`` calls ``run_server`` from the MCP service."""
    runner = CliRunner()
    mock_run = MagicMock()
    bind_all = "0.0.0.0"  # noqa: S104

    with patch(
        "superset.mcp_service.server.run_server",
        mock_run,
    ):
        result = runner.invoke(mcp, ["run", "--host", bind_all, "--port", "9999"])

    assert result.exit_code == 0, result.output
    mock_run.assert_called_once_with(host=bind_all, port=9999, debug=False)


def test_run_shows_helpful_error_when_fastmcp_missing():
    """``superset mcp run`` shows install instructions when fastmcp is absent."""
    runner = CliRunner()

    def _import_error_run(host: str, port: int, debug: bool) -> None:
        raise ImportError("No module named 'fastmcp'")

    with patch.object(mcp.commands["run"], "callback", _import_error_run):
        result = runner.invoke(mcp, ["run"])

    assert result.exit_code != 0
    assert (
        "fastmcp" in result.output.lower()
        or "fastmcp" in (result.exception and str(result.exception) or "").lower()
    )


def test_mcp_group_discovered_by_cli_autodiscovery():
    """The ``mcp`` group is found by the CLI auto-discovery in ``main.py``.

    ``superset.cli.main`` walks ``superset.cli.*`` and registers every
    ``click.Group`` / ``click.Command``.  This test verifies ``mcp`` is
    among the registered commands so ``superset mcp …`` resolves.
    """
    from superset.cli.main import superset as superset_cli

    assert "mcp" in superset_cli.commands, (
        "'mcp' command not registered – check superset/cli/mcp.py "
        "is importable and contains a click.Group named 'mcp'"
    )
