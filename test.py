import matplotlib.pyplot as plt
import networkx as nx


class Device:
    def __init__(self, ip, mac, did):
        self.ip = ip
        self.mac = mac
        self.did = did


class NetDevice:
    def __init__(self, ip, pm, did, dtype="Undefined"):
        self.ip = ip
        self.pm = pm
        self.did = did
        self.dtype = dtype
        self.aft = {}
    
    def getAFT(self):
        pass


if __name__ == '__main__':
    tv = Device(2, 2, 1)
    phone = Device(3, 2, 2)
    switch = NetDevice(44, {1: 100, 2: 100, 3: 101}, 3, "Switch")
    router = NetDevice(45, {1: 200}, 4, "Router")
    edge_list = [(tv, switch), (phone, switch), (switch, router)]

    G = nx.Graph()
    G.add_node(tv)
    G.add_node(phone)
    G.add_node(switch)
    G.add_node(router)

    G.add_edge(tv, switch)
    G[tv][switch]['con'] = (-1, 1)
    G.add_edge(phone, switch)
    G[phone][switch]['con'] = (-1, 2)
    G.add_edge(switch, router)
    G[switch][router]['con'] = (3, 1)

    pos = nx.spring_layout(G)

    nx.draw_networkx_nodes(G,
                           pos,
                           nodelist=[tv, phone, switch],
                           node_color='pink',
                           node_size=750,
                           alpha=0.8)

    nx.draw_networkx_nodes(G,
                           pos,
                           nodelist=[router],
                           node_color='pink',
                           node_size=600,
                           alpha=0.8)

    nx.draw_networkx_edges(G,
                           pos,
                           edgelist=edge_list,
                           width=2,
                           alpha=0.5,
                           edge_color='black')

    labels = {}
    labels[tv] = 'TV'
    labels[router] = 'Router'
    labels[switch] = 'Switch'
    labels[phone] = 'Phone'
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color=(0, 0, 0))
    nx.draw_networkx_edge_labels(G,
                                 pos, {
                                     (tv, switch): G[tv][switch]['con'],
                                     (phone, switch): G[phone][switch]['con'],
                                     (switch, router): G[switch][router]['con']
                                 },
                                 font_size=8,
                                 font_color=(1, 0.2, 0.4))
    plt.show()
