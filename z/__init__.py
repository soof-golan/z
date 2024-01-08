from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Callable, Generic, get_type_hints, TypeVar

from typing_extensions import ParamSpec

T = TypeVar("T")
Dep = TypeVar("Dep")
SubDep = TypeVar("SubDep")
P = ParamSpec("P")


def _infer_dependencies(func: Callable[P, SubDep]) -> dict[str, Depends[SubDep]]:
    _annotations = get_type_hints(func, include_extras=True)
    dependencies = {}
    for name, annotation in _annotations.items():
        if hasattr(annotation, "__metadata__"):
            for metadata in annotation.__metadata__:
                if isinstance(metadata, Depends):
                    dependencies[name] = metadata
    return dependencies


@dataclass(frozen=True)
class Depends(Generic[Dep]):
    func: Callable[P, Dep]

    @functools.cached_property
    def _deps(self) -> dict[str, Depends[Dep]]:
        return _infer_dependencies(self.func)

    def solve(self, *args: P.args, **kwargs: P.kwargs) -> Dep:
        sub_solution = {
            name: dependency.solve() for name, dependency in self._deps.items()
        }

        return self.func(
            *args,
            **kwargs,
            **sub_solution,
        )


def injectable(func: Callable[P, T]) -> Callable[[], T]:
    root = Depends(func)

    @functools.wraps(func)
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return root.solve(*args, **kwargs)

    return _wrapper
