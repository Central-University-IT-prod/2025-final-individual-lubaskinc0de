from typing import Annotated

from annotated_types import Ge, Le
from pydantic import BaseModel

PositiveIntZero = Annotated[int, Ge(0)]
PositiveFloatZero = Annotated[float, Ge(0.0)]
Age = Annotated[int, Ge(0), Le(100)]


class Pagination(BaseModel):
    size: PositiveIntZero | None = 10
    page: PositiveIntZero | None = 0
