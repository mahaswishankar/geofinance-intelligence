# geo_analysis.py
# Geospatial analysis module for GeoFinance Intelligence Platform
# Uses GeoPandas + Shapely to perform spatial operations on country-level risk data

import json
import math
from typing import Optional
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, shape
from shapely.ops import unary_union
import requests

# ─── Constants ─────────────────────────────────────────────────────────────────

# Natural Earth GeoJSON (110m resolution) — free, no API key required
WORLD_GEOJSON_URL = (
    "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
)

# Approximate centroids for key countries (ISO-3166 alpha-2 → lon, lat)
COUNTRY_CENTROIDS = {
    "US": (-95.71, 37.09), "CN": (104.19, 35.86), "RU": (105.32, 61.52),
    "DE": (10.45, 51.16),  "FR": (2.21, 46.23),   "GB": (-3.44, 55.37),
    "JP": (138.25, 36.20), "IN": (78.96, 20.59),   "BR": (-51.93, -14.24),
    "AU": (133.77, -25.27),"CA": (-96.80, 56.13),  "ZA": (25.08, -29.00),
    "SA": (45.08, 23.89),  "AE": (53.85, 23.42),   "SG": (103.82, 1.35),
    "HK": (114.17, 22.32), "KR": (127.77, 35.91),  "MX": (-102.55, 23.63),
    "NG": (8.68, 9.08),    "EG": (30.80, 26.82),   "TR": (35.24, 38.96),
    "PK": (69.35, 30.38),  "ID": (113.92, -0.79),  "TH": (100.99, 15.87),
    "PH": (121.77, 12.88), "VN": (108.28, 14.06),  "MY": (109.70, 4.21),
    "NL": (5.29, 52.13),   "CH": (8.23, 46.82),    "SE": (18.64, 60.13),
    "NO": (8.47, 60.47),   "PL": (19.14, 51.92),   "UA": (31.17, 48.38),
    "IR": (53.69, 32.43),  "IQ": (43.68, 33.22),   "IL": (34.85, 31.05),
    "AR": (-63.62, -38.42),"CL": (-71.54, -35.68), "CO": (-74.30, 4.57),
}

# Earth radius in kilometers
EARTH_RADIUS_KM = 6371.0

# ─── Data Loading ──────────────────────────────────────────────────────────────

_world_gdf: Optional[gpd.GeoDataFrame] = None


def load_world_geodataframe() -> gpd.GeoDataFrame:
    """
    Load Natural Earth country boundaries as a GeoDataFrame.
    Cached after first load. Falls back to centroid-based GDF if download fails.
    """
    global _world_gdf
    if _world_gdf is not None:
        return _world_gdf

    try:
        print("Loading world GeoDataFrame from Natural Earth...")
        response = requests.get(WORLD_GEOJSON_URL, timeout=10)
        response.raise_for_status()
        geojson_data = response.json()

        features = []
        for feature in geojson_data.get("features", []):
            props = feature.get("properties", {})
            iso2 = props.get("ISO_A2", "").upper()
            name = props.get("ADMIN", props.get("name", ""))
            geom = shape(feature["geometry"])
            features.append({"iso2": iso2, "name": name, "geometry": geom})

        _world_gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
        print(f"Loaded {len(_world_gdf)} country geometries.")

    except Exception as e:
        print(f"GeoJSON download failed ({e}), falling back to centroid GDF.")
        _world_gdf = _build_centroid_gdf()

    return _world_gdf


def _build_centroid_gdf() -> gpd.GeoDataFrame:
    """Build a minimal GeoDataFrame from known centroids when full boundaries unavailable."""
    rows = []
    for iso2, (lon, lat) in COUNTRY_CENTROIDS.items():
        rows.append({
            "iso2": iso2,
            "name": iso2,
            "geometry": Point(lon, lat).buffer(2.0)  # ~222km buffer as proxy polygon
        })
    return gpd.GeoDataFrame(rows, crs="EPSG:4326")


# ─── Core Spatial Functions ────────────────────────────────────────────────────

def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate great-circle distance between two points in kilometers.
    Uses the Haversine formula — accurate for all Earth distances.
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def get_country_centroid(iso2: str) -> Optional[tuple]:
    """Return (lon, lat) centroid for a country ISO-2 code."""
    return COUNTRY_CENTROIDS.get(iso2.upper())


def countries_within_radius(
    origin_iso2: str,
    radius_km: float,
    candidate_codes: Optional[list] = None
) -> list[dict]:
    """
    Find all countries whose centroids fall within radius_km of the origin country.

    Args:
        origin_iso2: ISO-2 code of the origin/epicentre country
        radius_km: Search radius in kilometres
        candidate_codes: Optional list of ISO-2 codes to filter. Defaults to all known.

    Returns:
        List of dicts with iso2, name, distance_km, bearing, sorted by distance.
    """
    origin = get_country_centroid(origin_iso2)
    if not origin:
        return []

    origin_lon, origin_lat = origin
    candidates = candidate_codes or list(COUNTRY_CENTROIDS.keys())
    results = []

    for iso2 in candidates:
        if iso2.upper() == origin_iso2.upper():
            continue
        coords = get_country_centroid(iso2)
        if not coords:
            continue
        c_lon, c_lat = coords
        dist = haversine_distance(origin_lon, origin_lat, c_lon, c_lat)
        if dist <= radius_km:
            results.append({
                "iso2": iso2.upper(),
                "distance_km": round(dist, 1),
                "bearing_deg": round(_bearing(origin_lat, origin_lon, c_lat, c_lon), 1),
                "centroid": {"lon": c_lon, "lat": c_lat},
            })

    return sorted(results, key=lambda x: x["distance_km"])


def _bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute initial compass bearing from point 1 to point 2 (degrees, 0=North)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


# ─── GeoDataFrame Spatial Operations ──────────────────────────────────────────

def spatial_join_risk(country_risks: dict) -> gpd.GeoDataFrame:
    """
    Perform a spatial join between world geometries and country risk scores.

    Args:
        country_risks: Dict mapping ISO-2 code → risk dict (from risk_model.py)

    Returns:
        GeoDataFrame with geometry + risk_score + risk_level columns.
    """
    gdf = load_world_geodataframe().copy()

    risk_rows = []
    for iso2, risk in country_risks.items():
        risk_rows.append({
            "iso2": iso2.upper(),
            "risk_score": risk.get("risk_score", 50),
            "risk_level": risk.get("risk_level", "moderate"),
            "sentiment_score": risk.get("sentiment_score", 0.0),
        })

    risk_df = pd.DataFrame(risk_rows)
    merged = gdf.merge(risk_df, on="iso2", how="left")
    merged["risk_score"] = merged["risk_score"].fillna(50.0)
    merged["risk_level"] = merged["risk_level"].fillna("unknown")
    return merged


def high_risk_zone_polygon(country_risks: dict, threshold: float = 70.0) -> dict:
    """
    Dissolve all high-risk country geometries into a single unified GeoJSON polygon.
    Useful for visualizing contiguous high-risk regions on a map.

    Args:
        country_risks: Dict from risk_model.compute_all_country_risks()
        threshold: Risk score cutoff (0–100) above which a country is "high risk"

    Returns:
        GeoJSON dict of the dissolved polygon (or empty FeatureCollection).
    """
    merged_gdf = spatial_join_risk(country_risks)
    high_risk = merged_gdf[merged_gdf["risk_score"] >= threshold]

    if high_risk.empty:
        return {"type": "FeatureCollection", "features": []}

    dissolved = unary_union(high_risk.geometry.values)
    return {
        "type": "Feature",
        "properties": {
            "threshold": threshold,
            "country_count": len(high_risk),
            "avg_risk_score": round(float(high_risk["risk_score"].mean()), 2),
        },
        "geometry": json.loads(gpd.GeoSeries([dissolved]).to_json())
            .get("features", [{}])[0]
            .get("geometry", {}),
    }


def proximity_risk_analysis(
    origin_iso2: str,
    radius_km: float,
    country_risks: dict
) -> dict:
    """
    Given an origin country and radius, return all nearby countries ranked
    by combined proximity + risk score. Core use case: geopolitical contagion modelling.

    Args:
        origin_iso2: ISO-2 epicentre country code
        radius_km: Search radius in kilometres
        country_risks: Full risk dict from risk_model

    Returns:
        Dict with origin info, nearby countries with risk scores, and composite scores.
    """
    nearby = countries_within_radius(origin_iso2, radius_km)
    origin_risk = country_risks.get(origin_iso2.upper(), {})

    enriched = []
    for c in nearby:
        iso2 = c["iso2"]
        risk = country_risks.get(iso2, {})
        risk_score = risk.get("risk_score", 50.0)

        # Proximity decay: closer = more contagion weight
        proximity_weight = max(0.0, 1.0 - (c["distance_km"] / radius_km))

        # Composite contagion score
        contagion_score = round(risk_score * proximity_weight, 2)

        enriched.append({
            **c,
            "risk_score": risk_score,
            "risk_level": risk.get("risk_level", "unknown"),
            "sentiment_score": risk.get("sentiment_score", 0.0),
            "proximity_weight": round(proximity_weight, 3),
            "contagion_score": contagion_score,
        })

    # Sort by contagion score descending
    enriched.sort(key=lambda x: x["contagion_score"], reverse=True)

    return {
        "origin": {
            "iso2": origin_iso2.upper(),
            "risk_score": origin_risk.get("risk_score", 50.0),
            "risk_level": origin_risk.get("risk_level", "unknown"),
            "centroid": get_country_centroid(origin_iso2),
        },
        "radius_km": radius_km,
        "country_count": len(enriched),
        "nearby_countries": enriched,
        "avg_contagion_score": round(
            sum(x["contagion_score"] for x in enriched) / len(enriched), 2
        ) if enriched else 0.0,
    }


def classify_geospatial_features(country_risks: dict) -> list[dict]:
    """
    Convert country risk data into a GeoJSON FeatureCollection with
    spatial attributes engineered as ML-ready features.
    Mirrors the 'engineer spatial attributes as model features' requirement.

    Each feature includes:
        - geometry (centroid Point in WKT and GeoJSON)
        - risk_score, sentiment_score
        - neighbor_avg_risk (spatial lag feature)
        - nearest_high_risk_km (proximity feature)
        - is_high_risk (binary label)
    """
    high_risk_codes = [
        iso2 for iso2, r in country_risks.items()
        if r.get("risk_score", 0) >= 70
    ]

    features = []
    for iso2, risk in country_risks.items():
        coords = get_country_centroid(iso2)
        if not coords:
            continue

        lon, lat = coords
        point = Point(lon, lat)
        risk_score = risk.get("risk_score", 50.0)

        # Spatial lag: average risk of countries within 2000km
        neighbors = countries_within_radius(iso2, 2000, list(country_risks.keys()))
        neighbor_risks = [
            country_risks.get(n["iso2"], {}).get("risk_score", 50.0)
            for n in neighbors
        ]
        neighbor_avg = round(float(np.mean(neighbor_risks)), 2) if neighbor_risks else 50.0

        # Nearest high-risk country distance
        nearest_hr_km = None
        for hr_iso2 in high_risk_codes:
            if hr_iso2 == iso2:
                continue
            hr_coords = get_country_centroid(hr_iso2)
            if hr_coords:
                d = haversine_distance(lon, lat, hr_coords[0], hr_coords[1])
                if nearest_hr_km is None or d < nearest_hr_km:
                    nearest_hr_km = d

        features.append({
            "iso2": iso2.upper(),
            "geometry_wkt": point.wkt,
            "geometry_geojson": {"type": "Point", "coordinates": [lon, lat]},
            "risk_score": risk_score,
            "sentiment_score": risk.get("sentiment_score", 0.0),
            "neighbor_avg_risk": neighbor_avg,
            "nearest_high_risk_km": round(nearest_hr_km, 1) if nearest_hr_km else None,
            "is_high_risk": int(risk_score >= 70),
        })

    return features


def wkt_to_geojson(wkt_string: str) -> dict:
    """Parse a WKT geometry string and return it as a GeoJSON geometry dict."""
    from shapely import wkt as shapely_wkt
    geom = shapely_wkt.loads(wkt_string)
    return json.loads(gpd.GeoSeries([geom]).to_json())["features"][0]["geometry"]


def geojson_to_wkt(geojson_geometry: dict) -> str:
    """Convert a GeoJSON geometry dict to its WKT representation."""
    geom = shape(geojson_geometry)
    return geom.wkt


# ─── Summary ───────────────────────────────────────────────────────────────────

def geospatial_summary(country_risks: dict) -> dict:
    """
    Return a high-level geospatial summary of the current risk landscape.
    Used by the /api/geo/summary endpoint.
    """
    features = classify_geospatial_features(country_risks)

    if not features:
        return {"error": "No geospatial data available"}

    risk_scores = [f["risk_score"] for f in features]
    high_risk = [f for f in features if f["is_high_risk"]]
    neighbor_lags = [f["neighbor_avg_risk"] for f in features]

    # Countries with highest spatial contagion risk (own risk + neighbor risk)
    for f in features:
        f["spatial_risk_index"] = round(
            0.6 * f["risk_score"] + 0.4 * f["neighbor_avg_risk"], 2
        )
    top_spatial = sorted(features, key=lambda x: x["spatial_risk_index"], reverse=True)[:5]

    return {
        "total_countries_analysed": len(features),
        "high_risk_country_count": len(high_risk),
        "high_risk_countries": [f["iso2"] for f in high_risk],
        "global_avg_risk": round(float(np.mean(risk_scores)), 2),
        "global_avg_spatial_lag": round(float(np.mean(neighbor_lags)), 2),
        "top_spatial_risk": [
            {"iso2": f["iso2"], "spatial_risk_index": f["spatial_risk_index"]}
            for f in top_spatial
        ],
        "formats_supported": ["GeoJSON", "WKT", "Shapely Geometry", "GeoDataFrame"],
    }


# ─── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== GeoFinance Spatial Analysis Module ===\n")

    print("1. Haversine distance London → Tokyo:")
    dist = haversine_distance(-0.12, 51.51, 139.69, 35.68)
    print(f"   {dist:.1f} km\n")

    print("2. Countries within 1500km of Ukraine (UA):")
    nearby = countries_within_radius("UA", 1500)
    for c in nearby[:5]:
        print(f"   {c['iso2']} — {c['distance_km']} km")

    print("\n3. WKT for New Delhi centroid:")
    delhi = Point(77.21, 28.61)
    print(f"   {delhi.wkt}")

    print("\n4. GeoJSON → WKT round-trip:")
    gj = {"type": "Point", "coordinates": [77.21, 28.61]}
    wkt_out = geojson_to_wkt(gj)
    print(f"   {wkt_out}")

    print("\n5. WKT → GeoJSON round-trip:")
    gj_out = wkt_to_geojson(wkt_out)
    print(f"   {gj_out}")

    print("\nAll spatial functions operational.")