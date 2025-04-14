from crudik.domain.error.base import AppError


class CannotShowAdError(AppError): ...


class CannotClickWithoutImpressionError(AppError): ...


class ClickLimitExceededError(AppError): ...
