import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Protocol
from app.models.routine import RoutineResponse


class RoutineStorageInterface(Protocol):
    """Interface for routine storage implementations"""
    
    def create_routine(self, routine_data: Dict) -> RoutineResponse:
        """Create a new routine and return it as RoutineResponse"""
        ...
    
    def get_routine(self, routine_id: str) -> Optional[RoutineResponse]:
        """Get a routine by ID as RoutineResponse"""
        ...
    
    def update_routine(self, routine_id: str, routine_data: Dict) -> bool:
        """Update an existing routine"""
        ...
    
    def delete_routine(self, routine_id: str) -> bool:
        """Delete a routine"""
        ...
    
    def list_routines(self) -> List[RoutineResponse]:
        """List all routines as RoutineResponse objects"""
        ...


class JSONRoutineStore:
    """JSON file-based storage for routines"""
    
    def __init__(self, storage_path: str = "storage/routines.json"):
        self.storage_path = Path(storage_path)
        self.routines = self._load_routines()
    
    def _load_routines(self) -> Dict:
        """Load routines from JSON file"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading routines: {e}")
                return {}
        return {}
    
    def _save_routines(self):
        """Save routines to JSON file"""
        try:
            # Create directory if it doesn't exist
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(self.routines, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving routines: {e}")
    
    def create_routine(self, routine_data: Dict) -> str:
        """Store routine data with generated ID"""
        routine_id = str(uuid.uuid4())
        routine_data = routine_data.copy()
        routine_data['routine_id'] = routine_id
        routine_data['created_at'] = datetime.now().isoformat()
        routine_data['updated_at'] = datetime.now().isoformat()
        
        self.routines[routine_id] = routine_data
        self._save_routines()
        return routine_id
    
    def get_routine(self, routine_id: str) -> Optional[Dict]:
        """Get routine data"""
        return self.routines.get(routine_id)
    
    def update_routine(self, routine_id: str, update_data: Dict) -> bool:
        """Update routine with new data"""
        if routine_id not in self.routines:
            return False
        
        existing = self.routines[routine_id]
        existing.update(update_data)
        existing['updated_at'] = datetime.now().isoformat()
        
        self.routines[routine_id] = existing
        self._save_routines()
        return True
    
    def delete_routine(self, routine_id: str) -> bool:
        """Delete routine"""
        if routine_id in self.routines:
            del self.routines[routine_id]
            self._save_routines()
            return True
        return False
    
    def list_routines(self) -> List[Dict]:
        """List all routines"""
        return list(self.routines.values())

# Global storage instance
routine_storage = JSONRoutineStore()