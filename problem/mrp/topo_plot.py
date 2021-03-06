import networkx as nx
import matplotlib.pyplot as plt
import json
import os


def topo_plot(topo):
    G = nx.Graph()
    
    LINK_PATH = os.getcwd() + '\\topo_file\\' + topo + '\\link_info.json'

    with open(LINK_PATH, 'r') as f:
        conf = json.load(f)
        for item in conf:
            G.add_edge(item['src'], item['dst'])
        f.close()

    nx.draw(G,pos=nx.spring_layout(G),node_color = 'w',edge_color = 'k',with_labels = True,font_size =10,node_size =150)
    plt.show()
    

if __name__ == '__main__':
    # topo = 'topo3'
    # topo_plot(topo)
    # G = nx.waxman_graph(10, alpha=0.8, beta=0.1)
    G = nx.random_graphs.gnm_random_graph(200, 500)
    pos1 = nx.fruchterman_reingold_layout(G)
    pos2 = nx.random_layout(G)
    pos3 = nx.spring_layout(G)
    nx.draw_networkx(G,pos=pos3)
    plt.show()
    
    # for path in nx.all_shortest_paths(G, source=5, target=33):
    #     print path
    
    # for dst in G.nodes():
    #     print nx.has_path(G,source=34,target=dst)