from test import *


def create_base(size):
    G = nx.Graph()
    AGW = NetDevice("99.99.99.99", dict(), 22, "Gateway", DevType.ROUTER)
    G.add_node(AGW)
    node_list = [AGW]
    edge_list = []

    for n in range(1, size):
        subnet = graph_creation(n)
        # print(nx.get_edge_attributes(subnet, ))
        xe = [x.label for x in subnet.nodes()]
        # print(xe)
        node_list.extend(subnet.nodes())
        edge_list.extend(subnet.edges.data())
        G.add_nodes_from(subnet.nodes())
        
        # for s in G.edges():
        #     print(s[0].label, s[1].label)

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

# print(timeit.timeit(setup="from __main__ import create_base\nfrom test import find_connections\ng=create_base({})".format(6), stmt="find_connections(g)", number=2))


# if __name__ == '__main__':

times1 = []
times2 = []
time_taken1 = [0, 0]
time_taken2 = [0, 0]


for i in range(2, 12):
    
    time_taken1[0] = timeit.timeit(setup="from __main__ import create_base\nfrom test import find_connections\ng, ml=create_base({})".format(i), stmt="find_connections(g)", number=1)
    time_taken2[0] = timeit.timeit(setup="from __main__ import create_base\nfrom test import Skeleton\ng, ml=create_base({})\nprint(ml)".format(i), stmt="Skeleton(g, ml)", number=1)

    time_taken1[1] = timeit.timeit(setup="from __main__ import create_base\nfrom test import find_connections\ng, ml=create_base({})".format(i), stmt="find_connections(g)", number=1)
    time_taken2[1] = timeit.timeit(setup="from __main__ import create_base\nfrom test import Skeleton\ng, ml=create_base({})\nprint(ml)".format(i), stmt="Skeleton(g, ml)", number=1)
    
    time1 = sum(time_taken1)/len(time_taken1)
    time2 = sum(time_taken2)/len(time_taken2)

    times1.append(time1)
    times2.append(time2)

    print(i, time1, time2)

import matplotlib.pyplot as plt

plt.plot(times1, 'r-', times2, 'b-')
plt.show()