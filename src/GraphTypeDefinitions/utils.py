import uuid
import strawberry

def _convert(info, value):
    if hasattr(value, "intoModel"):
        return value.intoModel(info)
    if isinstance(value, list):
        return [_convert(info, v) for v in value]
    return value

def intoModel(self, info: strawberry.types.Info):
    loader = self.getLoader(info=info)
    model = loader.getModel()
    instance = model()
    for key in self.__annotations__.keys():
        original = getattr(self, key)
        setattr(instance, key, _convert(info, original))
    return instance


class InputModelMixin:
    """
    Mixin providing generic intoModel logic for all Strawberry input models.
    Subclasses must implement getLoader().
    """
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        raise NotImplementedError(
            f"Class {cls.__name__} must implement getLoader()."
        )

    def intoModel(self, info: strawberry.types.Info):
        loader = self.getLoader(info)
        model_cls = loader.getModel()
        instance = model_cls()

        # … parsování ostatních polí …
        if self.id in (None, strawberry.UNSET):
            instance.id = uuid.uuid4()
        else:
            instance.id = self.id

        for key in self.__annotations__.keys():
            original = getattr(self, key)
            # Skip None values if desired
            if original is None:
                continue
            setattr(instance, key, _convert(info, original))
        return instance