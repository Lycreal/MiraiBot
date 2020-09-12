import json
import typing as T

from .base import PictureSource


class CatPicture(PictureSource):
    # https://thecatapi.com
    api_url: str = 'https://api.thecatapi.com/v1/images/search'
    keywords: T.List[str] = ['猫猫']

    def resolve(self, content: str):
        return json.loads(content)[0]['url']
