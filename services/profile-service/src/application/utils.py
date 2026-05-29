from dataclasses import dataclass, replace

from fastapi import UploadFile
from src.application.enums import SOCIAL_BUILDERS, SocialMediaType
from src.application.exceptions import FileSizeTooLarge


async def validate_file_size(file: UploadFile, max_file_size: int):
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > max_file_size:
        raise FileSizeTooLarge()


@dataclass(slots=True)
class SocialMediaDTO:
    type: SocialMediaType
    url: str | None = None
    detail: str | None = None


# OCP
def social_url_generator(social_medias: list[SocialMediaDTO]) -> list[dict]:

    result = []

    for sm in social_medias:
        builder = SOCIAL_BUILDERS.get(sm.type)

        if builder and sm.detail:
            sm = replace(sm, url=builder(sm.detail))

        result.append(
            {
                "type": sm.type,
                "detail": sm.detail,
                "url": sm.url,
            }
        )

    return result
