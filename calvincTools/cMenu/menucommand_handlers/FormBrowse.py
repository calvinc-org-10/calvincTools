from calvincTools.utils import UnderConstruction_Dialog


from typing import Any, Dict, Tuple


def FormBrowse(parntWind,
    formname,
    *args, **kwargs
    ) -> Any|None:
    urlIndex = 0
    viewIndex = 1

    from calvincTools import calvincTools
    FormNameToURL_Map:Dict[str,Tuple[str,Any]] = calvincTools().FormNameToURL_Map

    # theForm = 'Form ' + formname + ' is not built yet.  Calvin needs more coffee.'
    theForm = None
    authorized = True
    # formname = formname.lower()
    if formname in FormNameToURL_Map:
        if FormNameToURL_Map[formname][urlIndex]:
            # figure out how to repurpose this later
            # url = FormNameToURL_Map[formname][urlIndex]
            # try:
            #     theView = resolve(reverse(url)).func
            #     urlExists = True
            # except (Resolver404, NoReverseMatch):
            #     urlExists = False
            # # end try
            # if urlExists:
            #     theForm = theView(req)
            # else:
            #     formname = f'{formname} exists but url {url} '
            # #endif
            pass
        # endif FormNameToURL_Map[formname][urlIndex]:
        # elif FormNameToURL_Map[formname][viewIndex]:
        if FormNameToURL_Map[formname][viewIndex]:
            fn = None
            try:
                fn = FormNameToURL_Map[formname][viewIndex]
                theForm = fn(*args, **kwargs)
            except NameError:
                # fn = None
                formname = f'{formname} exists but view {FormNameToURL_Map[formname][viewIndex]} is either not defined, not imported, or has fatal errors.  Calvin needs more coffee.\n'
            except PermissionError:
                authorized = False
            # #end try
        # endif FormNameToURL_Map[formname][viewIndex]:
    # endif formname in FormNameToURL_Map:
    if authorized and not theForm:
        formname = f'Form {formname} is not built yet.  Calvin needs more coffee.'
        # print(formname)
        UnderConstruction_Dialog(parntWind, formname).show()
    else:
        return theForm
    # endif

    # must be rendered if theForm came from a class-based-view
    # if hasattr(theForm,'render'): theForm = theForm.render()
    # return theForm
# FormBrowse
    def end_of_class(self):
        """ place this after the all methods and comments in the class, to avoid accidentally leaving out a method or comment when copying/pasting or refactoring code"""
        pass