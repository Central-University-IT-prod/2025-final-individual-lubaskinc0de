import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError

from crudik.adapters.file_manager import FileUploadError
from crudik.adapters.swear_filter import CannotCheckSwearsError
from crudik.adapters.text_generator import TextGenerationError
from crudik.application.exceptions.ad import (
    CannotClickWithoutImpressionError,
    CannotShowAdError,
    ClickLimitExceededError,
)
from crudik.application.exceptions.advertiser import (
    AdvertiserDoesNotExistsError,
)
from crudik.application.exceptions.campaign import (
    CampaignAlreadyExistsError,
    CampaignCannotBeInPastError,
    CampaignContainsSwearsError,
    CampaignDoesNotExistsError,
    CannotChangeCampaignAfterStartError,
    ClickLimitGreaterThanImpressionsLimitError,
)
from crudik.application.exceptions.client import ClientDoesNotExistsError
from crudik.application.exceptions.day import CannotSetDayInPastError
from crudik.domain.error.base import AccessDeniedError, AppError
from crudik.presentation.http.exceptions import (
    CannotReadFileInfoError,
    CannotReadFileSizeError,
    FileIsNotImageError,
    FileTooBigError,
)

error_code = {
    AppError: 500,
    ClientDoesNotExistsError: 404,
    AdvertiserDoesNotExistsError: 404,
    CampaignAlreadyExistsError: 409,
    CampaignCannotBeInPastError: 422,
    CampaignDoesNotExistsError: 404,
    AccessDeniedError: 403,
    CannotChangeCampaignAfterStartError: 422,
    CannotSetDayInPastError: 422,
    CannotShowAdError: 404,
    CampaignContainsSwearsError: 422,
    FileIsNotImageError: 422,
    FileTooBigError: 413,
    CannotReadFileSizeError: 400,
    CannotReadFileInfoError: 400,
    FileUploadError: 422,
    CannotClickWithoutImpressionError: 403,
    ClickLimitExceededError: 403,
    CannotCheckSwearsError: 408,
    ClickLimitGreaterThanImpressionsLimitError: 422,
    TextGenerationError: 418,
}

error_message = {
    AppError: "Unhandled app error",
    ClientDoesNotExistsError: "Client does not exists",
    AdvertiserDoesNotExistsError: "Advertiser does not exists",
    CampaignAlreadyExistsError: "Campaign already exists",
    CampaignCannotBeInPastError: "Campaign cannot be in past",
    CampaignDoesNotExistsError: "Campaign does not exists",
    AccessDeniedError: "Access denied",
    CannotChangeCampaignAfterStartError: "You can't change some of provided params after company has started.",
    CannotSetDayInPastError: "You can`t set day in past.",
    CannotShowAdError: "We didn't find any relevant ad for you(",
    CampaignContainsSwearsError: "Your ad contains swears!",
    FileIsNotImageError: "Expected image. Your file is not an image",
    FileTooBigError: "File too big",
    CannotReadFileSizeError: "Cannot read file size",
    CannotReadFileInfoError: "Cannot read file info (determine file ext/mime)",
    FileUploadError: "Cannot upload content.",
    CannotClickWithoutImpressionError: "You can`t click until you didn`t see ad.",
    ClickLimitExceededError: "Click limit exceeded",
    CannotCheckSwearsError: "Cannot check for swears!",
    ClickLimitGreaterThanImpressionsLimitError: "Click limit cannot be greater than impressions limit!",
    TextGenerationError: "Text generation error!",
}


def get_http_error_response(
    err: AppError,
) -> JSONResponse:
    err_type = type(err)
    err_http_code = error_code[err_type]
    err_msg = error_message[err_type]
    class_name = err.__class__.__qualname__
    err_business_code = class_name[0]

    for char in err.__class__.__qualname__[1:]:
        if char.isupper():
            err_business_code += "_"
        err_business_code += char.upper()

    err_business_code = err_business_code.removesuffix("_ERROR")

    return JSONResponse(
        status_code=err_http_code,
        content={
            "msg": err_msg,
            "code": err_business_code,
        },
    )


async def app_exception_handler(
    _request: Request,
    exc: AppError,
) -> JSONResponse:
    return get_http_error_response(exc)


async def dbapi_error_handler(
    _request: Request,
    _exc: DBAPIError,
) -> JSONResponse:
    logging.exception("DBAPI Error:")
    return JSONResponse(
        status_code=422,
        content={
            "msg": "Bad request",
            "code": "INTEGRITY_ERROR",
        },
    )


async def validation_error_handler(
    _request: Request,
    _exc: ValidationError,
) -> JSONResponse:
    logging.exception("Validation error:")
    return JSONResponse(
        status_code=422,
        content={
            "msg": "Validation error in request",
            "code": "VALIDATION_ERROR",
        },
    )
