import networkx as nx

# fat-tree gen function taken from Plankton source code
def generate_topology(k):
    if k % 2 != 0:
        raise ValueError('"k" has to be even')

    G = nx.Graph()

    ## Nodes/Switches
    # G.add_nodes(range(0, (k / 2) ** 2 + k ** 2))
    index = 0
    core_switches = range(index, index + (k // 2) ** 2)
    index += len(core_switches)
    agg_switches = range(index, index + (k ** 2) // 2)
    index += len(agg_switches)
    edge_switches = range(index, index + (k ** 2) // 2)
    index += len(edge_switches)

    ## Core-Aggregation Links
    for i, core in enumerate(core_switches):
        for j in range(0, k):
            agg = agg_switches[j * (k // 2) + i // (k // 2)]
            G.add_edge(core, agg)
            G.add_edge(agg, core)

    ## Aggregation-Edge Links
    for i, agg in enumerate(agg_switches):
        for j in range(0, k // 2):
            edge = edge_switches[(i - i % (k // 2)) + j]
            G.add_edge(agg, edge)
            G.add_edge(edge, agg)


    return G, core_switches, edge_switches

def gen(k):
    import matplotlib.pyplot as plt
    G,_,edge_switches = generate_topology(k)
    nx.draw_networkx(G)
    plt.savefig('fattree%d.pdf' % k)
    import json
    with open('fattree%d.json' % k,'w') as f:
        json.dump({"links": [list(map(str,list(l))) for l in G.edges()]},f, indent=2)
    print("nodes ", len(G.nodes()))
    print("links ", len(G.edges()))
    print("#edges", len(edge_switches))
    print("edges", list(map(str, edge_switches)))


#gen(2)
#gen(4)
#gen(6)
#gen(8)
gen(10)
gen(12)
gen(14)