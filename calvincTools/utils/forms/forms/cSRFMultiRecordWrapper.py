from typing import List

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QStatusBar, QVBoxLayout, QWidget

import qtawesome

from calvincTools.utils.forms.definitions.cQFormLayout import cQFormLayout
from calvincTools.utils.forms.definitions.cQFormFieldDef import cQFormFieldDef
from calvincTools.utils.forms.definitions.cQFormBtnDef import cQFormBtnDef
from calvincTools.utils.forms.forms.cSRF_FormUI_Base import cSRF_FormUI_Base
from calvincTools.utils.forms.widgets.cQFmNameLabel import cQFmNameLabel
from calvincTools.utils.cQWidgets import cGridWidget, cstdTabWidget


class cSRFMultiRecordWrapper(cSRF_FormUI_Base):
    """
    Base class for multi record wrapper forms. 
    Should contain at least one subform (cSRFRecordGrid or cSRFRecordList) in the fieldDefs, but can contain other widgets as well.
    Inherits from cSRF_FormUI_Base to provide UI functionality, ***but does not include any db functionality.***

    Args:
        cSRF_FormUI_Base (_type_): _description_
    """
    def __init__(self,
        formname: str|None = None,
        field_defs: List[cQFormFieldDef] | None = None,
        parent: QWidget | None = None,
        *args, **kwargs):

        self._formname = getattr(self, '_formname', None)
        if not self._formname:
            self._formname = formname if formname else 'Form'

        super().__init__(field_defs=field_defs, parent=parent, *args, **kwargs)
    # __init__

    ######################################################
    ########    Layout construction

    def _buildFormLayout(self) -> cQFormLayout:
        """Build the form layout for cSimpleRecordForm.

        Returns:
            QFormLayout instance
        """

        layoutMain = QVBoxLayout(self)
        layoutFormHdr = QHBoxLayout()
        layoutForm = cGridWidget(scrollable=True)
        layoutFormFixedTop = QGridLayout()
        layoutFormPages = cstdTabWidget()
        layoutFormFixedBottom = QGridLayout()
        layoutButtons = QVBoxLayout()  # may get redefined in _addActionButtons
        statusBar = QStatusBar(self)

        # should this be in _finalizeMainLayout instead?
        layoutForm.addLayout(layoutFormFixedTop, 0, 0)
        layoutForm.addWidget(layoutFormPages, 1, 0)
        layoutForm.addLayout(layoutFormFixedBottom, 2, 0)

        assert isinstance(self._formname, str), "_formname must be set before building form layout"
        lblFormName = cQFmNameLabel(self.tr(self._formname), self)
        layoutFormHdr.addWidget(lblFormName)

        newrecFlag = QLabel("New Record", self)
        fontNewRec = QFont()
        fontNewRec.setBold(True)
        fontNewRec.setPointSize(10)
        fontNewRec.setItalic(True)
        newrecFlag.setFont(fontNewRec)
        newrecFlag.setStyleSheet("color: red;")
        layoutFormHdr.addWidget(newrecFlag)

        # put it together
        layoutMain.addLayout(layoutFormHdr)
        layoutMain.addWidget(layoutForm)
        layoutMain.addLayout(layoutButtons)
        layoutMain.addWidget(statusBar)

        self.setWindowTitle(self.tr(self._formname))

        rtnval = cQFormLayout(
            main=layoutMain,
            header=layoutFormHdr,
            form=layoutForm,
            fixed_top=layoutFormFixedTop,
            pages=layoutFormPages,
            fixed_bottom=layoutFormFixedBottom,
            buttons=layoutButtons,
            status_bar=statusBar,

            lblFormName = lblFormName,
            newrecFlag = newrecFlag,
            )

        return rtnval
    # _buildFormLayout

    ######################################################
    ########    field and Widget placement

    def defineActionButtons(self):
        _iconlib = qtawesome.icon
        r = [
            cQFormBtnDef(text="Close", icon=_iconlib("mdi.cancel"), action=self.on_close_clicked),
            ]
        return r

    def _addActionButtons(self,
            ActionButtons:List[cQFormBtnDef]|None = None,
            ) -> None:
        """Add action buttons to the form.
        """

        Actns = ActionButtons if ActionButtons is not None else self.defineActionButtons()
        if Actns is None:
            return

        layoutButtons = self._layouts.buttons

        innerLayout = QHBoxLayout()

        for btndef in Actns:
            if btndef.type == cQFormBtnDef.ButtonType.NEW_VSECTION:
                layoutButtons.addLayout(innerLayout)
                innerLayout = QHBoxLayout()
            elif btndef.type == cQFormBtnDef.ButtonType.NEW_HSECTION:
                innerLayout.addSpacing(20)
            elif btndef.type != cQFormBtnDef.ButtonType.NORMAL:
                raise ValueError(f"unknown button type {btndef.type}")
            else:
                btn = QPushButton(btndef.text)
                if btndef.icon is not None:
                    btn.setIcon(btndef.icon)
                if callable(btndef.action):
                    btn.clicked.connect(btndef.action)
                if btndef.commitBtn:
                    self.btnCommit = btn
                innerLayout.addWidget(btn)
            # endif button type
        # endfor btndef om Actns
    # _addNavButtons

    def on_close_clicked(self):
        """Handle the Cancel button click by closing the form.

        Note:
            Currently just closes the form without any confirmation.
        """
        #for now, just close form
        self.close()
    # cancel_record


    ######################################################
    ########    Display 

    def initialdisplay(self):
        """
        Initialize and display the form.
        """
        # self.initializeRec()
        # self.on_loadfirst_clicked()
        ...
    # initialdisplay()

# cSRFMultiRecordWrapper
    def endofclass(self):
        pass


# other form classes can be added here as needed, following the same pattern of inheriting from the appropriate base classes to combine UI and db functionality as needed.
# Note that a cSRFRecordGridForm = cSRFMultiRecordWrapper + cSRFRecordGrid is not necessary, as the cSRFRecordGrid can simply be used as a subform within the cSRFMultiRecordWrapper, and the cSRFMultiRecordWrapper can be used on its own as a wrapper for any number of subforms, including cSRFRecordGrids and cSRFRecordLists.
# similarly, a cSRFRecordListForm = cSRFMultiRecordWrapper + cSRFRecordList is not necessary, as the cSRFRecordList can simply be used as a subform within the cSRFMultiRecordWrapper, and the cSRFMultiRecordWrapper can be used on its own as a wrapper for any number of subforms, including cSRFRecordGrids and cSRFRecordLists.

class cSRFRecordGridForm(cSRFMultiRecordWrapper):
    ...


class cSRFRecordListForm(cSRFMultiRecordWrapper):
    ...