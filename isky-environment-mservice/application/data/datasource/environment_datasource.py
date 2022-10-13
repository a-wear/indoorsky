from abc import ABC, abstractmethod
import json

class IEnvironmentDatasource(ABC):
    
    @abstractmethod
    def verify_db(self) -> dict:
        pass
    
    @abstractmethod
    def verify_table(self) -> dict:
        pass
    
    @abstractmethod
    def create_environment(self, data: json) -> dict:
        pass
    
    @abstractmethod
    def get_environments(self) -> dict:
        pass
    
    @abstractmethod
    def get_environment_by_id(self, env_id:str) -> dict:
        pass
    
    @abstractmethod
    def get_environment_by_name(self, name:str) -> dict:
        pass
    
    @abstractmethod
    def delete_environment(self, env_id:str) -> dict:
        pass
    
    @abstractmethod
    def update_environment(self, env_id:str, name: str, address: str, 
                           num_buildings:int, is_public:bool, 
                           is_active: bool) -> dict:
        pass
    
    
    