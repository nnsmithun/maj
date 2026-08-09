from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel


def create_topology():
    net = Mininet(
        controller=None,
        switch=OVSSwitch
    )

    # Add remote OS-Ken controller
    controller = net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6653
    )

    # Add one OpenFlow switch
    s1 = net.addSwitch('s1')

    # Add two hosts
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')

    # Connect hosts to switch
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    # Start the network
    net.start()

    # Open Mininet CLI
    CLI(net)

    # Stop the network when we exit the CLI
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    create_topology()