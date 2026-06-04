import networkx as nx
from pyvis.network import Network
import os

# Load the GraphML file
G = nx.read_graphml("outputs/cleaned_network.graphml")

# Create an interactive visualization
net = Network(height="750px", width="100%", directed=True)
net.from_nx(G)

# Write HTML directly to avoid template rendering issues
output_file = "network_visualization.html"
net.write_html(output_file, open_browser=False, notebook=False)
print(f"Open {output_file} in your browser")
print(f"File created at: {os.path.abspath(output_file)}")
