import networkx as nx
import matplotlib.pyplot as plt

def draw_pfa_diagram(pfa):
    """_summary_

    Args:
        pfa (_type_): _description_
    """
    G = nx.MultiDiGraph()
    pos = {}
    
    for i, state in enumerate(pfa.states):
        G.add_node(state)
        pos[state] = (i, 0) #This way nodes are horizontally.
        
    for (src, symbol), transitions in pfa.transitions.items():
        for dst, prob in transitions.items():
            if prob == 0:
                continue
            if prob == 1:
                label = symbol
            else:
                label = f"{symbol}|{prob:.2f}"
            G.add_edge(src, dst, label=label)
        
    fig, ax = plt.subplots(figsize=(10, 3))
    nx.draw_networkx_nodes(G, pos, ax = ax, node_color='lightblue', node_size=1500)
    nx.draw_networkx_labels(G, pos, ax = ax, font_size=12)
    nx.draw_networkx_edges(G, pos, ax = ax, connectionstyle='arc3,rad=0.2', arrowsize=30, width=2, edge_color='gray', arrowstyle='-|>',style='solid')
    
    
    edge_labels = {
        (u, v, k): d['label'] 
        for u, v, k, d in G.edges(keys=True, data=True)
    }
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax = ax, font_color='red', font_size=10)
    
    
    ax.set_title("PFA State Diagram")
    ax.axis('off')
    return fig        