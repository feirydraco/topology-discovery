import matplotlib.pyplot as plt

import networkx as nx
import timeit
import sys
from Devices import *

from utlities import *

if __name__ == '__main__':
    G = nx.Graph()

    AGW = NetDevice("99.99.99.99", dict(), 22, "Gateway", DevType.ROUTER)

    G.add_node(AGW)

    node_list = [AGW]
    edge_list = []

    for n in range(1, int(sys.argv[1])):
        subnet = graph_creation(n, False)
        xe = [x.label for x in subnet.nodes()]
        node_list.extend(subnet.nodes())
        edge_list.extend(subnet.edges.data())
        G.add_nodes_from(subnet.nodes())

        G.add_edges_from(subnet.edges.data())
        connection_node = [
            node for node in subnet.nodes()
            if node.label == "FloorRouter{}".format(n - 1)
        ]
        floorRouter = connection_node[0]

        AGW.pm[n - 1] = "{}".format(n - 1)
        floorRouter.pm[int("1{}".format(n - 1))] = "999{}".format(n - 1)
        G.add_edge(AGW, floorRouter)

        G.edges[AGW, floorRouter][AGW] = n - 1
        G.edges[AGW, floorRouter][floorRouter] = int("1{}".format(n - 1))
    
    show_graph(G.nodes(), G.edges(), "Original Network")
    
    populate_AFT(G)

    discovered_edges = find_connections(G)
    discovered_nodes = [
        node.label for node in G.nodes() if not node.dtype == DevType.APPLIANCE
    ]
    
    # print_AFT(G)
    
    show_graph(discovered_nodes, discovered_edges, "Breitbart")

    internal_edges = [
        edge for edge in G.edges
        if (not edge[0].dtype == DevType.APPLIANCE) and (
            not edge[1].dtype == DevType.APPLIANCE)
    ]
    internal_nodes = [
        node for node in G.nodes if not node.dtype == DevType.APPLIANCE
    ]

    masterLabels = []
    for port in AGW.pm.keys():
        masterLabels.extend(AGW.pm[port])

    internal_edges = skeleton(G, masterLabels)
    internal_nodes = [
        node for node in G.nodes if not node.dtype == DevType.APPLIANCE
    ]

    show_graph(internal_nodes, internal_edges, "Mihara")

    plt.show()
