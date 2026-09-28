import ast
import itertools
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import plotly.graph_objects as go

DATA_DIR = Path("data")
DELIVERY_FILE = DATA_DIR / "delivery records.xlsx"
PROVINCE_FILE = DATA_DIR / "store province.xlsx"

IMAGE_DIR = Path("images")
INTERACTIVE_DIR = Path("interactive")
IMAGE_DIR.mkdir(exist_ok=True)
INTERACTIVE_DIR.mkdir(exist_ok=True)

CAPACITIES = [3.5, 5.0, 8.0]
CAPACITY_LABELS = {3.5: "3.5T", 5.0: "5T", 8.0: "8T"}

CAPACITY_COLORS = {
    3.5: "#d62728",
    5.0: "#ffd700",
    8.0: "#1f77b4",
}

PROVINCE_COLORS = {
    "ANHUI": "#e74c3c",
    "JIANGSU": "#f39c12",
    "SHANGHAI": "#3498db",
    "ZHEJIANG": "#2ecc71",
    "Unknown": "#7f8c8d",
}

if not DELIVERY_FILE.exists():
    raise FileNotFoundError(f"Delivery file not found: {DELIVERY_FILE}")

if not PROVINCE_FILE.exists():
    raise FileNotFoundError(f"Store province file not found: {PROVINCE_FILE}")

df = pd.read_excel(DELIVERY_FILE)
store_province = pd.read_excel(PROVINCE_FILE)

print(f"Delivery records: {len(df)}")
print(f"Store reference records: {len(store_province)}")
print(f"Delivery columns: {df.columns.tolist()}")
print(f"Store reference columns: {store_province.columns.tolist()}")

def parse_store_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            return parsed if isinstance(parsed, list) else []
        except (ValueError, SyntaxError):
            return []
    return []

df["Stores"] = df["List_Code"].apply(parse_store_list)
df["Number_of_stores"] = df["Stores"].apply(len)
df["Capacity(T)"] = pd.to_numeric(df["Capacity(T)"], errors="coerce")

province_lookup = dict(
    zip(store_province["Code"], store_province["Province"])
)

all_stores = sorted(
    set(itertools.chain.from_iterable(df["Stores"]))
)

store_provinces = {
    store: province_lookup.get(store, "Unknown")
    for store in all_stores
}

network_comb = []

for stores in df["Stores"]:
    for source, target in itertools.combinations(sorted(set(stores)), 2):
        network_comb.append((source, target))

edge_frequency = {}

for source, target in network_comb:
    edge = tuple(sorted((source, target)))
    edge_frequency[edge] = edge_frequency.get(edge, 0) + 1

G = nx.Graph()
G.add_nodes_from(all_stores)

for (source, target), weight in edge_frequency.items():
    G.add_edge(source, target, weight=weight)

nx.set_node_attributes(G, store_provinces, "province")

for source, target, data in G.edges(data=True):
    data["same_province"] = (
        G.nodes[source]["province"] == G.nodes[target]["province"]
    )

degree_dict = dict(G.degree())
weighted_degree_dict = dict(G.degree(weight="weight"))

most_connected_store = (
    max(degree_dict.items(), key=lambda x: x[1])
    if degree_dict
    else None
)

isolated_stores = list(nx.isolates(G))

network_density = nx.density(G)

strongest_pairs = sorted(
    edge_frequency.items(),
    key=lambda x: x[1],
    reverse=True,
)

same_province_edges = [
    (u, v)
    for u, v, data in G.edges(data=True)
    if data["same_province"]
]

different_province_edges = [
    (u, v)
    for u, v, data in G.edges(data=True)
    if not data["same_province"]
]

same_province_weight = sum(
    data["weight"]
    for _, _, data in G.edges(data=True)
    if data["same_province"]
)

different_province_weight = sum(
    data["weight"]
    for _, _, data in G.edges(data=True)
    if not data["same_province"]
)

print(f"Number of stores: {G.number_of_nodes()}")
print(f"Number of store relationships: {G.number_of_edges()}")
print(f"Network density: {network_density:.4f}")
print(f"Most connected store: {most_connected_store}")
print(f"Isolated stores: {isolated_stores}")
print(f"Same-province relationships: {len(same_province_edges)}")
print(f"Cross-province relationships: {len(different_province_edges)}")
print(f"Same-province co-delivery frequency: {same_province_weight}")
print(f"Cross-province co-delivery frequency: {different_province_weight}")

print("\nTop 10 co-delivered store pairs:")
for pair, frequency in strongest_pairs[:10]:
    print(f"{pair}: {frequency}")

province_pair_frequency = {}

for source, target, data in G.edges(data=True):
    province_pair = tuple(
        sorted(
            [
                G.nodes[source]["province"],
                G.nodes[target]["province"],
            ]
        )
    )
    province_pair_frequency[province_pair] = (
        province_pair_frequency.get(province_pair, 0)
        + data["weight"]
    )

province_pair_frequency = sorted(
    province_pair_frequency.items(),
    key=lambda x: x[1],
    reverse=True,
)

for province_pair, frequency in province_pair_frequency:
    print(f"{province_pair}: {frequency}")

if province_pair_frequency:
    total_frequency = sum(
        frequency for _, frequency in province_pair_frequency
    )

    print("\nProvince-pair percentages:")
    for province_pair, frequency in province_pair_frequency:
        percentage = frequency / total_frequency * 100
        print(
            f"{province_pair}: "
            f"{frequency} ({percentage:.2f}%)"
        )

communities = list(
    nx.community.greedy_modularity_communities(
        G,
        weight="weight",
    )
)

store_community = {}

for community_id, community in enumerate(communities, start=1):
    for store in community:
        store_community[store] = community_id

community_analysis = {}

for community_id, community in enumerate(communities, start=1):
    community_graph = G.subgraph(community)

    internal_weight = sum(
        data.get("weight", 1)
        for _, _, data in community_graph.edges(data=True)
    )

    community_analysis[community_id] = {
        "stores": len(community),
        "provinces": sorted(
            {
                G.nodes[store]["province"]
                for store in community
            }
        ),
        "internal_edges": community_graph.number_of_edges(),
        "internal_weight": internal_weight,
        "density": nx.density(community_graph),
    }

print(f"Number of communities: {len(communities)}")

for community_id, data in community_analysis.items():
    print(
        f"Community {community_id}: "
        f"{data['stores']} stores | "
        f"{data['internal_edges']} internal edges | "
        f"frequency {data['internal_weight']} | "
        f"density {data['density']:.4f} | "
        f"provinces: {', '.join(data['provinces'])}"
    )

delivery_df = df[
    [
        "Month",
        "Date",
        "Year-Week",
        "Capacity(T)",
        "Total_tons(T)",
        "Stores",
        "Number_of_stores",
    ]
].copy()

delivery_df["Utilization"] = (
    delivery_df["Total_tons(T)"]
    / delivery_df["Capacity(T)"].replace(0, pd.NA)
) * 100

print(f"Total delivery records: {len(delivery_df)}")
print(
    f"Average stores per delivery: "
    f"{delivery_df['Number_of_stores'].mean():.2f}"
)
print(
    f"Maximum stores in one delivery: "
    f"{delivery_df['Number_of_stores'].max()}"
)
print(
    f"Minimum stores in one delivery: "
    f"{delivery_df['Number_of_stores'].min()}"
)

multi_store_deliveries = delivery_df[
    delivery_df["Number_of_stores"] >= 2
]

single_store_deliveries = delivery_df[
    delivery_df["Number_of_stores"] == 1
]

print(
    f"Single-store deliveries: "
    f"{len(single_store_deliveries)}"
)
print(
    f"Multi-store deliveries: "
    f"{len(multi_store_deliveries)}"
)
print(
    f"Multi-store delivery percentage: "
    f"{len(multi_store_deliveries) / len(delivery_df) * 100:.2f}%"
)

valid_utilization = delivery_df["Utilization"].dropna()

if not valid_utilization.empty:
    print(
        f"Average truck utilization: "
        f"{valid_utilization.mean():.2f}%"
    )

samir_an = delivery_df[
    delivery_df["Capacity(T)"].isin(CAPACITIES)
].copy()

samir_route_count = (
    samir_an
    .groupby(["Month", "Capacity(T)"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=CAPACITIES, fill_value=0)
)

samir_route_count = samir_route_count[
    samir_route_count.sum(axis=1) > 0
]

fig, ax = plt.subplots(figsize=(11, 7))

samir_route_count.plot(
    kind="bar",
    stacked=True,
    ax=ax,
    color=[CAPACITY_COLORS[c] for c in CAPACITIES],
    edgecolor="black",
    width=0.75,
)

ax.set_xlabel("Month")
ax.set_ylabel("Number of Routes")
ax.set_title("Number of Routes per Truck Size")
ax.legend(
    title="Truck Capacity",
    labels=[CAPACITY_LABELS[c] for c in CAPACITIES],
)

plt.xticks(rotation=90)
plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "number_of_routes_per_truck_size.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

delivery_share = (
    samir_an
    .groupby("Capacity(T)")["Number_of_stores"]
    .sum()
    .reindex(CAPACITIES, fill_value=0)
)

fig, ax = plt.subplots(figsize=(8, 8))

ax.pie(
    delivery_share.values,
    labels=[CAPACITY_LABELS[c] for c in CAPACITIES],
    autopct="%1.1f%%",
    startangle=90,
    colors=[CAPACITY_COLORS[c] for c in CAPACITIES],
    wedgeprops={
        "linewidth": 5,
        "edgecolor": "white",
    },
)

centre = plt.Circle((0, 0), 0.70, fc="white")
ax.add_artist(centre)

ax.set_title("Distribution of Store Deliveries by Truck Size")
ax.axis("equal")

plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "delivery_distribution_by_truck_size.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

store_route = (
    samir_an
    .groupby(["Month", "Capacity(T)"])["Number_of_stores"]
    .mean()
    .unstack(fill_value=0)
    .reindex(columns=CAPACITIES, fill_value=0)
)

store_route = store_route[
    store_route.sum(axis=1) > 0
]

fig, ax = plt.subplots(figsize=(12, 7))

store_route.plot(
    kind="bar",
    ax=ax,
    color=[CAPACITY_COLORS[c] for c in CAPACITIES],
    edgecolor="black",
    width=0.75,
)

ax.set_xlabel("Month")
ax.set_ylabel("Average Stores per Route")
ax.set_title(
    "Number of Store Deliveries per Route for Each Truck Type"
)
ax.legend(
    title="Truck Capacity",
    labels=[CAPACITY_LABELS[c] for c in CAPACITIES],
)

plt.xticks(rotation=90)
plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "store_deliveries_per_route.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 7))

ax.pie(
    [
        len(single_store_deliveries),
        len(multi_store_deliveries),
    ],
    labels=["Single-store", "Multi-store"],
    autopct="%1.1f%%",
    startangle=90,
    wedgeprops={
        "linewidth": 4,
        "edgecolor": "white",
    },
)

centre = plt.Circle((0, 0), 0.70, fc="white")
ax.add_artist(centre)

ax.set_title("Single-Store vs Multi-Store Deliveries")
ax.axis("equal")

plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "single_vs_multi_store_deliveries.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

stores_per_delivery = (
    delivery_df["Number_of_stores"]
    .value_counts()
    .sort_index()
)

fig, ax = plt.subplots(figsize=(9, 6))

ax.bar(
    stores_per_delivery.index.astype(str),
    stores_per_delivery.values,
    edgecolor="black",
)

ax.set_xlabel("Number of Stores in Delivery")
ax.set_ylabel("Number of Deliveries")
ax.set_title("Distribution of Stores per Delivery")

plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "stores_per_delivery_distribution.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

province_counts = pd.Series(store_provinces).value_counts()

fig, ax = plt.subplots(figsize=(8, 8))

province_labels = province_counts.index.tolist()
province_colors = [
    PROVINCE_COLORS.get(p, PROVINCE_COLORS["Unknown"])
    for p in province_labels
]

ax.pie(
    province_counts.values,
    labels=province_labels,
    autopct="%1.1f%%",
    startangle=90,
    colors=province_colors,
    wedgeprops={
        "linewidth": 4,
        "edgecolor": "white",
    },
)

ax.set_title("Store Distribution by Province")
ax.axis("equal")

plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "province_distribution.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

top_degree = sorted(
    degree_dict.items(),
    key=lambda x: x[1],
    reverse=True,
)[:15]

top_degree_df = pd.DataFrame(
    top_degree,
    columns=["Store", "Connections"],
).sort_values("Connections")

fig, ax = plt.subplots(figsize=(9, 7))

ax.barh(
    top_degree_df["Store"],
    top_degree_df["Connections"],
    edgecolor="black",
)

ax.set_xlabel("Number of Connections")
ax.set_ylabel("Store")
ax.set_title("Top 15 Most Connected Stores")

plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "most_connected_stores.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

top_weighted = sorted(
    weighted_degree_dict.items(),
    key=lambda x: x[1],
    reverse=True,
)[:15]

top_weighted_df = pd.DataFrame(
    top_weighted,
    columns=["Store", "Weighted_Connectivity"],
).sort_values("Weighted_Connectivity")

fig, ax = plt.subplots(figsize=(9, 7))

ax.barh(
    top_weighted_df["Store"],
    top_weighted_df["Weighted_Connectivity"],
    edgecolor="black",
)

ax.set_xlabel("Weighted Connectivity")
ax.set_ylabel("Store")
ax.set_title("Top 15 Stores by Weighted Connectivity")

plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "weighted_store_connectivity.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

top_pairs = strongest_pairs[:15]

pair_labels = [
    f"{source} — {target}"
    for (source, target), _ in top_pairs
]

pair_values = [
    frequency
    for _, frequency in top_pairs
]

pair_df = pd.DataFrame(
    {
        "Pair": pair_labels,
        "Frequency": pair_values,
    }
).sort_values("Frequency")

fig, ax = plt.subplots(figsize=(10, 7))

ax.barh(
    pair_df["Pair"],
    pair_df["Frequency"],
    edgecolor="black",
)

ax.set_xlabel("Co-delivery Frequency")
ax.set_ylabel("Store Pair")
ax.set_title("Top 15 Most Frequently Co-Delivered Store Pairs")

plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "strongest_store_pairs.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

province_list = sorted(
    set(store_provinces.values())
)

province_matrix = pd.DataFrame(
    0,
    index=province_list,
    columns=province_list,
)

for (province_a, province_b), frequency in province_pair_frequency:
    province_matrix.loc[province_a, province_b] += frequency
    province_matrix.loc[province_b, province_a] += frequency

np_matrix = province_matrix.values

fig, ax = plt.subplots(figsize=(8, 7))

image = ax.imshow(np_matrix, aspect="auto")

ax.set_xticks(range(len(province_list)))
ax.set_yticks(range(len(province_list)))
ax.set_xticklabels(province_list, rotation=45, ha="right")
ax.set_yticklabels(province_list)

for i in range(len(province_list)):
    for j in range(len(province_list)):
        ax.text(
            j,
            i,
            int(np_matrix[i, j]),
            ha="center",
            va="center",
        )

ax.set_title("Province-to-Province Co-Delivery Connectivity")
fig.colorbar(image, ax=ax, label="Co-delivery Frequency")

plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "province_connectivity_heatmap.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

def draw_network(
    graph,
    title,
    output_file,
    edge_color=None,
    capacity_edges=None,
):
    if graph.number_of_nodes() == 0:
        return

    position = nx.spring_layout(
        graph,
        seed=42,
        weight="weight",
    )

    fig, ax = plt.subplots(figsize=(12, 9))

    if capacity_edges is None:
        nx.draw_networkx_edges(
            graph,
            position,
            width=[
                1 + data.get("weight", 1) * 0.15
                for _, _, data in graph.edges(data=True)
            ],
            alpha=0.65,
            edge_color=edge_color or "#555555",
            ax=ax,
        )
    else:
        for capacity in CAPACITIES:
            edges = capacity_edges.get(capacity, [])

            if edges:
                nx.draw_networkx_edges(
                    graph,
                    position,
                    edgelist=list(edges),
                    edge_color=CAPACITY_COLORS[capacity],
                    width=2,
                    alpha=0.70,
                    label=CAPACITY_LABELS[capacity],
                    ax=ax,
                )

    node_colors = [
        PROVINCE_COLORS.get(
            graph.nodes[node].get("province", "Unknown"),
            PROVINCE_COLORS["Unknown"],
        )
        for node in graph.nodes()
    ]

    nx.draw_networkx_nodes(
        graph,
        position,
        node_color=node_colors,
        node_size=220,
        edgecolors="black",
        ax=ax,
    )

    nx.draw_networkx_labels(
        graph,
        position,
        font_size=7,
        ax=ax,
    )

    ax.set_title(title, fontsize=15)
    ax.axis("off")

    if capacity_edges is not None:
        ax.legend(title="Truck Capacity")

    plt.tight_layout()

    fig.savefig(
        IMAGE_DIR / output_file,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

draw_network(
    G,
    "Full Transportation Network",
    "full_transportation_network.png",
)

def build_capacity_graph(capacity):
    capacity_df = df[
        df["Capacity(T)"] == capacity
    ]

    graph = nx.Graph()

    for stores in capacity_df["Stores"]:
        unique_stores = sorted(set(stores))

        for source, target in itertools.combinations(
            unique_stores,
            2,
        ):
            if graph.has_edge(source, target):
                graph[source][target]["weight"] += 1
            else:
                graph.add_edge(
                    source,
                    target,
                    weight=1,
                )

    for node in graph.nodes():
        graph.nodes[node]["province"] = store_provinces.get(
            node,
            "Unknown",
        )

    return graph

capacity_graphs = {
    capacity: build_capacity_graph(capacity)
    for capacity in CAPACITIES
}

for capacity, graph in capacity_graphs.items():
    safe_name = str(capacity).replace(".", "_")

    draw_network(
        graph,
        f"{CAPACITY_LABELS[capacity]} Transportation Network",
        f"network_{safe_name}T.png",
        edge_color=CAPACITY_COLORS[capacity],
    )

capacity_edges = {}

for capacity in CAPACITIES:
    edges = set()

    for stores in df.loc[
        df["Capacity(T)"] == capacity,
        "Stores",
    ]:
        for source, target in itertools.combinations(
            sorted(set(stores)),
            2,
        ):
            edges.add(tuple(sorted((source, target))))

    capacity_edges[capacity] = edges

draw_network(
    G,
    "Transportation Network by Truck Capacity",
    "truck_capacity_network_comparison.png",
    capacity_edges=capacity_edges,
)

community_colors = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#17becf",
    "#bcbd22",
    "#7f7f7f",
]

community_position = nx.spring_layout(
    G,
    seed=42,
    weight="weight",
)

fig, ax = plt.subplots(figsize=(12, 9))

nx.draw_networkx_edges(
    G,
    community_position,
    width=1.2,
    alpha=0.45,
    ax=ax,
)

for community_id, community in enumerate(
    communities,
    start=1,
):
    nx.draw_networkx_nodes(
        G,
        community_position,
        nodelist=list(community),
        node_color=community_colors[
            (community_id - 1) % len(community_colors)
        ],
        node_size=230,
        edgecolors="black",
        label=f"Community {community_id}",
        ax=ax,
    )

nx.draw_networkx_labels(
    G,
    community_position,
    font_size=7,
    ax=ax,
)

ax.set_title("Transportation Network — Community Detection")
ax.axis("off")
ax.legend(
    title="Community",
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
)

plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "community_network.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

community_sizes = {
    f"Community {community_id}": data["stores"]
    for community_id, data in community_analysis.items()
}

fig, ax = plt.subplots(figsize=(9, 6))

ax.bar(
    community_sizes.keys(),
    community_sizes.values(),
    edgecolor="black",
)

ax.set_xlabel("Community")
ax.set_ylabel("Number of Stores")
ax.set_title("Community Size")

plt.xticks(rotation=45)
plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "community_size.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

community_province_rows = []

for community_id, community in enumerate(
    communities,
    start=1,
):
    for store in community:
        community_province_rows.append(
            {
                "Community": f"Community {community_id}",
                "Province": G.nodes[store]["province"],
                "Store": store,
            }
        )

community_province_df = pd.DataFrame(
    community_province_rows
)

community_province_counts = (
    community_province_df
    .groupby(["Community", "Province"])
    .size()
    .unstack(fill_value=0)
)

fig, ax = plt.subplots(figsize=(11, 7))

community_province_counts.plot(
    kind="bar",
    stacked=True,
    ax=ax,
    edgecolor="black",
)

ax.set_xlabel("Community")
ax.set_ylabel("Number of Stores")
ax.set_title("Community Composition by Province")
ax.legend(title="Province")

plt.xticks(rotation=45)
plt.tight_layout()

fig.savefig(
    IMAGE_DIR / "community_province_composition.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close(fig)

pos_2d = nx.spring_layout(
    G,
    seed=42,
    weight="weight",
)

z_values = {
    node: G.degree(node)
    for node in G.nodes()
}

edge_x = []
edge_y = []
edge_z = []

for source, target in G.edges():
    edge_x.extend(
        [
            pos_2d[source][0],
            pos_2d[target][0],
            None,
        ]
    )
    edge_y.extend(
        [
            pos_2d[source][1],
            pos_2d[target][1],
            None,
        ]
    )
    edge_z.extend(
        [
            z_values[source],
            z_values[target],
            None,
        ]
    )

edge_trace = go.Scatter3d(
    x=edge_x,
    y=edge_y,
    z=edge_z,
    mode="lines",
    line=dict(
        width=2,
        color="#888888",
    ),
    hoverinfo="none",
    showlegend=False,
)

node_x = []
node_y = []
node_z = []
node_text = []
node_color = []

for node in G.nodes():
    province = G.nodes[node]["province"]

    node_x.append(pos_2d[node][0])
    node_y.append(pos_2d[node][1])
    node_z.append(z_values[node])

    weighted = G.degree(
        node,
        weight="weight",
    )

    node_text.append(
        f"<b>Store:</b> {node}<br>"
        f"<b>Province:</b> {province}<br>"
        f"<b>Connections:</b> {G.degree(node)}<br>"
        f"<b>Weighted connectivity:</b> {weighted}"
    )

    node_color.append(
        PROVINCE_COLORS.get(
            province,
            PROVINCE_COLORS["Unknown"],
        )
    )

node_trace = go.Scatter3d(
    x=node_x,
    y=node_y,
    z=node_z,
    mode="markers+text",
    text=list(G.nodes()),
    textposition="top center",
    hovertext=node_text,
    hoverinfo="text",
    marker=dict(
        size=7,
        color=node_color,
    ),
    name="Stores",
)

province_legend = []

for province in sorted(set(store_provinces.values())):
    province_legend.append(
        go.Scatter3d(
            x=[None],
            y=[None],
            z=[None],
            mode="markers",
            marker=dict(
                size=8,
                color=PROVINCE_COLORS.get(
                    province,
                    PROVINCE_COLORS["Unknown"],
                ),
            ),
            name=province,
        )
    )

fig_province = go.Figure(
    data=[
        edge_trace,
        node_trace,
    ] + province_legend
)

fig_province.update_layout(
    title="Interactive 3D Transportation Network — Province Analysis",
    scene=dict(
        xaxis_title="Network X",
        yaxis_title="Network Y",
        zaxis_title="Store Connectivity",
    ),
    margin=dict(l=0, r=0, b=0, t=50),
    legend=dict(title="Province"),
)

fig_province.write_html(
    INTERACTIVE_DIR / "province_network_3d.html"
)


community_node_color = []
community_node_text = []

for node in G.nodes():
    community_id = store_community[node]
    province = G.nodes[node]["province"]

    community_node_color.append(
        community_colors[
            (community_id - 1) % len(community_colors)
        ]
    )

    weighted = G.degree(
        node,
        weight="weight",
    )

    community_node_text.append(
        f"<b>Store:</b> {node}<br>"
        f"<b>Province:</b> {province}<br>"
        f"<b>Community:</b> {community_id}<br>"
        f"<b>Connections:</b> {G.degree(node)}<br>"
        f"<b>Weighted connectivity:</b> {weighted}"
    )

node_trace_community = go.Scatter3d(
    x=node_x,
    y=node_y,
    z=node_z,
    mode="markers+text",
    text=list(G.nodes()),
    textposition="top center",
    hovertext=community_node_text,
    hoverinfo="text",
    marker=dict(
        size=7,
        color=community_node_color,
    ),
    name="Stores",
)

community_legend = []

for community_id in range(
    1,
    len(communities) + 1,
):
    community_legend.append(
        go.Scatter3d(
            x=[None],
            y=[None],
            z=[None],
            mode="markers",
            marker=dict(
                size=8,
                color=community_colors[
                    (community_id - 1)
                    % len(community_colors)
                ],
            ),
            name=f"Community {community_id}",
        )
    )

fig_community = go.Figure(
    data=[
        edge_trace,
        node_trace_community,
    ] + community_legend
)

fig_community.update_layout(
    title="Interactive 3D Transportation Network — Community Analysis",
    scene=dict(
        xaxis_title="Network X",
        yaxis_title="Network Y",
        zaxis_title="Store Connectivity",
    ),
    margin=dict(l=0, r=0, b=0, t=50),
    legend=dict(title="Community"),
)

fig_community.write_html(
    INTERACTIVE_DIR / "community_network_3d.html"
)


fig_capacity = go.Figure()

for capacity in CAPACITIES:
    capacity_graph = capacity_graphs[capacity]

    capacity_edge_x = []
    capacity_edge_y = []
    capacity_edge_z = []

    for source, target in capacity_graph.edges():
        capacity_edge_x.extend(
            [
                pos_2d[source][0],
                pos_2d[target][0],
                None,
            ]
        )
        capacity_edge_y.extend(
            [
                pos_2d[source][1],
                pos_2d[target][1],
                None,
            ]
        )
        capacity_edge_z.extend(
            [
                z_values.get(source, 0),
                z_values.get(target, 0),
                None,
            ]
        )

    fig_capacity.add_trace(
        go.Scatter3d(
            x=capacity_edge_x,
            y=capacity_edge_y,
            z=capacity_edge_z,
            mode="lines",
            line=dict(
                width=3,
                color=CAPACITY_COLORS[capacity],
            ),
            name=CAPACITY_LABELS[capacity],
            hoverinfo="none",
        )
    )

capacity_node_x = []
capacity_node_y = []
capacity_node_z = []
capacity_node_text = []
capacity_node_colors = []

for node in G.nodes():
    province = G.nodes[node]["province"]

    capacity_node_x.append(pos_2d[node][0])
    capacity_node_y.append(pos_2d[node][1])
    capacity_node_z.append(z_values[node])

    weighted = G.degree(
        node,
        weight="weight",
    )

    capacity_node_text.append(
        f"<b>Store:</b> {node}<br>"
        f"<b>Province:</b> {province}<br>"
        f"<b>Connections:</b> {G.degree(node)}<br>"
        f"<b>Weighted connectivity:</b> {weighted}"
    )

    capacity_node_colors.append(
        PROVINCE_COLORS.get(
            province,
            PROVINCE_COLORS["Unknown"],
        )
    )

fig_capacity.add_trace(
    go.Scatter3d(
        x=capacity_node_x,
        y=capacity_node_y,
        z=capacity_node_z,
        mode="markers+text",
        text=list(G.nodes()),
        textposition="top center",
        hovertext=capacity_node_text,
        hoverinfo="text",
        marker=dict(
            size=7,
            color=capacity_node_colors,
        ),
        name="Stores",
    )
)

fig_capacity.update_layout(
    title="Interactive 3D Transportation Network — Truck Capacity",
    scene=dict(
        xaxis_title="Network X",
        yaxis_title="Network Y",
        zaxis_title="Store Connectivity",
    ),
    margin=dict(l=0, r=0, b=0, t=50),
    legend=dict(title="Truck Capacity"),
)

fig_capacity.write_html(
    INTERACTIVE_DIR / "truck_capacity_network_3d.html"
)


available_months = sorted(
    df["Month"].dropna().unique(),
    key=str,
)

if available_months:
    MTH = (
        "2016-10"
        if "2016-10" in available_months
        else available_months[0]
    )

    month_df = df[
        df["Month"] == MTH
    ]

    month_graph = nx.Graph()

    for stores in month_df["Stores"]:
        for source, target in itertools.combinations(
            sorted(set(stores)),
            2,
        ):
            if month_graph.has_edge(source, target):
                month_graph[source][target]["weight"] += 1
            else:
                month_graph.add_edge(
                    source,
                    target,
                    weight=1,
                )

    for node in month_graph.nodes():
        month_graph.nodes[node]["province"] = (
            store_provinces.get(node, "Unknown")
        )

    if month_graph.number_of_nodes() > 0:
        draw_network(
            month_graph,
            f"{MTH} — All Truck Sizes",
            f"monthly_network_{MTH}.png",
            capacity_edges={
                capacity: {
                    tuple(sorted((source, target)))
                    for stores in month_df.loc[
                        month_df["Capacity(T)"] == capacity,
                        "Stores",
                    ]
                    for source, target in itertools.combinations(
                        sorted(set(stores)),
                        2,
                    )
                }
                for capacity in CAPACITIES
            },
        )

print("FINAL TRANSPORTATION NETWORK SUMMARY")
print(f"Total stores: {G.number_of_nodes()}")
print(f"Total store relationships: {G.number_of_edges()}")
print(f"Network density: {nx.density(G):.4f}")
print(f"Number of communities: {len(communities)}")
print(f"Total delivery records: {len(delivery_df)}")
print(
    f"Average stores per delivery: "
    f"{delivery_df['Number_of_stores'].mean():.2f}"
)

if not valid_utilization.empty:
    print(
        f"Average truck utilization: "
        f"{valid_utilization.mean():.2f}%"
    )

print(
    f"Multi-store delivery percentage: "
    f"{len(multi_store_deliveries) / len(delivery_df) * 100:.2f}%"
)

print("\nGenerated folders:")
print(f"Images: {IMAGE_DIR.resolve()}")
print(f"Interactive 3D graphs: {INTERACTIVE_DIR.resolve()}")


interactive_files = [
    ("Province Network", "province_network_3d.html"),
    ("Community Network", "community_network_3d.html"),
    ("Truck Capacity Network", "truck_capacity_network_3d.html"),
]

index_html = "<html><head><title>Transportation Network Interactive Graphs</title></head><body><h1>Transportation Network Interactive Graphs</h1><ul>"

for title, filename in interactive_files:
    index_html += f"<li><a href='{filename}' target='_blank'>{title}</a></li>"

index_html += "</ul></body></html>"

(INTERACTIVE_DIR / "index.html").write_text(
    index_html,
    encoding="utf-8"
)

print("Static visualisations saved in:", IMAGE_DIR.resolve())
print("Interactive graphs saved in:", INTERACTIVE_DIR.resolve())
print("Interactive index:", (INTERACTIVE_DIR / "index.html").resolve())
