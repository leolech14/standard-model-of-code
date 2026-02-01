from abc import ABC, abstractmethod
from typing import Dict, Any, List
import time
import hashlib

class Courier(ABC):
    """
    The Base Worker Agent.

    A Courier is an entity that performs work on a Parcel.
    It adheres to the Logistics Law by modifying the Waybill to track its actions.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def checkout(self, parcel: Dict[str, Any]) -> Dict[str, Any]:
        """
        'Checks out' a parcel for work.
        Adds a 'checkout' event to the waybill.
        """
        parcel = parcel.copy() # Don't mutate original yet
        self._stamp_waybill(parcel, "checkout")
        return parcel

    def checkin(self, parcel: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """
        'Checks in' the finished work.
        Adds a 'checkin' event and potentially updates the parcel content/metadata.
        """
        self._stamp_waybill(parcel, "checkin", result_hash=self._hash(result))

        # In a real system, this would write back to the DB/File
        # For simulation, we return the modified parcel
        parcel['work_result'] = result
        return parcel

    @abstractmethod
    def process(self, content: str) -> str:
        """
        The actual work logic. Must be implemented by subclasses.
        returns: The result of the work.
        """
        pass

    def run(self, parcel: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main execution lifecycle.
        1. Checkout
        2. Process via subclass logic
        3. Checkin
        """
        active_parcel = self.checkout(parcel)

        try:
            # The actual work happening here
            self._stamp_waybill(active_parcel, "work_start")
            result = self.process(active_parcel.get('content', ''))
            self._stamp_waybill(active_parcel, "work_complete")

            final_parcel = self.checkin(active_parcel, result)
            return final_parcel

        except Exception as e:
            self._stamp_waybill(active_parcel, "work_failed", error=str(e))
            return active_parcel

    def _stamp_waybill(self, parcel: Dict[str, Any], event: str, **kwargs):
        """Helper to append to the route."""
        if 'waybill' not in parcel:
            parcel['waybill'] = {'route': []}

        timestamp = int(time.time())
        stamp = {
            "event": event,
            "agent": self.agent_id,
            "timestamp": timestamp,
            **kwargs
        }

        parcel['waybill']['route'].append(stamp)

    def _hash(self, data: Any) -> str:
        """Simple hash for integrity."""
        return hashlib.sha256(str(data).encode('utf-8')).hexdigest()[:12]
