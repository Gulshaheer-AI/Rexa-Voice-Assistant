from abc import ABC, abstractmethod

class Skill(ABC):
    @abstractmethod
    def matches(self, command: str) -> bool:
        pass

    @abstractmethod
    def execute(self, command: str, speak_func):
        pass