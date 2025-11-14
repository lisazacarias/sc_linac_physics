#!/usr/bin/env python

"""
Script to optimize SEL phase offsets
Originally by J. Nelson, refactored by L. Zacarias
"""
import argparse
import os
import time
from typing import List

from sc_linac_physics.applications.sel_phase_optimizer.sel_phase_linac import (
    SEL_MACHINE,
    SELCavity,
    MAX_STEP,
)
from sc_linac_physics.utils.epics import PV, PVInvalidError

# Lazy-load PV to make testing easier
_HEARTBEAT_PV = None


def get_heartbeat_pv() -> PV:
    """Get or create the heartbeat PV.

    Returns:
        PV: The heartbeat PV instance
    """
    global _HEARTBEAT_PV
    if _HEARTBEAT_PV is None:
        # Allow mocking in tests
        if os.getenv("PYTEST_CURRENT_TEST"):
            from unittest.mock import MagicMock

            _HEARTBEAT_PV = MagicMock()
        else:
            _HEARTBEAT_PV = PV("PHYS:SYS0:1:SC_SEL_PHAS_OPT_HEARTBEAT")
    return _HEARTBEAT_PV


def update_heartbeat(time_to_wait: int) -> None:
    """Update the heartbeat PV while waiting.

    Args:
        time_to_wait: Number of seconds to wait
    """
    print(f"Sleeping for {time_to_wait} seconds")
    heartbeat_pv = get_heartbeat_pv()

    for _ in range(time_to_wait):
        try:
            heartbeat_pv.put(heartbeat_pv.get() + 1)
        except (TypeError, PVInvalidError) as e:
            print(f"Error updating heartbeat: {e}")
        time.sleep(1)


def optimize_cavity(cavity: SELCavity) -> bool:
    """Optimize a single cavity's SEL phase.

    Args:
        cavity: The cavity to optimize

    Returns:
        bool: True if the phase change was >= MAX_STEP, False otherwise
    """
    try:
        phase_change = cavity.straighten_iq_plot()
        get_heartbeat_pv().put(get_heartbeat_pv().get() + 1)
        return phase_change >= MAX_STEP
    except (PVInvalidError, TypeError) as e:
        cavity.logger.error(f"Error optimizing {cavity}: {e}")
        return False


def run_optimization_cycle(cavities: List[SELCavity]) -> int:
    """Run one optimization cycle on all cavities.

    Args:
        cavities: List of cavities to optimize

    Returns:
        int: Number of cavities that hit the maximum step limit
    """
    num_large_steps = 0

    for cavity in cavities:
        if optimize_cavity(cavity):
            num_large_steps += 1

    return num_large_steps


def run() -> None:
    """Main optimization loop."""
    cavities: List[SELCavity] = list(SEL_MACHINE.all_iterator)

    while True:
        num_large_steps = run_optimization_cycle(cavities)

        if num_large_steps > 5:
            print(
                f"\033[91mPhase change limited to 5 deg {num_large_steps} times. "
                f"Re-running program.\033[0m"
            )
            update_heartbeat(5)
        else:
            current_time = time.strftime("%m/%d/%y %H:%M:%S", time.localtime())
            print(
                f"\033[94mThanks for your help! The current date/time is "
                f"{current_time}\033[0m"
            )
            update_heartbeat(600)


def main() -> None:
    """Main entry point for the SEL phase optimizer."""
    parser = argparse.ArgumentParser(description="Optimize SEL phase offsets")
    parser.parse_args()

    get_heartbeat_pv().put(0)
    run()


if __name__ == "__main__":
    main()
