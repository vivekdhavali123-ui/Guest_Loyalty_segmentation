"""
Accor Loyalty Segmentation Module
"""
from .rfm import compute_rfm_segments
from .kmeans_clusterer import AccorKMeansClusterer

__all__ = ["compute_rfm_segments", "AccorKMeansClusterer"]
