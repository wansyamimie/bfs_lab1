"""
Algorithm Explorer: BFS & DFS Visualizer
Run: python -m streamlit run app.py
"""
import json
from collections import deque
import streamlit as st
from graphviz import Digraph, escape

# --- Search Algorithms with Alphabetical Tie-Breaking ---

def run_bfs(graph, start):
    """Breadth-First Search with step tracking and levels."""
    visited = {start}
    queue = deque([(start, 0)])  # (node, level)
    
    order = []
    levels = {}
    steps = []
    
    step_num = 1
    
    while queue:
        curr_node, level = queue.popleft()
        order.append(curr_node)
        levels[curr_node] = level
        
        # Get neighbours sorted alphabetically
        neighbours = sorted(graph.get(curr_node, []))
        added = []
        
        for n in neighbours:
            if n not in visited:
                visited.add(n)
                queue.append((n, level + 1))
                added.append(n)
                
        q_contents = [item[0] for item in queue]
        steps.append({
            "step": step_num,
            "node": curr_node,
            "level": level,
            "added": ", ".join(added) if added else "none",
            "queue": f"[{', '.join(q_contents)}]"
        })
        step_num += 1
        
    return order, levels, steps


def run_dfs(graph, start):
    """Depth-First Search with step tracking and levels."""
    visited = set()
    stack = [(start, 0)]  # (node, level)
    
    order = []
    levels = {}
    steps = []
    
    step_num = 1
    
    while stack:
        curr_node, level = stack.pop()
        
        if curr_node not in visited:
            visited.add(curr_node)
            order.append(curr_node)
            levels[curr_node] = level
            
            # For DFS stack, reverse sorted neighbours to process alphabetically first
            neighbours = sorted(graph.get(curr_node, []), reverse=True)
            added = []
            
            for n in neighbours:
                if n not in visited:
                    stack.append((n, level + 1))
                    added.append(n)
                    
            added.reverse()  # Show in alphabetical order in the 'added' column
            s_contents = [item[0] for item in stack]
            steps.append({
                "step": step_num,
                "node": curr_node,
                "level": level,
                "added": ", ".join(added) if added else "none",
                "queue": f"[{', '.join(s_contents)}]"
            })
            step_num += 1
            
    return order, levels, steps


# --- Streamlit UI Configuration ---

st.set_page_config(page_title="Search Algorithm Explorer", page_icon="🔵", layout="wide")
st.markdown("<style>h1 {color: #0891b2;} .stButton button {border-radius: 10px;}</style>", unsafe_allow_html=True)

st.title("Search Algorithms Explorer")
st.caption("Breadth-First Search (BFS) & Depth-First Search (DFS) with Alphabetical Tie-Breaking.")

# --- Default Graph from Question 2 ---
default_graph = {
    "A": ["B", "D"],
    "B": ["C", "E", "G"],
    "C": ["A"],
    "D": ["C"],
    "E": ["H"],
    "F": [],
    "G": ["F"],
    "H": ["F", "G"]
}

# --- Sidebar Controls ---
algo_choice = st.sidebar.radio("Select Search Algorithm", ["BFS (Breadth-First Search)", "DFS (Depth-First Search)"])
text = st.sidebar.text_area("Edit graph (JSON)", json.dumps(default_graph, indent=2), height=280)

# Validate Input Graph
try:
    graph = json.loads(text)
    if not isinstance(graph, dict) or not graph:
        raise ValueError("Use a non-empty JSON object.")
    for neighbours in list(graph.values()):
        if not isinstance(neighbours, list) or not all(isinstance(n, str) and n.strip() for n in neighbours):
            raise ValueError("Each neighbour list must contain non-empty strings.")
        for node in neighbours:
            graph.setdefault(node, [])
    if len(graph) > 100 or not all(node.strip() for node in graph):
        raise ValueError("Use 1–100 nodes with non-empty names.")
except ValueError as error:
    st.error(f"Invalid graph: {error}")
    st.stop()

start_node = st.sidebar.selectbox("Start node", sorted(list(graph.keys())))
run_clicked = st.sidebar.button("Run Search", type="primary")

# Execute Algorithm
if "BFS" in algo_choice:
    order, levels, steps = run_bfs(graph, start_node)
else:
    order, levels, steps = run_dfs(graph, start_node)

# --- Visual Layout ---
canvas, result = st.columns([1.2, 1])

with canvas:
    st.subheader("Graph Visualization")
    dot = Digraph()
    dot.attr(bgcolor="transparent", rankdir="TB")
    dot.attr("node", shape="circle", style="filled", fontname="Arial", fontcolor="#111827")
    ids = {node: f"n{i}" for i, node in enumerate(graph)}
    
    for node in sorted(graph):
        color = "#fde68a" if node == start_node else "#67e8f9" if node in order else "#e2e8f0"
        label = node + (f"\n#{order.index(node) + 1}" if node in order else "")
        dot.node(ids[node], escape(label), fillcolor=color, color="#0891b2")
        
        for neighbour in sorted(graph[node]):
            dot.edge(ids[node], ids[neighbour], color="#94a3b8")
            
    st.graphviz_chart(dot, use_container_width=True)

with result:
    st.subheader("Traversal Details")
    
    if order:
        st.write("**Traversed Path:**")
        st.code(" ---> ".join(order), language="text")
        
        # Display Level Summary
        max_level = max(levels.values()) if levels else 0
        level_str_list = []
        for l in range(max_level + 1):
            nodes_at_l = [n for n in order if levels.get(n) == l]
            if nodes_at_l:
                level_str_list.append(f"Level {l}: {', '.join(nodes_at_l)}")
        st.caption(" | ".join(level_str_list))
        
        st.metric("Visited Nodes", f"{len(order)} / {len(graph)}")
        
        # Step-by-step Process Table
        st.write("**Process Step Table:**")
        queue_col_label = "Queue after" if "BFS" in algo_choice else "Stack after"
        
        table_data = []
        for row in steps:
            table_data.append({
                "Step": row["step"],
                "Node Visited": row["node"],
                "Level": row["level"],
                "Added": row["added"],
                queue_col_label: row["queue"]
            })
        st.dataframe(table_data, use_container_width=True)
    else:
        st.info("Select a start node and click Run Search.")

st.caption("Yellow: Start Node · Cyan: Visited · Grey: Unvisited")
st.caption("Dr. Ku Muhammad Naim Ku Khalif · Algorithm Explorer")