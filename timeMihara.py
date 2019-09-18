from test import *
import sys


def create_base(size):
    G = nx.Graph()
    AGW = NetDevice("99.99.99.99", dict(), 22, "Gateway", DevType.ROUTER)
    G.add_node(AGW)
    node_list = [AGW]
    edge_list = []

    for n in range(1, size):
        subnet = graph_creation(n)
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
    populate_AFT(G)

    masterLabels = []
    for port in AGW.pm.keys():
        masterLabels.extend(AGW.pm[port])

    print(len(G.edges()))
    return G, masterLabels


if __name__ == '__main__':

    times1 = []
    times2 = []
    time_taken1 = [0, 0]
    time_taken2 = [0, 0]

    for i in range(2, int(sys.argv[1])):

        time_taken1[0] = timeit.timeit(
            setup="from __main__ import create_base\nfrom test import skeleton\ng, ml=create_base({})".format(i),
            stmt="skeleton(g, ml)",
            number=1)
        time_taken2[0] = timeit.timeit(
            setup="from __main__ import create_base\nfrom test import skeleton\ng, ml=create_base({})\nprint(ml)".format(i),
            stmt="skeleton(g, ml)",
            number=1)

        time1 = sum(time_taken1) / len(time_taken1)

        times1.append(time1)

        print(i, time1)

    import matplotlib.pyplot as plt

    plt.plot(times1, 'r-', label="Mihara's Alogorithm")
    plt.legend(loc='upper right')
    plt.xlabel("Number of nodes/subnets")
    plt.ylabel("Time taken")

    plt.show()