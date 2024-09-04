from django.core.cache import cache
from django.db.models import Model
from typing import Union, List, Dict, Any


class CacheManager:
    @staticmethod
    def get_cache_key(model: Union[Model, str], identifier: Union[int, str]) -> str:
        if isinstance(model, str):
            model_name = model
        else:
            model_name = model.__name__
        return f"{model_name.lower()}:{identifier}"

    @staticmethod
    def set_cache(model: Union[Model, str], identifier: Union[int, str], data: Dict[str, Any],
                  timeout: int = 3600) -> None:
        cache_key = CacheManager.get_cache_key(model, identifier)
        cache.set(cache_key, data, timeout)

    @staticmethod
    def get_cache(model: Union[Model, str], identifier: Union[int, str]) -> Union[Dict[str, Any], None]:
        cache_key = CacheManager.get_cache_key(model, identifier)
        return cache.get(cache_key)

    @staticmethod
    def delete_cache(model: Union[Model, str], identifier: Union[int, str]) -> None:
        cache_key = CacheManager.get_cache_key(model, identifier)
        cache.delete(cache_key)

    @staticmethod
    def bulk_delete_cache(model: Union[Model, str], identifiers: List[Union[int, str]]) -> None:
        cache_keys = [CacheManager.get_cache_key(model, identifier) for identifier in identifiers]
        cache.delete_many(cache_keys)


class CacheModelMixin:
    def cache_data(self):
        raise NotImplementedError("Subclasses must implement cache_data method")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        CacheManager.set_cache(self.__class__, self.id, self.cache_data())

    def delete(self, *args, **kwargs):
        CacheManager.delete_cache(self.__class__, self.id)
        super().delete(*args, **kwargs)

    @classmethod
    def get_from_cache(cls, id):
        cached_data = CacheManager.get_cache(cls, id)
        if cached_data:
            return cls(**cached_data)
        return None
