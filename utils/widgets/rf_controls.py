from PyQt5.QtWidgets import QPushButton, QComboBox
from pydm.widgets import PyDMEnumComboBox, PyDMSpinbox


class RFControls:
    def __init__(self):
        self.ssa_on_button: QPushButton = QPushButton("On")
        self.ssa_off_button: QPushButton = QPushButton("Off")
        self.rf_mode_combobox: PyDMEnumComboBox = PyDMEnumComboBox()
        self.rf_on_button: QPushButton = QPushButton("On")
        self.rf_off_button: QPushButton = QPushButton("Off")
        seld.ades_spinbox: PyDMSpinbox = PyDMSpinbox()
