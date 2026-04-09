cSRF_FormUI_Base.__init__ method calls
=========================================
*This is a guide to where hooks are in cSRF for customizing forms*

_field_defs or field_defs (parameter) or defineFields()<br>
_validate_field_defs()

_buildFormLayout()

_buildPages()

```
_build_fields()
	for defn in self._field_defs:
		widget = self._create_widget(defn)
		self._configure_widget(widget, defn)
		self._connect_widget(widget, defn)
		self._place_widget(widget, defn)
```

```
_addActionButtons()
	(may call/use defineActionButtons())
	NotImplemented in Base, suggested first line of override is 
        Actns = ActionButtons if ActionButtons is not None else self.defineActionButtons()
        if Actns is None:
            return

        layoutButtons = self._layouts.buttons
```

initialdisplay()

---

cSRF (calvincTools Simple Record Form) class hierarchy / dependencies
=====================================================================

- cQFmConstants
---
- cQFormLayout
- cQFormFieldDef
- cQFormFieldInstance
- cQFormBtnDef
---
- cQFmNameLabel
---
- cSimpRecFmElement_Base
- cQFmFldWidg
- cQFmLookupWidg
---
- cSRF_FormUI_Base
- cSRF_Formdb_Base
---
- cSRFSingleRecordForm
---
- cSRFMultiRecordWrapper
- cSRFRecordGridForm
- cSRFRecordListForm
---
- cSRFRecordGrid
- cSRFRecordList_Record
- cSRFRecordList
---

