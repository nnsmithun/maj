from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info


CONTROLLER_IP = '127.0.0.1'
CONTROLLER_PORT = 6653


def create_topology():

    net = Mininet(
        controller=None,
        switch=OVSSwitch,
        autoSetMacs=True
    )

    # --------------------------------------------------
    # Remote OS-Ken Controller
    # --------------------------------------------------

    net.addController(
        'c0',
        controller=RemoteController,
        ip=CONTROLLER_IP,
        port=CONTROLLER_PORT
    )

    # --------------------------------------------------
    # OpenFlow Switch
    # --------------------------------------------------

    s1 = net.addSwitch(
        's1',
        protocols='OpenFlow13'
    )

    # --------------------------------------------------
    # Victim / Web Server
    # --------------------------------------------------

    server = net.addHost(
        'hserver',
        ip='10.0.0.100/24'
    )

    # --------------------------------------------------
    # Legitimate Users
    # --------------------------------------------------

    user1 = net.addHost(
        'huser1',
        ip='10.0.0.101/24'
    )

    user2 = net.addHost(
        'huser2',
        ip='10.0.0.102/24'
    )

    # --------------------------------------------------
    # Controlled Traffic Hosts
    #
    # These are NOT permanently assigned to an attack
    # class. They can be reused in different experiments.
    # --------------------------------------------------

    bot1 = net.addHost(
        'hbot1',
        ip='10.0.0.201/24'
    )

    bot2 = net.addHost(
        'hbot2',
        ip='10.0.0.202/24'
    )

    bot3 = net.addHost(
        'hbot3',
        ip='10.0.0.203/24'
    )

    bot4 = net.addHost(
        'hbot4',
        ip='10.0.0.204/24'
    )

    bot5 = net.addHost(
        'hbot5',
        ip='10.0.0.205/24'
    )

    bot6 = net.addHost(
        'hbot6',
        ip='10.0.0.206/24'
    )

    bot7 = net.addHost(
        'hbot7',
        ip='10.0.0.207/24'
    )

    # --------------------------------------------------
    # Links
    # --------------------------------------------------

    net.addLink(server, s1)

    net.addLink(user1, s1)
    net.addLink(user2, s1)

    net.addLink(bot1, s1)
    net.addLink(bot2, s1)
    net.addLink(bot3, s1)
    net.addLink(bot4, s1)
    net.addLink(bot5, s1)
    net.addLink(bot6, s1)
    net.addLink(bot7, s1)

    # --------------------------------------------------
    # Start network
    # --------------------------------------------------

    net.start()

    info('\n')
    info('==============================================\n')
    info('       MAJOR ONE - PHASE 3 TOPOLOGY\n')
    info('==============================================\n')

    info('Controller : OS-Ken\n')
    info('OpenFlow   : 1.3\n')
    info('Switch     : s1\n')
    info('\n')

    info('Victim Server:\n')
    info('  hserver    10.0.0.100\n')

    info('\nLegitimate Users:\n')
    info('  huser1     10.0.0.101\n')
    info('  huser2     10.0.0.102\n')

    info('\nTraffic Hosts:\n')
    info('  hbot1      10.0.0.201\n')
    info('  hbot2      10.0.0.202\n')
    info('  hbot3      10.0.0.203\n')
    info('  hbot4      10.0.0.204\n')
    info('  hbot5      10.0.0.205\n')
    info('  hbot6      10.0.0.206\n')
    info('  hbot7      10.0.0.207\n')

    info('\n==============================================\n')
    info('Website target: 10.0.0.100\n')
    info('==============================================\n')
    info('\n')

    # --------------------------------------------------
    # Open Mininet CLI
    # --------------------------------------------------

    CLI(net)

    # --------------------------------------------------
    # Stop network
    # --------------------------------------------------

    net.stop()


if __name__ == '__main__':

    setLogLevel('info')

    create_topology()