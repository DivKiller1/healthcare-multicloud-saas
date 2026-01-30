from fastapi import FastAPI
from pydantic import BaseModel
import math
import heapq

app = FastAPI(title="Routing Service")

class Point(BaseModel):
    id: int
    lat: float
    lon: float

class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    points: list[Point]

def distance(a_lat, a_lon, b_lat, b_lon):
    return math.sqrt((a_lat - b_lat)**2 + (a_lon - b_lon)**2)

def dijkstra(start, points):
    graph = {}
    all_nodes = [start] + points

    for a in all_nodes:
        graph[a["id"]] = {}
        for b in all_nodes:
            if a["id"] != b["id"]:
                graph[a["id"]][b["id"]] = distance(
                    a["lat"], a["lon"], b["lat"], b["lon"]
                )

    pq = [(0, start["id"], [])]
    visited = set()

    while pq:
        cost, node, path = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]

        if len(path) == len(all_nodes):
            return path

        for neighbor, weight in graph[node].items():
            if neighbor not in visited:
                heapq.heappush(pq, (cost + weight, neighbor, path))

    return []

@app.get("/health")
def health():
    return {"status": "ok", "service": "routing"}

@app.post("/route/optimize")
def optimize_route(req: RouteRequest):
    # Convert Pydantic models to plain dicts
    remaining = [
        {"id": p.id, "lat": p.lat, "lon": p.lon}
        for p in req.points
    ]

    current_lat = req.start_lat
    current_lon = req.start_lon

    visit_order = []

    while remaining:
        nearest = min(
            remaining,
            key=lambda p: distance(current_lat, current_lon, p["lat"], p["lon"])
        )

        visit_order.append(nearest["id"])
        current_lat = nearest["lat"]
        current_lon = nearest["lon"]
        remaining.remove(nearest)

    return {
        "visit_order": visit_order
    }
