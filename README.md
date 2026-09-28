Transportation Network Analysis with Graph Theory 🚚

Graph-based analysis of a retail transportation network to understand delivery patterns, truck capacity and store connectivity.

Objective

Build graphical representations of a retail transportation network to support transportation analysis and optimisation studies using Graph Theory.

Introduction

Delivery records are transformed into a network where stores are nodes and co-deliveries are edges. Repeated co-deliveries are represented through edge weights, while store provinces provide an additional network attribute.

The project combines logistics analytics with graph analysis to study route consolidation, truck-capacity patterns, store connectivity, province relationships and potential route-group opportunities.

Inspiration & Credit

This project was independently developed with inspiration from the transportation network analysis work of Samir Saci.

Original work:

Transportation Network Analysis with Graph Theory

Original GitHub Repository

The original work is acknowledged as the conceptual reference for the transportation-network approach and visualisation style. Additional network metrics, province analysis, community detection, operational analysis and interactive 3D visualisations were developed independently.

Scenario

The project analyses retail delivery records containing delivery time information, truck capacity, transported tons and store codes included in each delivery. A separate reference sheet maps store codes to provinces.

Graph Representation

Element

Meaning

Node

Store

Edge

Stores delivered together

Edge weight

Co-delivery frequency

Node attribute

Province

Truck capacities

3.5T, 5T and 8T

Truck Capacity Analysis

The project compares 3.5T, 5T and 8T trucks through route counts, delivery distribution and average stores delivered per route.







Network Analysis

The transportation network is analysed using NetworkX to identify highly connected stores, weighted connectivity, frequently co-delivered store pairs, isolated stores and network density.



Truck-Specific Networks









The combined capacity visualisation uses red for 3.5T, yellow for 5T and blue for 8T, while store nodes are coloured by province.

Store & Delivery Insights















Community Detection

Weighted community detection is used to identify groups of stores with relatively strong internal connectivity. These communities are analytical groups, not confirmed operational routes.







Interactive 3D Networks

Three interactive Plotly visualisations are generated:

Province-Based 3D Network

Community-Based 3D Network

Truck Capacity 3D Network

The 3D networks allow rotation, zooming and store-level inspection through interactive hover information.

Further Analysis

The network can support investigation of:

highly connected and isolated stores

repeated store-to-store relationships

province-level connectivity

truck-capacity-specific network structure

multi-store delivery opportunities

strongly connected store groups

Actual route optimisation would require additional operational constraints such as road distance, delivery windows, vehicle availability, capacity limits and transportation cost.

Project Structure

Transportation-Network-Analysis/
│
├── main.py
├── README.md
├── .gitignore
│
├── data/
│   ├── delivery records.xlsx
│   └── store province.xlsx
│
├── images/
│   ├── number_of_routes_per_truck_size.png
│   ├── delivery_distribution_by_truck_size.png
│   ├── store_deliveries_per_route.png
│   ├── single_vs_multi_store_deliveries.png
│   ├── stores_per_delivery_distribution.png
│   ├── province_distribution.png
│   ├── most_connected_stores.png
│   ├── weighted_store_connectivity.png
│   ├── strongest_store_pairs.png
│   ├── province_connectivity_heatmap.png
│   ├── full_transportation_network.png
│   ├── network_3_5T.png
│   ├── network_5T.png
│   ├── network_8_0T.png
│   ├── truck_capacity_network_comparison.png
│   ├── community_network.png
│   ├── community_size.png
│   ├── community_province_composition.png
│   └── monthly_network_<month>.png
│
└── interactive/
    ├── province_network_3d.html
    ├── community_network_3d.html
    └── truck_capacity_network_3d.html

Dataset

The project data is available in the data/ folder:

Delivery Records

Store Province Reference

Technologies

Python · Pandas · NumPy · NetworkX · Matplotlib · Plotly · OpenPyXL

Getting Started

pip install pandas numpy networkx matplotlib plotly openpyxl
python main.py

The script generates the static visualisations in images/ and the interactive 3D HTML files in interactive/.

Author

Abirami Kumarasamy
MSc Data Science with Logistics & Supply Chain Management

Focus: Supply Chain Analytics · Logistics Analytics · Transportation Analytics · Graph Theory

Acknowledgement

Special thanks to Samir Saci for the original transportation network analysis work that inspired this project.

https://github.com/samirsaci/graph-theory

https://www.samirsaci.com/transportation-network-analysis-with-graph-theory/
