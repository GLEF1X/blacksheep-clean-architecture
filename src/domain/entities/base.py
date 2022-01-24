import dataclasses
from typing import Any, Dict


@dataclasses.dataclass(eq=False)
class Entity:
    """
    Entity is a business logic pattern: it is thought to have a set of fields and methods
    that embody some knowledge about the domain.
    * Entity class is structured, which means that some relation to other entity is represented by
      concrete reference to the other object.
    * Entity (and an aggregate root especially) should represent complex data and shouldn't
      be normalized.
    """
    id: int = dataclasses.field()

    def __init__(self, **kwargs: Any):
        """
        This initializer will be overridden by dataclass decorator above. It is needed to
        persuade static type checkers that Entities have initializers.
        """

    def __eq__(self, other: Any) -> bool:
        """Entity is identified by the value of its `id` field."""
        return isinstance(other, self.__class__) and other.id == self.id

    def dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

