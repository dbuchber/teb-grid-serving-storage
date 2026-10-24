from fakes import STATION_IDS, write_fake_prepared
from gridsim.data import load_prepared


def test_load_prepared_roundtrip(tmp_path):
    p = load_prepared(write_fake_prepared(tmp_path), 2023)
    assert p.pv_bins.shape == (8760, 4) and p.nodes_station.shape == (10,)
    assert p.station_ids == STATION_IDS
    assert p.first_weekday == 6  # 1.1.2023 Sonntag
    assert p.n_stations == 3
    assert list(p.kva) == [160, 250, 125]
