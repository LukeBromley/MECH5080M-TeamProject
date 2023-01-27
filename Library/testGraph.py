import model

test_model = model
nodes = test_model.nodes
paths = test_model.paths
start_nodes = nodes
end_nodes = nodes
for path in paths:
    if path.start_node in end_nodes:
        end_nodes.remove(path.start_node)
    if path.end_node in start_nodes:
        start_nodes.remove(path.end_node)
