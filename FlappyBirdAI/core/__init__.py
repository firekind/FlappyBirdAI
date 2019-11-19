from abc import ABC, abstractmethod
from enum import Enum
import pygame

class Entity(ABC):
    """
    Represents an entity in the game.
    """
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def update(self, delta: float) -> None:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def rect(self) -> pygame.Rect:
        raise NotImplementedError

    @abstractmethod
    def on_collide(self, entity: 'Entity') -> 'Entity':
        raise NotImplementedError

class Axis(Enum):
    """
    Represents the Axes.
    """
    
    horizontal = 1
    vertical = 2
    all = 3

class Direction(Enum):
    """
    Represents directions.
    """

    up = 1
    down = 2
    left = 3
    right = 4
    horizontal = 5
    vertical = 6
    all = 7
