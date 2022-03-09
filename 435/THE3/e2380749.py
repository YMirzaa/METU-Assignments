#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    def build(self, **_opts):
        # Add 3 routers in two different subnets
        router1 = self.addHost('Router1', cls=LinuxRouter, ip='10.0.0.1/24')
        router2 = self.addHost('Router2', cls=LinuxRouter, ip='10.1.0.1/24')
        router3 = self.addHost('Router3', cls=LinuxRouter, ip='10.0.1.1/24')

        # Add 3 switches
        switch1 = self.addSwitch('switch1')
        switch2 = self.addSwitch('switch2')
        switch3 = self.addSwitch('switch3')

        # Add host-switch links in the same subnet
        self.addLink(switch1,
                     router1,
                     intfName2='r1-eth1',
                     params2={'ip': '10.0.0.1/24'})

        self.addLink(switch2,
                     router2,
                     intfName2='r2-eth1',
                     params2={'ip': '10.1.0.1/24'})        
        self.addLink(switch3,
                     router3,
                     intfName2='r3-eth1',
                     params2={'ip': '10.0.1.1/24'})

        # Add router-router link in a new subnet for the router-router connection
        self.addLink(router1,
                     router2,
                     intfName1='r1-eth2',
                     intfName2='r2-eth2',
                     params1={'ip': '10.100.0.1/24'},
                     params2={'ip': '10.100.0.2/24'})
        
        self.addLink(router1,
                     router3,
                     intfName1='r1-eth3',
                     intfName2='r3-eth2',
                     params1={'ip': '10.200.0.1/24'},
                     params2={'ip': '10.200.0.2/24'})
        
        self.addLink(router2,
                     router3,
                     intfName1='r2-eth3',
                     intfName2='r3-eth3',
                     params1={'ip': '10.150.0.1/24'},
                     params2={'ip': '10.150.0.2/24'})

        
        # Adding hosts specifying the default route
        ezekiel = self.addHost(name='ezekiel',
                          ip='10.0.0.199/24',
                          defaultRoute='via 10.0.0.1')

        frank = self.addHost(name='frank',
                          ip='10.0.0.250/24',
                          defaultRoute='via 10.0.0.1')
        
        bob = self.addHost(name='bob',
                          ip='10.0.0.251/24',
                          defaultRoute='via 10.0.0.1')


        alice = self.addHost(name='alice',
                          ip='10.1.0.144/24',
                          defaultRoute='via 10.1.0.1')

        hannah = self.addHost(name='hannah',
                          ip='10.1.0.201/24',
                          defaultRoute='via 10.1.0.1')


        evilCorp = self.addHost(name='evilCorp',
                          ip='10.0.1.101/24',
                          defaultRoute='via 10.0.1.1')
        
        # Add host-switch links
        self.addLink(ezekiel, switch1)
        self.addLink(frank, switch1)
        self.addLink(bob, switch1)

        self.addLink(alice, switch2)
        self.addLink(hannah, switch2)

        self.addLink(evilCorp, switch3)

    def run():
        topo = NetworkTopo()
        net = Mininet(topo=topo)

        # Add routing for reaching networks that aren't directly connected
        info(net['router1'].cmd("ip route add 10.1.0.0/24 via 10.100.0.2 dev r1-eth2"))
        info(net['router1'].cmd("ip route add 10.0.1.0/24 via 10.200.0.2 dev r1-eth3"))

        info(net['router2'].cmd("ip route add 10.0.0.0/24 via 10.100.0.1 dev r2-eth2"))
        info(net['router2'].cmd("ip route add 10.0.1.0/24 via 10.150.0.2 dev r2-eth3"))

        info(net['router3'].cmd("ip route add 10.0.0.0/24 via 10.200.0.1 dev r3-eth2"))
        info(net['router3'].cmd("ip route add 10.1.0.0/24 via 10.150.0.1 dev r3-eth3"))

        net.start()
        CLI(net)
        net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()