"""
ResilienceAI - Infrastructure Network & Cascade Analysis
Models critical infrastructure as a network graph for vulnerability assessment.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from config import PROCESSED_DIR, RAW_DIR

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


def haversine_km(lat1, lon1, lat2, lon2):
    """Haversine distance in km (scalar version)."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


class InfrastructureNetwork:
    """Build and analyze infrastructure networks for cascade risk assessment."""

    def __init__(self):
        self.county_df = None
        self.facility_data = {}
        self._load_data()

    def _load_data(self):
        """Load county features and facility data."""
        path = PROCESSED_DIR / "county_features.csv"
        if path.exists():
            self.county_df = pd.read_csv(path, dtype={"fips": str})

        for ftype in ["hospitals", "fire_stations", "ems_stations", "nursing_homes"]:
            fpath = RAW_DIR / f"hifld_{ftype}.csv"
            if fpath.exists():
                self.facility_data[ftype] = pd.read_csv(fpath)

    def build_facility_network(self, center_lat, center_lon, radius_km=80,
                                connectivity_km=50):
        """
        Build a NetworkX graph of facilities within radius of a point.

        Args:
            center_lat, center_lon: Center point
            radius_km: Radius to include facilities
            connectivity_km: Max distance for network edges

        Returns:
            NetworkX graph, facility dataframe
        """
        if not HAS_NETWORKX:
            return None, pd.DataFrame()

        all_facilities = []
        for ftype, fdf in self.facility_data.items():
            fdf_clean = fdf.dropna(subset=["latitude", "longitude"]).copy()
            if len(fdf_clean) == 0:
                continue
            # Filter to radius
            dists = np.array([
                haversine_km(center_lat, center_lon, row["latitude"], row["longitude"])
                for _, row in fdf_clean.iterrows()
            ])
            mask = dists <= radius_km
            nearby = fdf_clean[mask].copy()
            nearby["facility_type"] = ftype.replace("_", " ").title()
            nearby["dist_to_center_km"] = dists[mask]
            all_facilities.append(nearby)

        if not all_facilities:
            return nx.Graph(), pd.DataFrame()

        facilities = pd.concat(all_facilities, ignore_index=True)

        # Build graph
        G = nx.Graph()
        for idx, row in facilities.iterrows():
            G.add_node(idx,
                       facility_type=row["facility_type"],
                       lat=row["latitude"],
                       lon=row["longitude"],
                       name=row.get("NAME", row.get("name", f"Facility {idx}")),
                       dist_to_center=row["dist_to_center_km"])

        # Add edges based on proximity
        positions = facilities[["latitude", "longitude"]].values
        n = len(facilities)
        for i in range(n):
            for j in range(i + 1, min(n, i + 200)):  # Cap edge computation
                dist = haversine_km(
                    positions[i][0], positions[i][1],
                    positions[j][0], positions[j][1]
                )
                if dist <= connectivity_km:
                    G.add_edge(i, j, weight=dist)

        return G, facilities

    def analyze_network(self, center_lat, center_lon, radius_km=80):
        """
        Full network vulnerability analysis for an area.

        Returns:
            dict with network metrics and critical facility identification
        """
        if not HAS_NETWORKX:
            return {"error": "NetworkX not installed. Run: pip install networkx"}

        G, facilities = self.build_facility_network(center_lat, center_lon, radius_km)

        if G.number_of_nodes() < 2:
            return {
                "total_facilities": G.number_of_nodes(),
                "network_density": 0,
                "connected_components": G.number_of_nodes(),
                "articulation_points": 0,
                "max_betweenness": 0,
                "avg_clustering": 0,
                "vulnerability_score": 1.0,
                "critical_facilities": [],
                "facility_type_counts": {},
            }

        # Core metrics
        density = nx.density(G)
        components = nx.number_connected_components(G)

        # Betweenness centrality (identifies critical bottleneck facilities)
        betweenness = nx.betweenness_centrality(G, weight="weight")
        max_betweenness = max(betweenness.values())

        # Articulation points (single points of failure)
        artic_points = list(nx.articulation_points(G))

        # Clustering coefficient
        avg_clustering = nx.average_clustering(G)

        # Identify critical facilities (high betweenness or articulation points)
        critical = []
        for node_id in sorted(betweenness, key=betweenness.get, reverse=True)[:10]:
            node_data = G.nodes[node_id]
            critical.append({
                "name": node_data.get("name", f"Node {node_id}"),
                "type": node_data.get("facility_type", "Unknown"),
                "betweenness_centrality": round(betweenness[node_id], 4),
                "is_articulation_point": node_id in artic_points,
                "lat": node_data.get("lat"),
                "lon": node_data.get("lon"),
            })

        # Facility type breakdown
        type_counts = {}
        for _, data in G.nodes(data=True):
            ft = data.get("facility_type", "Unknown")
            type_counts[ft] = type_counts.get(ft, 0) + 1

        # Composite vulnerability score (0=resilient, 1=vulnerable)
        vuln_score = (
            0.3 * (1 - density) +
            0.2 * min(components / 5, 1) +
            0.2 * max_betweenness +
            0.15 * (len(artic_points) / max(G.number_of_nodes(), 1)) +
            0.15 * (1 - avg_clustering)
        )

        return {
            "total_facilities": G.number_of_nodes(),
            "total_connections": G.number_of_edges(),
            "network_density": round(density, 4),
            "connected_components": components,
            "articulation_points": len(artic_points),
            "max_betweenness_centrality": round(max_betweenness, 4),
            "avg_clustering_coefficient": round(avg_clustering, 4),
            "vulnerability_score": round(vuln_score, 4),
            "critical_facilities": critical,
            "facility_type_counts": type_counts,
        }

    def simulate_cascade(self, center_lat, center_lon, failed_facility_idx=None,
                          radius_km=80, failure_threshold=0.5):
        """
        Simulate cascade failure starting from a facility removal.

        Args:
            center_lat, center_lon: Area center
            failed_facility_idx: Index of initially failed facility (default: highest betweenness)
            radius_km: Analysis radius
            failure_threshold: Load threshold that triggers cascade

        Returns:
            dict with cascade progression and impact
        """
        if not HAS_NETWORKX:
            return {"error": "NetworkX not installed"}

        G, facilities = self.build_facility_network(center_lat, center_lon, radius_km)
        if G.number_of_nodes() < 3:
            return {"cascade_steps": 0, "total_failed": G.number_of_nodes(),
                    "cascade_ratio": 1.0}

        # Pick initial failure point
        if failed_facility_idx is None:
            betweenness = nx.betweenness_centrality(G, weight="weight")
            failed_facility_idx = max(betweenness, key=betweenness.get)

        # Simulate cascade
        failed = {failed_facility_idx}
        cascade_log = [{"step": 0, "newly_failed": [failed_facility_idx],
                        "total_failed": 1}]

        for step in range(1, 20):
            newly_failed = set()
            for node in list(G.nodes()):
                if node in failed:
                    continue
                # Count how many neighbors have failed
                neighbors = set(G.neighbors(node))
                if not neighbors:
                    continue
                failed_neighbor_ratio = len(neighbors & failed) / len(neighbors)
                if failed_neighbor_ratio >= failure_threshold:
                    newly_failed.add(node)

            if not newly_failed:
                break

            failed |= newly_failed
            cascade_log.append({
                "step": step,
                "newly_failed": list(newly_failed),
                "total_failed": len(failed),
            })

        return {
            "initial_failure": failed_facility_idx,
            "cascade_steps": len(cascade_log) - 1,
            "total_failed": len(failed),
            "total_facilities": G.number_of_nodes(),
            "cascade_ratio": round(len(failed) / G.number_of_nodes(), 4),
            "cascade_log": cascade_log,
        }

    def analyze_county(self, fips):
        """Analyze network for a specific county by FIPS code."""
        if self.county_df is None:
            return {"error": "County data not loaded"}
        match = self.county_df[self.county_df["fips"] == str(fips)]
        if match.empty:
            return {"error": f"County {fips} not found"}
        row = match.iloc[0]
        return self.analyze_network(row["latitude"], row["longitude"])


if __name__ == "__main__":
    net = InfrastructureNetwork()
    if net.county_df is not None and HAS_NETWORKX:
        # Test with a sample county
        sample = net.county_df.iloc[0]
        print(f"Analyzing network around {sample['county_name']}...")
        result = net.analyze_network(sample["latitude"], sample["longitude"], radius_km=50)
        for k, v in result.items():
            if k != "critical_facilities":
                print(f"  {k}: {v}")
        print(f"  Critical facilities: {len(result['critical_facilities'])}")
    else:
        print("Run pipeline first or install networkx.")
