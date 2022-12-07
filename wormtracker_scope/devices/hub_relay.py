#! python
#
# Copyright 2022
# Author: Mahdi Torkashvand, Vivek Venkatachalam

"""
This handles commands involving multiple devices.

Usage:
    hub_relay.py                        [options]

Options:
    -h --help                           Show this help.
    --server=PORT                        Connection with the clinet.
                                            [default: 5002]
    --inbound=PORT                      Incoming from forwarder.
                                            [default: L5001]
    --outbound=PORT                     outgoing to forwarder.
                                            [default: L5000]
    --name=NAME                         device name.
                                            [default: hub]
    
"""

import time

from docopt import docopt

from wormtracker_scope.zmq.hub import Hub
from wormtracker_scope.zmq.utils import parse_host_and_port

class WormTrackerHub(Hub):
    """This is a central hub that is responsible for subscribing and publishing
    messages to all components of Lambda. Clients controlling the microscope
    should communicate only with this."""
    def __init__(
            self,
            inbound,
            outbound,
            server,
            name="hub"):

        Hub.__init__(self, inbound, outbound, server, name)

    def shutdown(self):
        self._displayer_shutdown()
        self._writer_shutdown()
        self._flir_camera_shutdown()
        self._data_hub_shutdown()
        self._tracker_shutdown()
        self._writer_shutdown()
        self._displayer_shutdown()
        self._teensy_commands_shutdown()
        time.sleep(0.5)
        self._logger_shutdown()
        self.running = False

    def _logger_shutdown(self):
        self.send("logger shutdown")

    def _displayer_set_shape(self, y, x):
        self.send("displayer set_shape {} {}".format(y, x))

    def _displayer_shutdown(self):
        self.send("displayer shutdown")

    def _data_hub_set_shape(self, z, y, x):
        self.send("data_hub set_shape {} {}".format(y, x))

    def _data_hub_shutdown(self):
        self.send("data_hub shutdown")

    def _flir_camera_start(self):
        self.send("FlirCamera start")

    def _flir_camera_stop(self):
        self.send("FlirCamera stop")

    def _flir_camera_shutdown(self):
        self.send("FlirCamera shutdown")

    def _flir_camera_set_exposure(self, exposure, rate):
        self.send("FlirCamera set_exposure {} {}".format(exposure, rate))
        time.sleep(1)
        self._flir_camera_start()

    def _flir_camera_set_height(self, height):
        self.send("FlirCamera set_height {}".format(height))

    def _flir_camera_set_width(self, width):
        self.send("FlirCamera set_width {}".format(width))

    def _tracker_change_threshold(self, dir_sign):
        self.send("tracker change_threshold {}".format(dir_sign))

    def _tracker_toggle_tracking(self):
        self.send("tracker toggle_tracking")

    def _tracker_shutdown(self):
        self.send("tracker shutdown")

    def _writer_start(self):
        self.send("writer start")

    def _writer_stop(self):
        self.send("writer stop")

    def _writer_toggle(self):
        self.send("writer toggle")

    def _writer_set_shape(self, y, x):
        self.send("writer set_shape {} {}".format(y, x))

    def _writer_shutdown(self):
        self.send("writer shutdown")

    def _teensy_commands_toggle_led1(self):
        self.send("teensy_commands toggle_led1")

    def _teensy_commands_toggle_led2(self):
        self.send("teensy_commands toggle_led2")

    def _teensy_commands_toggle_laser(self):
        self.send("teensy_commands toggle_laser")

    def _teensy_commands_movex(self, xvel):
        self.send("teensy_commands movex {}".format(xvel))

    def _teensy_commands_movey(self, yvel):
        self.send("teensy_commands movey {}".format(yvel))

    def _teensy_commands_movez(self, zvel):
        self.send("teensy_commands movez {}".format(zvel))

    def _teensy_commands_change_vel_z(self, dir_sign):
        self.send("teensy_commands change_vel_z {}".format(dir_sign))

    def _teensy_commands_disable(self):
        self.send("teensy_commands disable")

    def _teensy_commands_enable(self):
        self.send("teensy_commands enable")

    def _teensy_commands_shutdown(self):
        self.send("teensy_commands shutdown")

def main():
    """This is the hub for lambda."""
    arguments = docopt(__doc__)

    scope = WormTrackerHub(
        inbound=parse_host_and_port(arguments["--inbound"]),
        outbound=parse_host_and_port(arguments["--outbound"]),
        server=int(arguments["--server"]),
        name=arguments["--name"])

    scope.run()

if __name__ == "__main__":
    main()
