import asyncio

from analytics.worker import noop


def test_noop() -> None:
    assert asyncio.run(noop()) is None
