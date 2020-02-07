#!/usr/bin/python3
# Script to instantiate and pull message traces out of core emulator session
# Make sure this is run with sudo
# Needs sudo to run core daemon

import logging
import time
from builtins import range
import sys
import codecs



from core.emulator.coreemu import CoreEmu
from core.emulator.emudata import IpPrefixes, NodeOptions
from core.emulator.enumerations import EventTypes, NodeTypes

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

#Duration defines how many seconds to capture packets for
def example(duration):
    # ip generator for example
    prefixes = IpPrefixes("200.66.12.0/16")

    # create emulator instance for creating sessions and utility methods
#    coreemu = globals()["coreemu"] # use this line when running this script from gui
    coreemu = CoreEmu() # OR use this when running this script from cmdline

    session = coreemu.create_session()

    # must be in configuration state for nodes to start, when using "node_add" below
    session.set_state(EventTypes.CONFIGURATION_STATE)

    
#define options that will be used to create router
    opts1 = NodeOptions(name="rt1", model = "router")
    opts1.set_position(50+275,100)
    opts1.services=["zebra","OSPFv2"]# Zebra seems to be required to run OSPF
    
    router1 = session.add_node(node_options = opts1)


    opts2 = NodeOptions(name="rt2", model = "router")
    opts2.services=["zebra","OSPFv2"] # Zebra seems to be required to run OSPF
    opts2.set_position(50+(275*2),200)

    router2 = session.add_node(node_options = opts2)

    rt_interface1 = prefixes.create_interface(router1)
    rt_interface2 = prefixes.create_interface(router2)    
    session.add_link(router1.id, router2.id,interface_one=rt_interface1, interface_two=rt_interface2)
    


    
    print("instantiate session...")    
    # instantiate session
    session.instantiate()
    print("session instantiated!")    

# there is a little bit of documentation to be found in
# interactive python3 with: help(core.nodes.base)

#    router1.cmd(["command","-flag1","-flag2"])
#    router1.check_cmd(["command","-flag1","-flag2"])
#    router1.cmd_output(['tshark','-f',"'ip proto ospf'"])
    print("run check_cmd tshark, for ", duration, ' seconds')    
    out = router1.check_cmd(["tshark","-f",str("ip proto ospf"),"-a",str("duration:"+str(duration))])
# I don't think we need to sleep as it seems to wait for tshark to finish
# I was hoping we would be able to run a few in parallel.
# That may be possible by running each tshark instance on different nodes


    print("=============================================================")
    print()
    print(out)
    packets = []
    out = out.split('\n')
    for line in out:
        temp = line.split(' ')
        if len(temp) > 7:
            packets.append(str(temp[-2]+temp[-1]+', '+temp[-10]+', '+temp[-8]))
    packets = packets[:-1]
    print(packets)
#   the structure of the file is: Packet Type, Source, Destination
#   Note that the 224... addresses are a multicast
    with open('message_trace.txt', 'w') as f:
        for i in packets:
            f.write(str(i+'\n'))
        

    coreemu.shutdown()
    
    

if __name__ in {"__main__", "__builtin__"}:
    logging.basicConfig(level=logging.INFO)
    example(45)
# example(duration)
# where duration is how long to capture packets for in seconds
