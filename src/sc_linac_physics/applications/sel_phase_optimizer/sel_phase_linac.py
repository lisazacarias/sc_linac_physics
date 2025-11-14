from typing import Optional

import numpy as np
from scipy import stats

from sc_linac_physics.applications.sel_phase_optimizer.utils import (
    SEL_PHASE_OPT_LOG_DIR,
)
from sc_linac_physics.utils.epics import PV
from sc_linac_physics.utils.logger import custom_logger
from sc_linac_physics.utils.sc_linac.cavity import Cavity
from sc_linac_physics.utils.sc_linac.linac import Machine
from sc_linac_physics.utils.sc_linac.linac_utils import RF_MODE_SELAP

MAX_STEP = 5
MULT = -51.0471


class SELCavity(Cavity):

    def __init__(
        self,
        cavity_num,
        rack_object,
    ):
        super().__init__(cavity_num=cavity_num, rack_object=rack_object)
        self._q_waveform_pv: Optional[PV] = None
        self._i_waveform_pv: Optional[PV] = None
        self._sel_poff_pv_obj: Optional[PV] = None
        self._fit_chisquare_pv_obj: Optional[PV] = None
        self._fit_slope_pv_obj: Optional[PV] = None
        self._fit_intercept_pv_obj: Optional[PV] = None

        self.logger = custom_logger(
            name=f"{self.cryomodule.name}.{self.number}.SELPhaseOpt",
            log_dir=str(SEL_PHASE_OPT_LOG_DIR / self.cryomodule.name),
            log_filename=f"{self.number}",
        )

    @property
    def sel_poff_pv_obj(self) -> PV:
        if not self._sel_poff_pv_obj:
            self._sel_poff_pv_obj = PV(self.pv_addr("SEL_POFF"))
        return self._sel_poff_pv_obj

    @property
    def sel_phase_offset(self):
        return self.sel_poff_pv_obj.get()

    @property
    def i_waveform(self):
        if not self._i_waveform_pv:
            self._i_waveform_pv = PV(self.pv_addr("CTRL:IWF"))
        return self._i_waveform_pv.get()

    @property
    def q_waveform(self):
        if not self._q_waveform_pv:
            self._q_waveform_pv = PV(self.pv_addr("CTRL:QWF"))
        return self._q_waveform_pv.get()

    @property
    def fit_chisquare_pv_obj(self) -> PV:
        if not self._fit_chisquare_pv_obj:
            self._fit_chisquare_pv_obj = PV(self.pv_addr("CTRL:FIT_CHISQUARE"))
        return self._fit_chisquare_pv_obj

    @property
    def fit_slope_pv_obj(self) -> PV:
        if not self._fit_slope_pv_obj:
            self._fit_slope_pv_obj = PV(self.pv_addr("CTRL:FIT_SLOPE"))
        return self._fit_slope_pv_obj

    @property
    def fit_intercept_pv_obj(self) -> PV:
        if not self._fit_intercept_pv_obj:
            self._fit_intercept_pv_obj = PV(self.pv_addr("CTRL:FIT_INTERCEPT"))
        return self._fit_intercept_pv_obj

    def can_be_straightened(self) -> bool:
        return (
            self.is_online
            and self.is_on
            and self.rf_mode == RF_MODE_SELAP
            and self.aact > 1
        )

    def straighten_iq_plot(self) -> float:
        """
        TODO make the return value more intuitive
        :return: change in SEL phase offset
        """

        if not self.can_be_straightened():
            return 0

        start_val = self.sel_phase_offset
        iwf = self.i_waveform
        qwf = self.q_waveform

        # siegelslopes is called with y then (optional) x
        [slop, inter] = stats.siegelslopes(iwf, qwf)

        if not np.isnan(slop):
            chisum = 0
            for nn, yy in enumerate(iwf):
                denom = slop * qwf[nn] + inter
                # Avoid division by zero in chi^2 (very unlikely but cheap safeguard)
                if denom == 0:
                    continue
                chisum += (yy - denom) ** 2 / denom

            step = slop * MULT
            if abs(step) > MAX_STEP:
                step = MAX_STEP * np.sign(step)
                self.logger.warning(
                    f"Desired SEL Phase Offset change too large, moving by {step} instead"
                )

            if start_val + step < -180:
                step = step + 360
            elif start_val + step > 180:
                step = step - 360

            self.sel_poff_pv_obj.put(start_val + step)
            self.fit_chisquare_pv_obj.put(chisum)
            self.fit_slope_pv_obj.put(slop)
            self.fit_intercept_pv_obj.put(inter)

            self.logger.info(
                f"Changed SEL Phase Offset by {step:5.2f} with chi^2 {chisum:.2g}"
            )
            return step

        else:
            self.logger.warning(
                "IQ slope is NaN, not changing SEL Phase Offset"
            )
            return 0


SEL_MACHINE: Machine = Machine(cavity_class=SELCavity)
