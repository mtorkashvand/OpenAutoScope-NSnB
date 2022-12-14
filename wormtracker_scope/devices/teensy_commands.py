"""
This communicates with the teensy board.
Usage:
    teensy_commands.py          [options]

Options:
    -h --help                   Show this help.
    --inbound=HOST:PORT         Socket address to receive commands.
                                    [default: localhost:5001]
    --outbound=HOST:PORT        Socket address to publish status.
                                    [default: localhost:5000]
    --port=<PORT>               USB port.
                                    [default: COM4]
"""

import json
import time
from typing import Tuple

import numpy as np
from serial import Serial
from docopt import docopt

from wormtracker_scope.zmq.publisher import Publisher
from wormtracker_scope.zmq.subscriber import ObjectSubscriber
from wormtracker_scope.zmq.utils import parse_host_and_port

class TeensyCommandsDevice():
    """This device sends serial commands to the teensy board."""


    _COMMANDS = {
        "set_led1":"l1{led_status}\n",
        "set_led2":"l2{led_status}\n",
        "set_laser":"L{laser_status}\n",
        "vx":"vx{xvel}\n",
        "vy":"vy{yvel}\n",
        "vz":"vz{zvel}\n",
        "disable":"q\n",
        "enable":"e\n"
        }

    def __init__(
            self,
            inbound: Tuple[str, int, bool],
            outbound: Tuple[str, int, bool],
            port,
            name="teensy_commands",):

        self.status = {}
        self.port = port
        self.is_port_open = 0
        self.name = name
        self.device_status = 1
        self.zspeed = 1
        self.led1_status = 0
        self.led2_status = 0
        self.laser_status = 0

        self.command_subscriber = ObjectSubscriber(
            obj=self,
            name=name,
            host=inbound[0],
            port=inbound[1],
            bound=inbound[2])

        self.status_publisher = Publisher(
            host=outbound[0],
            port=outbound[1],
            bound=outbound[2])

        try:
            self.serial_obj = Serial(port=self.port, baudrate=115200, timeout=0)
            self.is_port_open = self.serial_obj.is_open
        except Exception as e:
            print (e)
            return

        self.enable()
        self.set_led1(0)
        self.set_led2(0)
        self.set_laser(0)

    def set_led1(self, led_status):
        self._execute("set_led1", led_status=led_status)

    def toggle_led1(self):
        new_status = not self.led1_status
        self.set_led1(int(new_status))
        self.led1_status = new_status
    
    def set_led2(self, led_status):
        self._execute("set_led2", led_status=led_status)

    def toggle_led2(self):
        new_status = not self.led2_status
        self.set_led2(int(new_status))
        self.led2_status = new_status

    def set_laser(self, laser_status):
        self._execute("set_laser", laser_status=laser_status)

    def toggle_laser(self):
        new_status = not self.laser_status
        self.set_laser(int(new_status))
        self.laser_status = new_status

    def movex(self, xvel):
        self._execute("vx", xvel=xvel)

    def movey(self, yvel):
        self._execute("vy", yvel=yvel)

    def movez(self, zvel):
        self._execute("vz", zvel=zvel)

    def update_position(self):
        self.status_publisher.send("logger "+ json.dumps({"position": [self.x, self.y, self.z]}, default=int))

    def disable(self):
        self._execute("disable")

    def enable(self):
        self._execute("enable")

    def change_vel_z(self, sign):
        self.zspeed = int(np.clip(self.zspeed * 2 ** sign, 1, 1024))
        print("zspeed is: {}   ".format(self.zspeed), end="\r")

    def start_z_move(self, sign):
        self.movez(sign * self.zspeed)

    def shutdown(self):
        self.device_status = 0
        self.set_led1(0)
        self.set_led2(0)
        self.set_laser(0)
        self.disable()
        self.serial_obj.close()
        self.serial_obj.__del__()

    def _execute(self, cmd: str, **kwargs):
        cmd_format_string = self._COMMANDS[cmd]
        formatted_string = cmd_format_string.format(**kwargs)
        reply = b''
        self.serial_obj.write(bytes(formatted_string, "ascii"))
        while not reply:
            reply = self.serial_obj.readline()
        pos = reply.decode("utf-8")[:-1].split(" ")
        self.x, self.y, self.z = [int(coord) for coord in pos]
        self.update_position()

    def run(self):
        """Starts a loop and receives and processes a message."""
        self.command_subscriber.flush()
        while self.device_status:
            req = self.command_subscriber.recv()
            self.command_subscriber.process(req)




def main():
    """Create and start DragonflyDevice."""

    arguments = docopt(__doc__)

    device = TeensyCommandsDevice(
        inbound=parse_host_and_port(arguments["--inbound"]),
        outbound=parse_host_and_port(arguments["--outbound"]),
        port=arguments["--port"])

    if device is not None:
        device.run()

if __name__ == "__main__":
    main()