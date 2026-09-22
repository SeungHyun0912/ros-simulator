import math
import pytest
from study_nodes.core import Motion, Request, Interlock, Lease

def test_arrival():
    m=Motion(); m.start(Request("a", 1, 0, speed=1))
    for _ in range(10): m.tick(0.1)
    assert m.phase=="SUCCEEDED"
    assert m.x==pytest.approx(1.0)

def test_cancel_is_terminal():
    m=Motion(); m.start(Request("a", 5, 0))
    m.tick(0.5); x=m.x; m.cancel(); m.tick(100)
    assert m.phase=="CANCELED" and m.x==x

def test_fault():
    m=Motion(); m.start(Request("a", 1, 0))
    m.fail("JAM"); m.tick(1)
    assert (m.phase,m.detail)==("FAILED","JAM")

def test_busy():
    m=Motion(); m.start(Request("a",1,0))
    with pytest.raises(ValueError, match="BUSY"):
        m.start(Request("b",2,0))

def test_duplicate_after_soft_reset():
    m=Motion(); m.start(Request("a",0,0)); m.tick(0)
    m.reset_idle()
    with pytest.raises(ValueError, match="DUPLICATE"):
        m.start(Request("a",0,0))

@pytest.mark.parametrize("speed", [0, -1, 1.1, math.nan, math.inf])
def test_invalid_speed(speed):
    with pytest.raises(ValueError):
        Motion().start(Request("a",1,0,speed=speed))

@pytest.mark.parametrize("timeout", [0,-1,math.inf])
def test_invalid_timeout(timeout):
    with pytest.raises(ValueError):
        Motion().start(Request("a",1,0,timeout_sec=timeout))

@pytest.mark.parametrize("x", [math.nan, math.inf, 101])
def test_invalid_position(x):
    with pytest.raises(ValueError):
        Motion().start(Request("a",x,0))

def test_timeout_wins_same_tick():
    m=Motion(); m.start(Request("a",1,0,speed=1,timeout_sec=1))
    m.tick(1)
    assert m.detail=="TIMEOUT"

def test_odom_observe_no_fake_integration():
    m=Motion(); m.start(Request("a",1,0)); m.tick(1,integrate=False)
    assert m.x==0 and m.busy
    m.observe(1,0); m.tick(0.01,integrate=False)
    assert m.phase=="SUCCEEDED"

def test_reset_busy():
    m=Motion(); m.start(Request("a",1,0))
    with pytest.raises(ValueError): m.reset_idle()

def test_capacity_fail_closed():
    m=Motion(capacity=1); m.start(Request("a",0,0)); m.tick(0)
    with pytest.raises(ValueError,match="LEDGER_FULL"):
        m.start(Request("b",0,0))

def test_negative_dt():
    with pytest.raises(ValueError): Motion().tick(-1)

def test_interlock():
    assert Interlock(True,True,True,True,True).ready()
    assert not Interlock(True,True,True,True,False).ready()

def test_lease_old_release_rejected():
    l=Lease(); a=l.acquire("amr_01"); l.release("amr_01",a)
    b=l.acquire("amr_01")
    assert b>a
    with pytest.raises(ValueError):
        l.release("amr_01",a)
    assert l.owner=="amr_01"

def test_lease_exclusion():
    l=Lease(); l.acquire("a")
    with pytest.raises(ValueError): l.acquire("b")
