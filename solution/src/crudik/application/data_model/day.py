from pydantic import BaseModel

from crudik.application.data_model.common import PositiveIntZero


class Day(BaseModel):
    current_date: PositiveIntZero = 0
