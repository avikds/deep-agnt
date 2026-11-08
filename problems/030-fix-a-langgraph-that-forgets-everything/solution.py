from typing import TypedDict, Annotated
import operator

class State(TypedDict):
    findings: Annotated[list, operator.add]
    steps: Annotated[int, operator.add]
