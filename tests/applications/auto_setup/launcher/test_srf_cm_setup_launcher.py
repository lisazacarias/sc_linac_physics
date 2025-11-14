from random import randint, choice
from unittest.mock import MagicMock, PropertyMock

import pytest

from sc_linac_physics.applications.auto_setup.backend.setup_cavity import (
    SetupCavity,
)
from sc_linac_physics.applications.auto_setup.backend.setup_cryomodule import (
    SetupCryomodule,
)
from sc_linac_physics.applications.auto_setup.launcher.srf_cm_setup_launcher import (
    setup_cavity,
)
from sc_linac_physics.utils.epics import make_mock_pv
from sc_linac_physics.utils.sc_linac.linac_utils import (
    ALL_CRYOMODULES,
    STATUS_READY_VALUE,
    STATUS_ERROR_VALUE,
)


@pytest.fixture
def cavity():
    mock_rack = MagicMock()
    mock_rack.name = "RACK01"

    cavity = SetupCavity(cavity_num=randint(1, 8), rack_object=mock_rack)
    cavity.logger = MagicMock()
    cavity._status_msg_pv_obj = make_mock_pv()
    cavity._status_pv_obj = make_mock_pv()
    cavity._ssa_cal_requested_pv_obj = make_mock_pv()
    cavity._auto_tune_requested_pv_obj = make_mock_pv()
    cavity._cav_char_requested_pv_obj = make_mock_pv()
    cavity._rf_ramp_requested_pv_obj = make_mock_pv()
    cavity._start_pv_obj = make_mock_pv()
    cavity._stop_pv_obj = make_mock_pv()
    cavity._abort_pv_obj = make_mock_pv()
    cavity.trigger_start = MagicMock()
    cavity.trigger_shutdown = MagicMock()

    mock_linac = MagicMock()
    mock_linac.name = "L0B"

    cavity.cryomodule = SetupCryomodule(
        cryo_name=choice(ALL_CRYOMODULES), linac_object=mock_linac
    )
    cm = cavity.cryomodule
    cm.logger = MagicMock()
    cm._ssa_cal_requested_pv_obj = make_mock_pv()
    cm._auto_tune_requested_pv_obj = make_mock_pv()
    cm._cav_char_requested_pv_obj = make_mock_pv()
    cm._rf_ramp_requested_pv_obj = make_mock_pv()
    cm._start_pv_obj = make_mock_pv()
    cm._stop_pv_obj = make_mock_pv()
    cm._abort_pv_obj = make_mock_pv()

    yield cavity


def test_setup_cavity(cavity):
    args = MagicMock()
    args.shutdown = False

    # Use a fixed status value instead of random choice for deterministic behavior
    cavity._status_pv_obj.get = MagicMock(return_value=STATUS_READY_VALUE)

    # Mock script_is_running to return False so setup proceeds
    type(cavity).script_is_running = PropertyMock(return_value=False)

    setup_cavity(cavity, args)

    cavity.trigger_start.assert_called()
    cryomodule = cavity.cryomodule

    cavity._ssa_cal_requested_pv_obj.put.assert_called()
    cryomodule._ssa_cal_requested_pv_obj.get.assert_called()

    cavity._auto_tune_requested_pv_obj.put.assert_called()
    cryomodule._auto_tune_requested_pv_obj.get.assert_called()

    cavity._cav_char_requested_pv_obj.put.assert_called()
    cryomodule._cav_char_requested_pv_obj.get.assert_called()

    cavity._rf_ramp_requested_pv_obj.put.assert_called()
    cryomodule._rf_ramp_requested_pv_obj.get.assert_called()


def test_setup_cavity_error_status(cavity):
    """Test setup with ERROR status"""
    args = MagicMock()
    args.shutdown = False

    cavity._status_pv_obj.get = MagicMock(return_value=STATUS_ERROR_VALUE)
    type(cavity).script_is_running = PropertyMock(return_value=False)

    setup_cavity(cavity, args)

    # Verify expected behavior based on implementation
    cavity.trigger_start.assert_called()


def test_setup_cavity_shutdown(cavity):
    """Test shutdown path"""
    args = MagicMock()
    args.shutdown = True

    cavity._status_pv_obj.get = MagicMock(return_value=STATUS_READY_VALUE)
    type(cavity).script_is_running = PropertyMock(return_value=False)

    setup_cavity(cavity, args)

    cavity.trigger_shutdown.assert_called()
    cavity.trigger_start.assert_not_called()
