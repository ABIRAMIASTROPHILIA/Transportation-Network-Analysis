Transportation Network Analysis with Graph Theory 🚚

Use Graph Theory to analyse a retail transportation network, understand store connectivity and explore route optimisation opportunities.

Objective

Build graphical representations of a retail transportation network to understand delivery patterns, truck capacity, store connectivity and network structure.

Introduction

Retail transportation involves serving stores through a combination of single-store and multi-store deliveries.

In this project, historical delivery records are transformed into a network to study how stores are connected through shared delivery routes.

The analysis combines operational delivery analysis with Graph Theory, province-level analysis, community detection and interactive 3D visualisation.

Inspiration

This project was independently developed with inspiration from the work of Samir Saci on transportation network analysis using Graph Theory.

Original article:
https://www.samirsaci.com/transportation-network-analysis-with-graph-theory/

Original GitHub repository:
https://github.com/samirsaci/graph-theory

Samir Saci's work is acknowledged as the conceptual reference for the transportation-network approach. The additional analyses and visualisations in this repository were developed independently.

Scenario

The project uses retail delivery records containing:

Delivery period

Delivery date

Truck capacity

Total transported tons

Store codes included in each delivery

A separate reference file maps store codes to provinces.

Solution: Graph Theory

The transportation network is represented as an undirected weighted graph.

Node → Store

Edge → Two stores delivered together

Edge weight → Co-delivery frequency

Node attribute → Province

Truck capacity → 3.5T, 5T or 8T

For example, a delivery containing three stores creates connections between each pair of stores.

Exploratory Analysis

Number of Routes per Truck Size



Distribution of Store Deliveries by Truck Size



Store Deliveries per Route



Single-Store vs Multi-Store Deliveries



Transportation Network

The complete delivery network is constructed from historical co-delivery relationships.



Truck Capacity Analysis

The network is also analysed separately for:

3.5T

5T

8T

3.5T Network



5T Network



8T Network



Combined Truck Capacity Network

Truck-capacity relationships are visualised using:

🔴 3.5T

🟡 5T

🔵 8T

Store nodes are coloured by province.



Network Analysis

The project analyses store connectivity using:

Degree

Weighted degree

Network density

Isolated stores

Frequently co-delivered store pairs

Most Connected Stores



Weighted Store Connectivity



Strongest Store Pairs



Province Analysis

Store-level relationships are also aggregated at province level.

Store Distribution by Province



Province Connectivity



Community Detection

Weighted community detection is used to identify groups of stores with relatively strong internal connections.



Community Size



Community Composition by Province



These communities are analytical network groups rather than confirmed operational routes. Actual route planning would require operational constraints such as distance, delivery windows, vehicle availability and transportation cost.

Interactive 3D Network Analysis

The project also includes interactive Plotly visualisations for deeper network exploration.

Province-Based 3D Network

Open Interactive Province Network

Community-Based 3D Network

Open Interactive Community Network

Truck Capacity 3D Network

Open Interactive Truck Capacity Network

Further Analysis

The network can be used to investigate questions such as:

Which stores are highly connected?

Which stores are isolated?

Which store pairs are repeatedly delivered together?

How does truck capacity affect network structure?

Which provinces have stronger transportation relationships?

Which store groups could be investigated for future route consolidation?

The analysis provides decision support and does not by itself produce an operationally feasible optimised route.

Files

Transportation-Network-Analysis/
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
│   ├── network_5_0T.png
│   ├── network_8_0T.png
│   ├── truck_capacity_network_comparison.png
│   ├── community_network.png
│   ├── community_size.png
│   └── community_province_composition.png
│
├── interactive/
│   ├── province_network_3d.html
│   ├── community_network_3d.html
│   └── truck_capacity_network_3d.html
│
├── main.py
└── README.md

Getting Started

pip install pandas numpy networkx matplotlib plotly openpyxl
python main.py

Static visualisations are saved in images/ and interactive 3D visualisations are saved in interactive/.

Technologies

Python · Pandas · NumPy · NetworkX · Matplotlib · Plotly · OpenPyXL

Acknowledgement

Special thanks to Samir Saci for the original transportation-network analysis work that inspired this project.

Original work:

https://github.com/samirsaci/graph-theory

https://www.samirsaci.com/transportation-network-analysis-with-graph-theory/

This repository is an independent implementation and extension. The additional operational analysis, weighted network metrics, province analysis, community detection and interactive 3D visualisations were developed independently.

Author

Abirami Kumarasamy

MSc Data Science with Logistics & Supply Chain Management
