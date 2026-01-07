from typing import Any

# str2 doesn't work as intended, so just returning str for now and testing if s==None explicitly.
def str2(s: Any, TypeTransforms={None: lambda:'', }, ValueTransforms={None: lambda:''}) -> str:
#     """
#     Convert input to string, handling "special values or types".
#     :param s: Input value.
#     :param TypeTransforms: Dict mapping types to functions that return strings.
#     :param ValueTransforms: Dict mapping specific values to functions that return strings.
#     :return: String representation of input.
    
#     By default, None is converted to an empty string.
#     """
#     if s in ValueTransforms:
#         return ValueTransforms[s]()
#     if s in TypeTransforms:
#         return TypeTransforms[s]()
    if s is None:
        return ''
    return str(s)

def WrapInQuotes(strg, openquotechar = '"', closequotechar = '"'):
    return openquotechar + strg + closequotechar
# WrapInQuotes
def UnWrapQuotes(strg, quotechar = '"'):
    if strg.startswith(quotechar) and strg.endswith(quotechar):
        return strg[1:-1]
    return strg
# UnWrapQuotes

def IsWrappedInQuotes(strg, quotechar = '"'):
    return strg.startswith(quotechar) and strg.endswith(quotechar)
# IsWrappedInQuotes

