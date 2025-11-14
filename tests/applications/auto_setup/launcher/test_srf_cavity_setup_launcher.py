from random import randint
from unittest.mock import MagicMock, PropertyMock

import pytest

from sc_linac_physics.applications.auto_setup.backend.setup_cavity import (
    SetupCavity,
)
from sc_linac_physics.applications.auto_setup.launcher.srf_cavity_setup_launcher import (
    setup_cavity,
)
from sc_linac_physics.utils.epics import make_mock_pv


@pytest.fixture
def cavity():
    mock_rack = MagicMock()
    mock_rack.name = "RACK01"  # Use actual string to avoid logger issues
    cavity = SetupCavity(cavity_num=randint(1, 8), rack_object=mock_rack)
    cavity.logger = MagicMock()  # Mock the logger
    cavity.setup = MagicMock()
    cavity.shut_down = MagicMock()
    cavity._status_msg_pv_obj = make_mock_pv()
    cavity._status_pv_obj = make_mock_pv()
    yield cavity


@pytest.fixture
def mock_logger():
    return MagicMock()


def test_setup(cavity, mock_logger):
    """Test that setup is called when shutdown=False and script is not running"""
    # Mock script_is_running to return False
    type(cavity).script_is_running = PropertyMock(return_value=False)

    setup_cavity(cavity, shutdown=False, logger=mock_logger)
    cavity.setup.assert_called_once()
    cavity.shut_down.assert_not_called()


def test_setup_running(cavity, mock_logger):
    """Test that nothing happens when script is already running"""
    # Mock script_is_running to return True
    type(cavity).script_is_running = PropertyMock(return_value=True)

    setup_cavity(cavity, shutdown=False, logger=mock_logger)
    cavity.setup.assert_not_called()
    cavity.shut_down.assert_not_called()
    mock_logger.warning.assert_called()


def test_shutdown(cavity, mock_logger):
    """Test that shutdown is called when shutdown=True and script is not running"""
    # Mock script_is_running to return False
    type(cavity).script_is_running = PropertyMock(return_value=False)

    setup_cavity(cavity, shutdown=True, logger=mock_logger)
    cavity.setup.assert_not_called()
    cavity.shut_down.assert_called_once()


def test_shutdown_running(cavity, mock_logger):
    """Test that nothing happens when trying to shutdown a running script"""
    # Mock script_is_running to return True
    type(cavity).script_is_running = PropertyMock(return_value=True)

    setup_cavity(cavity, shutdown=True, logger=mock_logger)
    cavity.setup.assert_not_called()
    cavity.shut_down.assert_not_called()
    mock_logger.warning.assert_called()
