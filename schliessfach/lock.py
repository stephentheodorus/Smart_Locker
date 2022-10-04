import serial
import time
from kink import inject


class Lock:
    def lock(self, locker_id):
        pass

    def unlock(self, locker_id):
        pass


@inject
class BoxLock(Lock):
    def __init__(self):
        self.ser = serial.Serial("COM10", 9600)

    def lock(self, locker_id):
        if 1 <= locker_id <= 4:
            time.sleep(2)
            self.ser.write(bytes(str((locker_id * 2) - 1), encoding="utf-8"))
            # ser.close()

        ### This is for locker number 5 to 8, where we use alphabet A until D for locking lockers number 5 to 8
        elif 5 <= locker_id <= 8:
            time.sleep(2)
            self.ser.write(
                bytes(
                    chr(((locker_id - (locker_id - 5)) * 13) + (locker_id % 5)),
                    encoding="utf-8",
                )
            )

    def unlock(self, locker_id):
        if 1 <= locker_id <= 4:
            time.sleep(2)
            self.ser.write(bytes(str(locker_id * 2), encoding="utf-8"))
            # ser.close()

        elif 5 <= locker_id <= 8:
            time.sleep(2)
            self.ser.write(
                bytes(
                    chr(((locker_id - (locker_id - 5)) * 13) + (locker_id % 5) + 4),
                    encoding="utf-8",
                )
            )


class MockLock(Lock):
    def __init__(self):
        pass
