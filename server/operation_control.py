"""Per-request cancellation and content-free progress."""
import contextlib
import threading
from wda_client import WDAError

class OperationControl:
    def __init__(self):self.local=threading.local()

    @contextlib.contextmanager
    def operation(self,event=None,progress=None):
        previous=getattr(self.local,"state",None)
        self.local.state={"event":event or threading.Event(),"progress":progress,"pending":False,"completed":0,"total":None}
        try:yield
        finally:self.local.state=previous

    def check(self):
        state=getattr(self.local,"state",None)
        if state and state["event"].is_set():
            uncertain=state["pending"]
            raise WDAError("action_uncertain" if uncertain else "cancelled","Request cancelled; inspect fresh state before continuing. Completed actions must not be replayed.",uncertain=uncertain,details={"cancelled":True,"completed_steps":state["completed"],"action_executed":"unknown" if uncertain else state["completed"]>0,"replay_action":False})

    def before_request(self,readonly):
        self.check()
        state=getattr(self.local,"state",None)
        if state:state["pending"]=not readonly

    def after_request(self):
        self.check()
        state=getattr(self.local,"state",None)
        if state:state["pending"]=False

    def progress(self,completed,total):
        state=getattr(self.local,"state",None)
        if state:
            state.update(completed=completed,total=total)
            if state["progress"]:state["progress"](completed,total)
        self.check()
