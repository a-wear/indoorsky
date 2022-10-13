from abc import ABC, abstractmethod
import json

class IAuditDatasource(ABC):
    
    @abstractmethod
    def verify_db(self) -> dict:
        pass
    
    @abstractmethod
    def verify_table(self) -> dict:
        pass
    
    @abstractmethod
    def insert_audit(self, data: json) -> dict:
        pass
    
   
    @abstractmethod
    def get_audit_by_user_id(self, user_id: str) -> dict:
        pass