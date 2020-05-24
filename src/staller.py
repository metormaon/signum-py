import abc
import time
from datetime import datetime
from threading import Thread
from typing import Tuple, Generic, TypeVar

T = TypeVar('T')


class Staller(Generic[T]):
    def __init__(self, unit_time_in_ms: int, stall_if_successful: bool = False, cut_if_delayed: bool = True):
        self.cut_if_delayed = cut_if_delayed
        self.stall_if_successful = stall_if_successful
        self.unit_time_in_ms = unit_time_in_ms

    class Stallable(abc.ABC):
        @abc.abstractmethod
        def do_work(self, *args, **kwargs) -> None:
            pass

        @abc.abstractmethod
        def get_result(self) -> T:
            pass

        @abc.abstractmethod
        def interrupt(self):
            pass

        @abc.abstractmethod
        def was_successful(self) -> bool:
            pass

    def stall(self, stallable: Stallable, *args, **kwargs) -> Tuple[bool, T]:
        start_time = time.time()

        if self.cut_if_delayed:
            thread: Thread = Thread(target=stallable.do_work, args=args, kwargs=kwargs)
            thread.start()
            thread.join(self.unit_time_in_ms/1000)

            if thread.is_alive():
                stallable.interrupt()
                return False, None

        else:
            stallable.do_work(*args, **kwargs)

        result: T = stallable.get_result()

        success: bool = stallable.was_successful()

        if not success or self.stall_if_successful:
            elapsed: int = int((time.time() - start_time) * 1000)

            left: int = self.unit_time_in_ms - elapsed

            if left >= 0:
                time.sleep(left/1000)

        return success, result
