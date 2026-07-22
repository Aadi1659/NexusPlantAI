import os
import networkx as nx
from pyvis.network import Network

# Define outputs
OUTPUT_DIR = "/Users/aadityadevsharma/Documents/hackathon/data/processed"
HTML_PATH = os.path.join(OUTPUT_DIR, "knowledge_graph.html")

def build_knowledge_graph(output_path=HTML_PATH):
    """
    Builds a high-impact, beautifully spaced Dark Cyber Relational Knowledge Graph topology
    with clean, sleek glowing vector edges (no overlapping Times New Roman edge text).
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    G = nx.DiGraph()
    node_types = {}
    
    # Core Topology Nodes
    nodes = [
        # Equipment (Amber Spheres)
        ("P-101", "equipment", "Centrifugal Pump P-101"),
        ("P-102", "equipment", "Boiler Feed Pump P-102"),
        ("V-105", "equipment", "Control Valve V-105"),
        ("V-203", "equipment", "High-Pressure Gate Valve V-203"),
        ("C-301", "equipment", "Reciprocating Compressor C-301"),
        
        # OEM Manuals (Violet Tech Boxes)
        ("centrifugal-pump-manual.pdf", "document", "OEM Pump Manual (PDF)"),
        ("811_iom.pdf", "document", "Compressor IOM Manual (PDF)"),
        ("factory_acta1948-63.pdf", "document", "Factories Act 1948 Safety Code"),
        ("hsg245.pdf", "document", "HSG245 Accident Guide"),
        ("riddor-report.pdf", "document", "RIDDOR Statutory Guidelines"),
        
        # Failure Modes (Rose Diamonds)
        ("Mechanical Seal Failure", "failure_mode", "Mechanical Seal Breakdown"),
        ("Bearing Vibration", "failure_mode", "High Bearing Vibration"),
        ("Thermal ISO Oil Breakdown", "failure_mode", "Thermal Degradation"),
        ("Steam Pressure Peak Leak", "failure_mode", "Packing Gland Leakage"),
        ("High Temp Valve Trip", "failure_mode", "Thermal Valve Trip"),
        
        # Remediation & Compliance (Emerald Hexagons)
        ("ISO VG 46 Oil Flush", "remediation", "Flush & Refill ISO VG 46"),
        ("Laser Shaft Realignment", "remediation", "Laser Realignment (<0.05mm)"),
        ("Form F-18 Report Filing", "remediation", "Factories Act Filing"),
        ("RIDDOR Notice Filing", "remediation", "Statutory Incident Notice")
    ]
    
    for nid, ntype, title in nodes:
        G.add_node(nid, label=nid, title=f"{ntype.upper()}: {title}")
        node_types[nid] = ntype
        
    # Relationships & Edges
    edges = [
        ("P-101", "centrifugal-pump-manual.pdf", "HAS MANUAL"),
        ("P-102", "centrifugal-pump-manual.pdf", "HAS MANUAL"),
        ("C-301", "811_iom.pdf", "HAS MANUAL"),
        ("V-105", "factory_acta1948-63.pdf", "GOVERNED BY"),
        ("V-203", "hsg245.pdf", "GOVERNED BY"),
        
        ("P-101", "Bearing Vibration", "HAS FAILURE"),
        ("P-102", "Mechanical Seal Failure", "HAS FAILURE"),
        ("C-301", "Thermal ISO Oil Breakdown", "HAS FAILURE"),
        ("C-301", "High Temp Valve Trip", "HAS FAILURE"),
        ("V-203", "Steam Pressure Peak Leak", "HAS FAILURE"),
        
        ("Bearing Vibration", "Laser Shaft Realignment", "REMEDIATED BY"),
        ("Mechanical Seal Failure", "ISO VG 46 Oil Flush", "REMEDIATED BY"),
        ("Thermal ISO Oil Breakdown", "ISO VG 46 Oil Flush", "REMEDIATED BY"),
        ("Steam Pressure Peak Leak", "Form F-18 Report Filing", "CITED IN"),
        ("High Temp Valve Trip", "RIDDOR Notice Filing", "STATUTORY NOTICE"),
        
        ("factory_acta1948-63.pdf", "Form F-18 Report Filing", "REGULATORY CODE"),
        ("riddor-report.pdf", "RIDDOR Notice Filing", "REGULATORY CODE")
    ]
    
    for u, v, lbl in edges:
        G.add_edge(u, v, label=lbl)
        
    # Export to Pyvis with Clean Vector Lines (No messy canvas font edge text)
    net = Network(height="100%", width="100%", bgcolor="#060911", font_color="#FFFFFF", directed=True)
    
    net.set_options("""
    {
      "nodes": {
        "font": {
          "color": "#F8FAFC",
          "size": 13,
          "face": "JetBrains Mono",
          "strokeWidth": 3,
          "strokeColor": "#060911"
        },
        "shadow": {
          "enabled": true,
          "color": "rgba(255, 153, 0, 0.5)",
          "size": 18
        }
      },
      "edges": {
        "font": {
          "color": "transparent",
          "size": 0
        },
        "smooth": {
          "type": "cubicBezier",
          "roundness": 0.4
        }
      },
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -130,
          "centralGravity": 0.008,
          "springLength": 190,
          "springConstant": 0.05
        },
        "maxVelocity": 45,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {"iterations": 200}
      }
    }
    """)
    
    color_map = {
        "equipment": {
            "background": "#FF9900",  # Electric Amber Gold
            "border": "#FFD000",
            "highlight": {"background": "#FFB800", "border": "#FFFFFF"}
        },
        "document": {
            "background": "#8B5CF6",  # Quantum Violet
            "border": "#C4B5FD",
            "highlight": {"background": "#A78BFA", "border": "#FFFFFF"}
        },
        "failure_mode": {
            "background": "#F43F5E",  # Cyber Rose
            "border": "#FDA4AF",
            "highlight": {"background": "#FB7185", "border": "#FFFFFF"}
        },
        "remediation": {
            "background": "#00FF9D",  # Neon Emerald
            "border": "#6EE7B7",
            "highlight": {"background": "#34D399", "border": "#FFFFFF"}
        }
    }
    
    for node in G.nodes():
        ntype = node_types.get(node, "general")
        colors = color_map.get(ntype, {"background": "#38BDF8", "border": "#7DD3FC"})
        
        shape = "dot"
        size = 32
        if ntype == "equipment":
            shape = "dot"
            size = 36
        elif ntype == "document":
            shape = "box"
            size = 22
        elif ntype == "failure_mode":
            shape = "diamond"
            size = 30
        elif ntype == "remediation":
            shape = "hexagon"
            size = 30
            
        net.add_node(
            node, 
            label=node, 
            title=f"{ntype.upper()}: {node}", 
            color=colors, 
            shape=shape,
            size=size
        )
        
    for u, v, data in G.edges(data=True):
        label = data.get("label", "")
        color = "#FF9900"
        if "FAILURE" in label:
            color = "#F43F5E"
        elif "MANUAL" in label:
            color = "#8B5CF6"
        elif "REMEDIATED" in label:
            color = "#00FF9D"
        elif "GOVERNED" in label or "REGULATORY" in label:
            color = "#38BDF8"
            
        net.add_edge(u, v, title=f"Relationship: {label}", color=color, width=2.8, arrowStrikethrough=False)
        
    net.write_html(output_path)
    
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            html = f.read()
            
        custom_head = """
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
        <style>
            html, body { background-color: #060911 !important; margin: 0; padding: 0; overflow: hidden; font-family: 'JetBrains Mono', monospace !important; }
            #mynetwork { background-color: #060911 !important; width: 100vw; height: 100vh; border: none; }
            div.vis-network { outline: none !important; }
        </style>
        """
        html = html.replace("</head>", f"{custom_head}</head>")
        with open(output_path, "w") as f:
            f.write(html)
            
    print(f"Clean Knowledge Graph generated at {output_path}")
    return True

if __name__ == "__main__":
    build_knowledge_graph()
