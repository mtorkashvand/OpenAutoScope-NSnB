#! python
#
# Copyright 2021
# Author: Vivek Venkatachalam, Mahdi Torkashvand
#
# This is a convertor of messages from the PROCESSOR
# into stage commands for Zaber stages.
# Author: Vivek Venkatachalam, Mahdi Torkashvand

"""
This converts raw controller output to discrete events.

Usage:
    commands.py             [options]

Options:
    -h --help               Show this help.
    --inbound=HOST:PORT     Connection for inbound messages.
                                [default: L6001]
    --outbound=HOST:PORT    Connection for outbound messages.
                                [default: 6002]
    --console               Stream to stdout.
"""

import time
import signal
from typing import Tuple

from docopt import docopt

from wormtracker_scope.zmq.publisher import Publisher
from wormtracker_scope.zmq.subscriber import Subscriber
from wormtracker_scope.zmq.utils import parse_host_and_port

class XboxStageCommands():

    def __init__(self,
                 inbound: Tuple[str, int],
                 outbound: Tuple[str, int]):

        self.subscriber = Subscriber(inbound[1],
                                     inbound[0],
                                     inbound[2])

        self.publisher = Publisher(outbound[1],
                                   outbound[0],
                                   outbound[2])

        buttons = [
            b"X pressed", b"Y pressed", b"B pressed",
            b"A pressed",
            b"dpad_up pressed", b"dpad_up released",
            b"dpad_down pressed", b"dpad_down released",
            b"dpad_right pressed", b"dpad_left pressed",
            b"right_stick", b"left_stick",
            b"left_shoulder pressed", b"right_shoulder pressed"
            ]

        self.subscriber.remove_subscription("")
        for button in buttons:
            self.subscriber.add_subscription(button)

    def run(self):
        def _finish(*_):
            raise SystemExit

        signal.signal(signal.SIGINT, _finish)

        while True:
            message = self.subscriber.recv_last_string()

            if message is None:
                time.sleep(0.01)
                continue

            tokens = message.split(" ")
            if message == "B pressed":
                self.publish("hub _writer_toggle")
            
            elif message == "X pressed":
                self.publish("hub _teensy_commands_toggle_led1")
                self.publish("hub _teensy_commands_toggle_led2")

            elif message == "Y pressed":
                self.publish("hub _teensy_commands_toggle_laser")

            elif message == "left_shoulder pressed":
                self.publish("hub _teensy_commands_change_vel_z -1")

            elif message == "right_shoulder pressed":
                self.publish("hub _teensy_commands_change_vel_z 1")

            elif message == "dpad_right pressed":
                self.publish("hub _tracker_change_threshold 1")

            elif message == "dpad_left pressed":
                self.publish("hub _tracker_change_threshold -1")

            elif message == "A pressed":
                self.publish("hub _tracker_toggle_tracking")

            elif message == "dpad_up pressed":
                self.publish("teensy_commands start_z_move 1")

            elif message == "dpad_up released":
                self.publish("teensy_commands movez 0")

            elif message == "dpad_down pressed":
                self.publish("teensy_commands start_z_move -1")

            elif message == "dpad_down released":
                self.publish("teensy_commands movez 0")

            elif tokens[0] == "left_stick":
                xspeed = int(tokens[1]) // 50
                yspeed = int(tokens[2]) // 50
                self.publish("teensy_commands movey {}".format(yspeed))
                self.publish("teensy_commands movex {}".format(-xspeed))

            elif tokens[0] == "right_stick":
                xspeed = int(tokens[1])
                yspeed = int(tokens[2])
                self.publish("teensy_commands movey {}".format(yspeed))
                self.publish("teensy_commands movex {}".format(-xspeed))

            else:
                print("Unexpected message received: ", message)

    def publish(self, verb, *args):
        command = verb
        for arg in args:
            command += " " + str(arg)
        self.publisher.send(command)

def main():
    """CLI entry point."""
    arguments = docopt(__doc__)

    inbound = parse_host_and_port(arguments["--inbound"])
    outbound = parse_host_and_port(arguments["--outbound"])

    processor = XboxStageCommands(inbound, outbound)

    processor.run()

if __name__ == "__main__":
    main()






