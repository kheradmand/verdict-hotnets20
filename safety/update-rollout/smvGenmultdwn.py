import networkx as nx
import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("--settings", type=str, default="inputs/test.json")
parser.add_argument("--template", type=str, default="mutlipledown.template")
args = parser.parse_args()

with open(args.template) as f:
    template = f.read()

with open(args.settings) as f:
    settings = json.load(f)

dir = os.path.dirname(os.path.realpath(args.settings))

with open(dir + "/" + settings["topology"]) as f:
    topology = json.load(f)

G = nx.Graph()

for l in topology["links"]:
    G.add_edge(l[0], l[1])

service_nodes = settings["service_nodes"]
front_end = settings["front_end"]
max_failure = settings["max_failure"]
min_reachable = settings["min_reachable"]
nodes_count = len(G.nodes())
service_nodes_count = len(service_nodes)

r_decs = "\n".join(["r_%s : boolean;" % n for n in G.nodes()])
r_init = "\n".join("init(r_%s) := %s;" % (n, "TRUE" if n == front_end else "FALSE") for n in G.nodes())
r_next = "\n".join("next(r_%s) := reset ? %s : r_%s | " % (n,"TRUE" if n == front_end else "FALSE",n) + " | ".join("(r_%s & link_%s_%s.status = UP)" % (m,min(n,m),max(n,m)) for m in G[n]) + ";" for n in G.nodes())
node_decs = "\n".join(["node_%s : node(n_%s, more_updates, device_to_update);" % (n,n) for n in service_nodes])
devices_to_update = "{" + " , ".join("n_%s" % n for n in service_nodes) + "}"
link_decs = "\n".join(["link_%s_%s : link(l_%s_%s, link_to_fail, failable);" % (min(l), max(l), min(l), max(l)) for l in G.edges()])
links_to_fail = "{" + " , ".join("l_%s_%s" % (min(l),max(l)) for l in G.edges)  + "}"
just_failed = " | ".join("link_%s_%s.just_failed" % (min(l), max(l)) for l in G.edges())
failure_count = " + ".join("(link_%s_%s.status = DOWN ? 0ud8_1 : 0ud8_0)" % (min(l), max(l)) for l in G.edges())
updated_count = " + ".join("(node_%s.updated ? 0ud8_1 : 0ud8_0)" % n for n in service_nodes)
down_count = " + ".join("(node_%s.status = DOWN ? 0ud8_1 : 0ud8_0)" % n for n in service_nodes)
reachable_count = " + ".join("(R_%s ? 0ud8_1 : 0ud8_0)" % n for n in service_nodes)
reachability_defs = "\n".join("R_%s := node_%s.status = UP & t.r_%s;" % (n,n,n) for n in service_nodes)
done_def = " & ".join("next(r_%s) = r_%s" % (n,n) for n in G.nodes())

template = template \
    .replace("%DONE_DEF%", done_def) \
    .replace("%R_DECS%", r_decs) \
    .replace("%R_INIT%", r_init) \
    .replace("%R_NEXT%", r_next) \
    .replace("%NODE_DECS%", node_decs) \
    .replace("%DEVICES_TO_UPDATE%", devices_to_update) \
    .replace("%LINK_DECS%", link_decs) \
    .replace("%LINKS_TO_FAIL%", links_to_fail) \
    .replace("%JUST_FAILED%", just_failed) \
    .replace("%FAILURE_COUNT%", failure_count) \
    .replace("%UPDATED_COUNT%", updated_count)\
    .replace("%DOWN_COUNT%", down_count) \
    .replace("%REACHABLE_COUNT%", reachable_count) \
    .replace("%REACHABILITY_DEFS%", reachability_defs) \
    .replace("%SERVICE_NODES_COUNT%", "0ud8_%d" % service_nodes_count)
    # .replace("%MAX_FAILURE%", "0ud8_%d" % max_failure) \
    # .replace("%MIN_REACHABLE%", "0ud8_%d" % min_reachable) \

print(template)
