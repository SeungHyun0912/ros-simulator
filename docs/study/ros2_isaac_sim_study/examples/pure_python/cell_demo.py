"""Run with the study_nodes package directory on PYTHONPATH."""
from study_nodes.core import Interlock, Lease
lease = Lease()
epoch = lease.acquire("amr_01")
gate = Interlock(docked=True, amr_stopped=True, arm_ready=True,
                 output_clear=True, communication_fresh=True)
assert gate.ready()
print(f"handover permitted; owner={lease.owner}, epoch={epoch}")
lease.release("amr_01", epoch)
try:
    lease.release("amr_01", epoch)
except ValueError as exc:
    print("duplicate release rejected:", exc)
