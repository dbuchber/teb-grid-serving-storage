import hashlib
from pathlib import Path

from gridsim import legacy

LEGACY_DIR = Path(legacy.__file__).parent


def test_checksums_match():
    lines = (LEGACY_DIR / 'SHA256SUMS').read_text().splitlines()
    assert len(lines) == 7
    for line in lines:
        digest, name = line.split()
        assert hashlib.sha256((LEGACY_DIR / name).read_bytes()).hexdigest() == digest, name


def test_load_resolves_cross_imports():
    m = legacy.load('steyr_storage_need')
    assert hasattr(m, 'segment_row')
    assert m.sim.TRAFO_SIZES == (125, 160, 250, 400, 630, 800, 1000)
