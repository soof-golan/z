from typing import Annotated


import z


def test_flat_deps() -> None:
    def foo() -> str:
        return "foo"

    def bar() -> str:
        return "bar"

    @z.injectable
    def baz(
        _foo: Annotated[str, z.Depends(foo)],
        _bar: Annotated[str, z.Depends(bar)],
    ) -> str:
        return _foo + _bar

    assert baz() == "foobar"


def test_nested_deps() -> None:
    def foo() -> str:
        return "foo"

    def bar(_foo: Annotated[str, z.Depends(foo)]) -> str:
        return _foo + "bar"

    @z.injectable
    def baz(_bar: Annotated[str, z.Depends(bar)]) -> str:
        return _bar + "baz"

    assert baz() == "foobarbaz"
