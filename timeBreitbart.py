from test import *
import sys


def create_base(size):
    GPLC = nx.Graph()
    GNPLC = nx.Graph()
    
    AGW_PLC = NetDevice("99.99.99.99", dict(), 22, "Gateway", DevType.ROUTER)
    AGW_NPLC = NetDevice("99.99.99.99", dict(), 22, "Gateway", DevType.ROUTER)
    
    GPLC.add_node(AGW_PLC)
    GNPLC.add_node(AGW_NPLC)

    GPLC_node_list = [AGW_PLC]
    GPLC_edge_list = []
    
    GNPLC_node_list = [AGW_NPLC]
    GNPLC_edge_list = []
    

    for n in range(1, size):

        subnetPLC = graph_creation(n)
        subnetNPLC = graph_creation(n, False)

        #DEBUG
        #xePLC = [x.label for x in subnetPLC.nodes()]
        #xeNPLC = [x.label for x in subnetNPLC.nodes()]
        
        GPLC_node_list.extend(subnetPLC.nodes())
        GPLC_edge_list.extend(subnetPLC.edges.data())
            
        GPLC_node_list.extend(subnetPLC.nodes())
        GPLC_edge_list.extend(subnetPLC.edges.data())
        
        GPLC.add_nodes_from(subnetPLC.nodes())
        GNPLC.add_nodes_from(subnetNPLC.nodes())

        GPLC.add_edges_from(subnetPLC.edges.data())
        GNPLC.add_edges_from(subnetNPLC.edges.data())

        connection_nodePLC = [
            node for node in subnetPLC.nodes()
            if node.label == "FloorRouter{}".format(n - 1)
        ]
        connection_nodeNPLC = [
            node for node in subnetNPLC.nodes()
            if node.label == "FloorRouter{}".format(n - 1)
        ]

        floorRouterPLC = connection_nodePLC[0]
        floorRouterNPLC = connection_nodeNPLC[0]

        AGW_PLC.pm[n - 1] = "{}".format(n - 1)
        AGW_NPLC.pm[n - 1] = "{}".format(n - 1)
        

        floorRouterPLC.pm[int("1{}".format(n - 1))] = "999{}".format(n - 1)
        floorRouterNPLC.pm[int("1{}".format(n - 1))] = "999{}".format(n - 1)
        
        GPLC.add_edge(AGW_PLC, floorRouterPLC)
        GNPLC.add_edge(AGW_NPLC, floorRouterNPLC)

        GPLC.edges[AGW_PLC, floorRouterPLC][AGW_PLC] = n - 1
        GNPLC.edges[AGW_NPLC, floorRouterNPLC][AGW_NPLC] = n - 1

        GPLC.edges[AGW_PLC, floorRouterPLC][floorRouterPLC] = int("1{}".format(n - 1))
        GNPLC.edges[AGW_NPLC, floorRouterNPLC][floorRouterNPLC] = int("1{}".format(n - 1))
    
    populate_AFT(GPLC)
    populate_AFT(GNPLC)

    masterLabelsPLC = []
    masterLabelsNPLC = []

    for port in AGW_PLC.pm.keys():
        masterLabelsPLC.extend(AGW_PLC.pm[port])

    for port in AGW_NPLC.pm.keys():
        masterLabelsNPLC.extend(AGW_NPLC.pm[port])

    return GPLC, masterLabelsPLC, GNPLC, masterLabelsNPLC


if __name__ == '__main__':

    times1 = []
    times2 = []
    time_taken1 = [0, 0]
    time_taken2 = [0, 0]

    for i in range(2, int(sys.argv[1])):

        time_taken1[0] = timeit.timeit(
            setup="from __main__ import create_base\nfrom test import find_connections\ng_plc, ml_plc, g_nplc, ml_nplc=create_base({})".format(i),
            stmt="find_connections(g_plc)",
            number=1)
        time_taken2[0] = timeit.timeit(
            setup="from __main__ import create_base\nfrom test import find_connections\ng_plc, ml_plc, g_nplc, ml_nplc=create_base({})".format(i),
            stmt="find_connections(g_nplc)",
            number=1)

        time_taken1[1] = timeit.timeit(
            setup="from __main__ import create_base\nfrom test import find_connections\ng_plc, ml_plc, g_nplc, ml_nplc=create_base({})".format(i),
            stmt="find_connections(g_plc)",
            number=1)
        time_taken2[1] = timeit.timeit(
            setup="from __main__ import create_base\nfrom test import find_connections\ng_plc, ml_plc, g_nplc, ml_nplc=create_base({})".format(i),
            stmt="find_connections(g_nplc)",
            number=1)

        time1 = sum(time_taken1) / len(time_taken1)
        time2 = sum(time_taken2) / len(time_taken2)

        times1.append(time1)
        times2.append(time2)

        print(i, time1, time2)

    import matplotlib.pyplot as plt

    plt.plot(times1, 'r-', label="Breitbart, on n/w with PLCs")
    plt.plot(times2, 'b-', label="Breitbart, on n/w with No PLCs")
    plt.legend(loc='upper right')
    plt.xlabel("Number of nodes/subnets")
    plt.ylabel("Time taken")

    plt.show()