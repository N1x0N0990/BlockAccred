"""Thin wrapper around ../../ml/anomaly_detection.py (Isolation Forest)."""
import os
import sys

ML_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml"))
if ML_DIR not in sys.path:
    sys.path.insert(0, ML_DIR)

import anomaly_detection as _ad  # noqa: E402

score = _ad.score
history = _ad.history
train = _ad.train
THRESHOLD = _ad.THRESHOLD
