from test import *
import sys


def create_base(size):
    GPLC = nx.Graph()
    GNPLC = nx.Graph()
    
    AGW = NetDevice("99.99.99.99", dict(), 22, "Gateway", DevType.ROUTER)
    
    GPLC.add_node(AGW)
    GNPLC.add_node(AGW)

    GPLC_node_list = [AGW]
    GPLC_edge_list = []
    
    GNPLC_node_list = [AGW]
    GNPLC_edge_list = []
    

    for n in range(1, size):

        subnetPLC = graph_creation(n)
        subnetNPLC = graph_creation(n, False)

        xePLC = [x.label for x in subnetPLC.nodes()]
        xeNPLC = [x.label for x in subnetNPLC.nodes()]
        
        GPLC_node_list.extend(subnetPLC.nodes())
        GPLC_edge_list.extend(subnetPLC.edges.data())
            
        GPLC_node_list.extend(subnetPLC.nodes())
        GPLC_edge_list.extend(subnetPLC.edges.data())


        
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
            setup="from __main__ import create_base\nfrom test import find_connections\ng, ml=create_base({})".format(i),
            stmt="find_connections(g)",
            number=1)
        time_taken2[0] = timeit.timeit(
            setup="from __main__ import create_base\nfrom test import skeleton\ng, ml=create_base({})\nprint(ml)".format(i),
            stmt="skeleton(g, ml)",
            number=1)

        time_taken1[1] = timeit.timeit(
            setup=
            "from __main__ import create_base\nfrom test import find_connections\ng, ml=create_base({})".format(i),
            stmt="find_connections(g)",
            number=1)
        time_taken2[1] = timeit.timeit(
            setup=
            "from __main__ import create_base\nfrom test import skeleton\ng, ml=create_base({})\nprint(ml)".format(i),
            stmt="skeleton(g, ml)",
            number=1)

        time1 = sum(time_taken1) / len(time_taken1)
        time2 = sum(time_taken2) / len(time_taken2)

        times1.append(time1)
        times2.append(time2)

        print(i, time1, time2)

    import matplotlib.pyplot as plt

    plt.plot(times1, 'r-', label="Old Algorithm")
    plt.plot(times2, 'b-', label="Improved Algorithm")
    plt.legend(loc='upper right')
    plt.xlabel("Number of nodes/subnets")
    plt.ylabel("Time taken")

    plt.show()