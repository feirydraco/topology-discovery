import matplotlib.pyplot as plt
import networkx as nx
import enum

class DevType(enum.Enum):
    ROUTER = 1
    SWITCH = 2
    APPLIANCE = 3

class Device:
    def __init__(self, ip, mac, did, label, dtype="Undefined"):
        self.ip = ip
        self.mac = mac
        self.did = did
        self.label = label
        self.dtype = dtype

    def getName(self):
            return self.did

class NetDevice:
    def __init__(self, ip, pm, did, label, dtype="Undefined"):
        self.ip = ip
        self.pm = pm
        self.did = did
        self.dtype = dtype
        self.label = label
        self.AFT = dict()

    def getAFT(self):
        pass
    
    def getName(self):
        return self.dtype

    def dispAFT(self):
        print(self.AFT)

def find_node_from_ip(G, ip):
    for node in G.nodes():
        if node.ip == ip:
            return node

def find_node_from_mac(G, mac):
    for node in G.nodes():
        if(hasattr(node, 'pm')):
            for port in node.pm.keys():
                if(node.pm[port] == mac):
                    return node

def find_next_hop_ips(G, ip):
    node = find_node_from_ip(G, ip)
    
    next_hop_ips = []
    for neighbor in G[node]:
        if(neighbor.dtype == DevType.ROUTER):
            next_hop_ips.append(neighbor.ip)
    
    return next_hop_ips

def find_router(G, router_ip):
    router_set = [router_ip]
    visited = []

    while not len(router_set) == 0:
        for ip in router_set:
            router_set.remove(ip)
            if ip in visited:
                continue
            visited.append(ip)
            next_hop = find_next_hop_ips(G, ip)
            router_set = router_set + next_hop
    return visited

def find_connections(G):
    # Init variables
    all_nodes = []   # set of all routers and switches in the subnet
    matched = dict()
    edges = []  
    # Find set of switches
    switches = []
    for node in G.nodes():
        if(node.dtype == DevType.SWITCH):
            switches.append(node)
    # Find the set of routers
    routers = []
    for node in G.nodes():
        if(node.dtype == DevType.ROUTER):
            routers.append(node)

    # Set matched to false for all switches
    for node in (switches + routers):
        matched[node] = dict()
        for port in node.pm.keys():
            matched[node][port] = False

    all_nodes = routers + switches

    # Begin algorithm
    for switch1 in switches:
        for port1 in switch1.pm.keys():
            if matched[switch1][port1]:
                continue
            else:
                for switch2 in switches:
                    if(not switch2 == switch1):
                        for port2 in switch2.pm.keys():
                            mac1 = set([find_node_from_mac(G, mac) for mac in switch1.AFT[port1]])     # nodes with MACs visible from port1 of switch1
                            mac2 = set([find_node_from_mac(G, mac) for mac in switch2.AFT[port2]])  # nodes with MACs visible from port2 of switch2
                            
                            if((mac1 | mac2) == set(all_nodes) and (mac1 - mac2) == mac1):
                                matched[switch1][port1] = True
                                matched[switch2][port2] = True
                                edges.append((switch1.label, switch2.label))#{switch1: port1, switch2: port2}))

    for router in routers:
        for switch in switches:
            for port in switch.pm.keys():
                if(matched[switch][port] == False):
                    mac = [find_node_from_mac(G, mac) for mac in switch.AFT[port]]
                    if(router in mac):
                        matched[switch][port] = True
                        edges.append((switch.label, router.label))

    return edges
                            

def find_MAC(node, port, mac, visited):
    for edge in G.edges():
        if (node in edge) and (G.edges[edge[0], edge[1]][node] == port) and (
                edge not in visited):
            if (edge[0] == node):
                next_node = edge[1]
            else:
                next_node = edge[0]
        
            visited.append(edge)
            if (not hasattr(next_node, 'pm')):
                #mac.append(next_node.mac)
                return
            mac.append(next_node.pm[G.edges[edge[0], edge[1]][next_node]])
            for p in next_node.pm.keys():
                find_MAC(next_node, p, mac, visited)

def populate_AFT(G):
    for node in G.nodes:
        if (hasattr(node, 'pm')):
            for p in node.pm.keys():
                mac = list()
                visited = list()
                find_MAC(node, p, mac, visited)
                node.AFT[p] = mac


def Skeleton(G, ML):
    unmarked = [node for node in G.nodes() if not node.dtype == DevType.APPLIANCE]
    internal_nodes = [node for node in G.nodes() if not node.dtype == DevType.APPLIANCE]
    edges = []
    router = set([find_node_from_mac(G, mac) for mac in ML])
    for node in internal_nodes:       
        for port in node.pm.keys():
            visible_nodes = set([find_node_from_mac(G, mac) for mac in node.AFT[port]])
            if(not len(visible_nodes & router) == 0):
                node.AFT[port] = []
    
    # for node in G.nodes():
    #     marked[node] = dict()
    #     for port in node.pm.keys():
    #         marked[node][port] = False

    while(not ((len(unmarked) == 0) or (len(unmarked) == 1 and unmarked[0].dtype == DevType.ROUTER))):
        L = []
        for node in unmarked:
            flag = 0
            for port in node.pm.keys():
                if(not len(node.AFT[port]) == 0):
                    flag = 1
                    break
            if(flag == 0):
                L.append(node)
                
        for node in unmarked:
            for port in node.pm.keys():
                #print(node.label, port)
                visible_nodes = set([find_node_from_mac(G, mac) for mac in node.AFT[port]])
                visible_nodes = set([node for node in visible_nodes if not node.dtype == DevType.APPLIANCE]) 
                flag = 0
                for node1 in visible_nodes:
                    if node1 not in L:
                        flag = 1
                        break
                if(flag == 1):
                    continue
                for next_node in visible_nodes:
                    edges.append((node, next_node))
                    print(edges)
                    unmarked.remove(next_node)
                    macs = set(next_node.pm.values())


                    for mac in macs:
                        G = remove_mac(G, mac)

                    #print([node.label for node in unmarked])
                        
    return edges

def remove_mac(G, mac):
    nodelist=[]
    new_G = []
    if(isinstance(G, list)):
        nodelist = G
    else:
        nodelist = G.nodes()

    for node in nodelist:
        if(not hasattr(node, 'pm')):
            continue
        for port in node.pm.keys():
            if(mac in node.AFT[port]):
                node.AFT[port].remove(mac)
        new_G.append(node)

    # for node in G.nodes():
    #     print(node.label)
    #     if(hasattr(node, 'AFT')):
    #         print(node.AFT)
    return G




if __name__ == '__main__':
    # Edge devices
    Laptop = Device("10.0.0.1", "009", 1, "Laptop", DevType.APPLIANCE)
    HDD_Recorder = Device("10.0.0.2", "090", 2, "HDD_Recorder", DevType.APPLIANCE)
    Portable_GD = Device("10.0.0.3", "900", 3, "Portable_GD", DevType.APPLIANCE)
    Audio_device = Device("10.0.0.4", "008", 4, "Audio_device", DevType.APPLIANCE)
    Air_condition = Device("10.0.0.5", "080", 5, "Air_condition", DevType.APPLIANCE)
    TV = Device("10.0.0.6", "800", 6, "TV", DevType.APPLIANCE)
    Gaming_device = Device("10.0.0.7", "006", 7, "Gaming_device", DevType.APPLIANCE)
    Desktop_PC = Device("10.0.0.8", "060", 8, "Desktop_PC", DevType.APPLIANCE)
    Security_Cam = Device("10.0.0.9", "600", 9, "Security_Cam", DevType.APPLIANCE)

    # Switches
    SW1 = NetDevice("10.0.1.1", {1: "010", 2: "010", 3: "010", 4 : "010"}, 10, "Switch1", DevType.SWITCH)
    SW2 = NetDevice("10.0.1.2", {1: "002", 2: "002", 3: "002"}, 11, "Switch2", DevType.SWITCH)
    SW3 = NetDevice("10.0.1.3", {1: "003", 2: "003", 3: "003"}, 12, "Switch3", DevType.SWITCH)
    SW4 = NetDevice("10.0.1.4", {1: "004", 2: "004"}, 13, "Switch4", DevType.SWITCH)
    PLC1 = NetDevice("10.0.1.5", {1: "005", 2 : "105"}, 14, "PLC1", DevType.SWITCH)
    PLC2 = NetDevice("10.0.1.6", {1: "006", 2 : "006"}, 15, "PLC2", DevType.SWITCH)
    PLC3 = NetDevice("10.0.1.7", {1: "007", 2 : "007", 3 : "007"}, 16, "PLC3", DevType.SWITCH)
    PLC4 = NetDevice("10.0.1.8", {1: "020", 2 : "020", 3: "020"}, 17, "PLC4", DevType.SWITCH)
    WL1 = NetDevice("10.0.1.9", {1: "200", 2 : "200", 3 : "200"}, 20, "WL1", DevType.SWITCH)
    WR = NetDevice("10.0.1.10", {1: "001", 2 : "001"}, 21, "WR", DevType.SWITCH)

    # Access gateway
    AGW = NetDevice("10.1.0.1", {1: "000", 2 : "100"}, 22, "Gateway", DevType.ROUTER)

    node_list = [Laptop, HDD_Recorder, Portable_GD, Audio_device, Air_condition, TV, Gaming_device, Desktop_PC, Security_Cam, AGW, SW1, SW2, SW3, SW4, WL1, WR, PLC1, PLC2, PLC3, PLC4]
    
    G = nx.Graph()

    # Add nodes
    G.add_nodes_from(node_list)

    # Add edges
    edge_list = [(AGW, WR), (AGW, SW1), 
                 (WR, Laptop), 
                 (SW1, Security_Cam), (SW1, SW2), (SW1, SW3),
                 (SW2, HDD_Recorder), (SW2, WL1),
                 (WL1, Audio_device), (WL1, Portable_GD),
                 (SW3, PLC1), (SW3, SW4), 
                 (SW4, Desktop_PC),
                 (PLC1, PLC4),
                 (PLC4, PLC2), (PLC4, PLC3),
                 (PLC2, Air_condition),
                 (PLC3, TV), (PLC3, Gaming_device)]

    G.add_edges_from(edge_list)

    # Add edge attributes
    G.edges[AGW, WR][AGW] = 1
    G.edges[AGW, WR][WR] = 2

    G.edges[WR, Laptop][WR] = 1
    G.edges[WR, Laptop][Laptop] = -1

    G.edges[AGW, SW1][AGW] = 2
    G.edges[AGW, SW1][SW1] = 1

    G.edges[SW1, Security_Cam][SW1] = 2
    G.edges[AGW, SW1][Security_Cam] = -1

    G.edges[SW1, SW2][SW1] = 4
    G.edges[SW2, SW1][SW2] = 3

    G.edges[SW2, HDD_Recorder][SW2] = 1
    G.edges[SW2, HDD_Recorder][HDD_Recorder] = -1

    G.edges[SW2, WL1][SW2] = 2
    G.edges[SW2, WL1][WL1] = 1

    G.edges[WL1, Portable_GD][WL1] = 2
    G.edges[WL1, Portable_GD][Portable_GD] = -1

    G.edges[WL1, Audio_device][WL1] = 3
    G.edges[WL1, Audio_device][Audio_device] = -1

    G.edges[SW1, SW3][SW1] = 3
    G.edges[SW1, SW3][SW3] = 1

    G.edges[SW4, SW3][SW3] = 3
    G.edges[SW4, SW3][SW4] = 1

    G.edges[SW4, Desktop_PC][SW4] = 2
    G.edges[SW4, Desktop_PC][Desktop_PC] = -1

    G.edges[SW3, PLC1][SW3] = 2
    G.edges[SW3, PLC1][PLC1] = 2

    G.edges[PLC4, PLC1][PLC1] = 1
    G.edges[PLC4, PLC1][PLC4] = 1

    G.edges[PLC4, PLC2][PLC4] = 2
    G.edges[PLC4, PLC2][PLC2] = 2

    G.edges[Air_condition, PLC2][PLC2] = 1
    G.edges[Air_condition, PLC2][Air_condition] = -1

    G.edges[PLC3, PLC4][PLC3] = 1
    G.edges[PLC3, PLC4][PLC4] = 3

    G.edges[PLC3, TV][PLC3] = 2
    G.edges[PLC3, TV][TV] = -1

    G.edges[PLC3, Gaming_device][PLC3] = 3
    G.edges[PLC3, Gaming_device][Gaming_device] = -1

    pos = nx.spring_layout(G)
    
    ax = plt.subplot(221)
    ax.set_xlabel('Original network')

    nx.draw_networkx_nodes(G,
                           pos,
                           nodelist=node_list,
                           node_color='pink',
                           node_size=750,
                           alpha=0.8)

    nx.draw_networkx_edges(G,
                           pos,
                           edgelist=edge_list,
                           width=2,
                           alpha=0.8,
                           edge_color='black')    

    mapping = dict()
    for elem in node_list:
        mapping[elem] = elem.label              

    nx.draw_networkx_labels(G, pos, mapping, font_size=9, font_color=(0, 0, 0))

    populate_AFT(G)

    discovered_edges = find_connections(G)
    discovered_nodes = [node.label for node in G.nodes() if not node.dtype == DevType.APPLIANCE]

    H = nx.Graph()
    H.add_nodes_from(discovered_nodes)
    H.add_edges_from(discovered_edges)

    pos = nx.spring_layout(H)

    ax = plt.subplot(222)
    ax.set_xlabel('Discovered network')

    nx.draw_networkx_nodes(H,
                           pos,
                           nodelist=discovered_nodes,
                           node_color='pink',
                           node_size=700,
                           alpha=0.8)

    nx.draw_networkx_edges(G,
                           pos,
                           edgelist=discovered_edges,
                           width=1,
                           alpha=0.9,
                           edge_color='black')    

    mapping = dict()
    for elem in discovered_nodes:
        mapping[elem] = elem              

    nx.draw_networkx_labels(H, pos, mapping, font_size=8, font_color=(0, 0, 0))





    internal_edges = [edge for edge in G.edges if (not edge[0].dtype == DevType.APPLIANCE) and (not edge[1].dtype == DevType.APPLIANCE)]
    internal_nodes = [node for node in G.nodes if not node.dtype == DevType.APPLIANCE]

    H = nx.Graph()
    H.add_nodes_from(internal_nodes)
    H.add_edges_from(internal_edges)

    pos = nx.spring_layout(H)

    ax = plt.subplot(223)
    ax.set_xlabel('Original network without the leaf devices')

    nx.draw_networkx_nodes(H,
                           pos,
                           nodelist=internal_nodes,
                           node_color='pink',
                           node_size=700,
                           alpha=0.8)

    nx.draw_networkx_edges(G,
                           pos,
                           edgelist=internal_edges,
                           width=1,
                           alpha=0.9,
                           edge_color='black')    

    mapping = dict()
    for elem in internal_nodes:
        mapping[elem] = elem.label              

    nx.draw_networkx_labels(H, pos, mapping, font_size=8, font_color=(0, 0, 0))

    internal_edges = Skeleton(G, ['000', '100'])
    internal_nodes = [node for node in G.nodes if not node.dtype == DevType.APPLIANCE]


    H = nx.Graph()
    H.add_nodes_from(internal_nodes)
    H.add_edges_from(internal_edges)

    pos = nx.spring_layout(H)

    ax = plt.subplot(224)
    ax.set_xlabel('Network discovered from algorithm 2')

    nx.draw_networkx_nodes(H,
                           pos,
                           nodelist=internal_nodes,
                           node_color='pink',
                           node_size=700,
                           alpha=0.8)

    nx.draw_networkx_edges(G,
                           pos,
                           edgelist=internal_edges,
                           width=1,
                           alpha=0.9,
                           edge_color='black')    

    mapping = dict()
    for elem in internal_nodes:
        mapping[elem] = elem.label              

    nx.draw_networkx_labels(H, pos, mapping, font_size=8, font_color=(0, 0, 0))

    #print(Skeleton(G, ['000', '100']))
    # print(remove_mac(G, '007'))

    plt.show()




