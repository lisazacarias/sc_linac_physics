from PyQt5.QtWidgets import QPushButton
from pydm.widgets import PyDMEnumComboBox, PyDMSpinbox, PyDMLabel


class RFControls:
    def __init__(self):
        self.ssa_on_button: QPushButton = QPushButton("On")
        self.ssa_off_button: QPushButton = QPushButton("Off")
        self.ssa_readback_label: PyDMLabel = PyDMLabel()

        self.rf_mode_combobox: PyDMEnumComboBox = PyDMEnumComboBox()
        self.rf_mode_readback_label: PyDMLabel = PyDMLabel()

        self.rf_on_button: QPushButton = QPushButton("On")
        self.rf_off_button: QPushButton = QPushButton("Off")
        self.rf_status_readback_label: PyDMLabel = PyDMLabel()

        self.ades_spinbox: PyDMSpinbox = PyDMSpinbox()
        self.aact_readback_label: PyDMLabel = PyDMLabel()

        self.srf_max_spinbox: PyDMSpinbox = PyDMSpinbox()
        self.srf_max_readback_label: PyDMLabel = PyDMLabel()
