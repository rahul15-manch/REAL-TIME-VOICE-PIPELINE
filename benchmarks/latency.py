
import time
from app.session.manager import SessionManager

def benchmark_session():
    manager = SessionManager()
    times_create = []
    times_lookup = []
    
    for _ in range(100):
        t0 = time.perf_counter()
        session = manager.create_session()
        t1 = time.perf_counter()
        times_create.append((t1 - t0) * 1000)
        
        t0 = time.perf_counter()
        manager.get_session(session.session_id)
        t1 = time.perf_counter()
        times_lookup.append((t1 - t0) * 1000)
        
    return {"create": times_create, "lookup": times_lookup}
