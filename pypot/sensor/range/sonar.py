from __future__ import print_function
import time
import numpy as np

from ...robot.sensor import Sensor
from ...utils import StoppableLoopThread

try:
    import smbus
except ImportError:
    print('''You need to install smbus:
          sudo apt-get install build-essential libi2c-dev i2c-tools python-dev libffi-dev
          pip install smbus-cffi''')


class SonarSensor(Sensor):
	""" Give acces to ultrasonic I2C modules SRF-02 in a *pypot way* """

	def __init__(self,)
		pass


class Sonar():
    """ Give acces to ultrasonic I2C modules SRF-02 connected with I2C pin of your board.
        To have more informations, go to http://www.robot-electronics.co.uk/htm/srf02techI2C.htm

        Example:

        > i2c = smbus.SMBus(1)
        > sonar = Sonar(i2c, adresses=[0x70,0x71,0x72])
        >
    """

    def __init__(self, i2c, addresses=None):
        self.i2c = i2c

        # 0x70 is the default adress of SRF-02 I2C module
        self.addresses = addresses if addresses is not None else [0x70]
        self.datas = None

        self._raw_data_queues = []
        for _ in self.addresses:
            self._raw_data_queues.append(5 * [0, ])

        self.results_type = {'inches': 0x50,
                             'centimeters': 0x51,
                             'microseconds': 0x52}

        self.__errors = 0

    def update(self):
        self.ping()
        time.sleep(0.065)
        self.datas = self._filter(self.read())
        return self.datas

    def ping(self):
        for addr in self.addresses:
            self._ping(addr)

    def read(self, reg=2):
        return [self._read(addr, reg) for addr in self.addresses]

    def _filter(self, datas):
        """Apply a filter to reduce noisy datas
           return the median value on a heap of 5 raw datas
        """
        filtered_datas = []
        for queue, data in zip(self._raw_data_queues, datas):
            queue.pop(0)
            queue.append(data)
            filtered_datas.append(sorted(queue)[2])
        return filtered_datas

    def _ping(self, address, data=None):
        d = data if data is not None else self.results_type['centimeters']
        while 1:
            try:
                self.i2c.write_byte_data(address, 0, d)
                break
            except IOError:
                time.sleep(0.005)
                self.__errors += 1
                continue

    def _read(self, address, reg=2):
        while 1:
            try:
                return int(self.i2c.read_word_data(address, reg)) / 256
            except IOError:
                time.sleep(0.005)
                self.__errors += 1
                continue

 if __name__ == '__main__':
	from pylab import plot
	i2c = smbus.SMBus(1)
	sonar = Sonar(i2c)

	d = []
	t = [time.time()]
	for _ in range(1000):
	    sonar.update()
	    d.append(sonar.datas[0])
	    t.append(time.time() - t[0])
	plot(t[1:], d)
