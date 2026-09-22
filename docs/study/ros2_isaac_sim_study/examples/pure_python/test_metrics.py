import pytest
from summarize import percentile, summarize

def test_nearest_rank():
    assert percentile(list(range(1,101)),95)==95
    assert percentile([1,2],99)==2

def test_empty_rejected():
    with pytest.raises(ValueError): percentile([],95)
    with pytest.raises(ValueError): summarize([])

def test_summary():
    r=summarize([{"accepted":True,"success":True,
                  "accept_latency_ms":10,"completion_ms":100}])
    assert r["success_records"]==1
    assert r["accept_latency_ms"]["p95"]==10
