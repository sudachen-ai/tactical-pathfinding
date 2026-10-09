"""Metrics for a path that excludes the start cell."""
import math

def path_length(path, start):
    previous = (int(start[0]), int(start[1]))
    total = 0.0
    for cell in path:
        total += math.dist(previous, cell)
        previous = cell
    return total

def path_threat(path, threat_map):
    return sum(threat_map[row][col] for col, row in path)
