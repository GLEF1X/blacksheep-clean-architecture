import typing as t

from sqlalchemy.orm import Session


def make_proxy_bulk_save_func(
        instances: t.Sequence[t.Any],
        return_defaults: bool = False,
        update_changed_only: bool = True,
        preserve_order: bool = True,
) -> t.Callable[[Session], None]:
    def _proxy(session: Session) -> None:
        return session.bulk_save_objects(
            instances,
            return_defaults=return_defaults,
            update_changed_only=update_changed_only,
            preserve_order=preserve_order,
        )  # type: ignore

    return _proxy
