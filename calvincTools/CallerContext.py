from typing import Any
from dataclasses import dataclass

@dataclass
class CallerContext:
    Qapp:Any = None
    config:Any = None
    app_ssnmaker:Any = None
    cTools_bind_key:Any = None
    cTools_tablenames:Any = None
    cTools_models:Any = None
