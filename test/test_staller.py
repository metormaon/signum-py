import time
from typing import Any, Tuple, Dict
from unittest import TestCase

from src.staller import Staller, T


class TestStaller(TestCase):
    class TestStallable(Staller.Stallable):
        def __init__(self, sleep_time: int, success: bool):
            self.args: Tuple[Any, ...] = ()
            self.kwargs: Dict[str, Any] = {}
            self.sleep_time: int = sleep_time
            self.result: int = 0
            self.interrupted = False
            self.success = success

        def do_work(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

            for _ in range(self.sleep_time // 50):
                if self.interrupted:
                    break

                time.sleep(50/1000)

            if not self.interrupted:
                self.result = 8

        def get_result(self) -> int:
            return self.result

        def interrupt(self):
            self.interrupted = True

        def was_successful(self) -> bool:
            return self.success

    def test_stall_on_success(self):
        stallable = self.TestStallable(400, success=True)

        staller = Staller(1000)

        start_time = time.time()

        staller.stall(stallable, 1, True, pi=3.4)

        elapsed: int = int((time.time() - start_time) * 1000)
        print(elapsed)

        self.assertTrue(400 <= elapsed < 500)
        self.assertEqual(8, stallable.result)
        self.assertEqual((1, True), stallable.args)
        self.assertEqual({'pi': 3.4}, stallable.kwargs)

    def test_stall_on_success_when_stalling(self):
        stallable = self.TestStallable(400, success=True)

        staller = Staller(1000, stall_if_successful=True)

        start_time = time.time()

        staller.stall(stallable, 1, True, pi=3.4)

        elapsed: int = int((time.time() - start_time) * 1000)
        print(elapsed)

        self.assertTrue(1000 <= elapsed < 1100)
        self.assertEqual(8, stallable.result)
        self.assertEqual((1, True), stallable.args)
        self.assertEqual({'pi': 3.4}, stallable.kwargs)

    def test_stall_on_failure(self):
        stallable = self.TestStallable(400, success=False)

        staller = Staller(1000)

        start_time = time.time()

        staller.stall(stallable, 1, True, pi=3.4)

        elapsed: int = int((time.time() - start_time) * 1000)
        print(elapsed)

        self.assertTrue(1000 <= elapsed < 1100)
        self.assertEqual(8, stallable.result)
        self.assertEqual((1, True), stallable.args)
        self.assertEqual({'pi': 3.4}, stallable.kwargs)

    def test_cut_on_delay(self):
        stallable = self.TestStallable(1000, success=True)

        staller = Staller(400)

        start_time = time.time()

        staller.stall(stallable, 1, True, pi=3.4)

        elapsed: int = int((time.time() - start_time) * 1000)
        print(elapsed)

        self.assertTrue(400 <= elapsed < 500)
        self.assertEqual(0, stallable.result)
        self.assertEqual((1, True), stallable.args)
        self.assertEqual({'pi': 3.4}, stallable.kwargs)

    def test_no_cut_on_delay(self):
        stallable = self.TestStallable(1000, success=True)

        staller = Staller(400, cut_if_delayed=False)

        start_time = time.time()

        staller.stall(stallable, 1, True, pi=3.4)

        elapsed: int = int((time.time() - start_time) * 1000)
        print(elapsed)

        self.assertTrue(1000 <= elapsed < 1100)
        self.assertEqual(8, stallable.result)
        self.assertEqual((1, True), stallable.args)
        self.assertEqual({'pi': 3.4}, stallable.kwargs)
