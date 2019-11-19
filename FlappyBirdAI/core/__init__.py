from typing import List, Tuple, Callable
from abc import ABC, abstractmethod
from enum import Enum
import pygame

class Entity:
    """
    Represents an entity in the game.
    """
    def __init__(self):
        self.components: List['Component'] = []
        self.is_collidable = False
        self.transform_component = None
        self.render_component = None
        self.collision_component = None

    def add_component(self, component: 'Component') -> None:
        if component.id == ComponentID.TransformComponent:
            self.transform_component = component
        elif component.id == ComponentID.RenderComponent:
            self.render_component = component
        elif component.id == ComponentID.CollisionComponent:
            self.collision_component = component

        self.components.append(component)

class Component(ABC):
    def __init__(self, ID: 'ComponentID'):
        self.id: 'ComponentID' = ID

    @abstractmethod
    def update(self, delta: float) -> None:
        raise NotImplementedError

    def render(self, screen: pygame.Surface) -> None:
        raise NotImplementedError


class ComponentID(Enum):
    TransformComponent = 1
    RenderComponent = 2
    CollisionComponent = 3

class TransformComponent(Component):
    def __init__(self, pos: pygame.Vector2 = pygame.Vector2(0, 0), 
                 rot: pygame.Vector2 = pygame.Vector2(0, 0),
                 scale: pygame.Vector2 = pygame.Vector2(1, 1),
                 speed: float = 5):
        Component.__init__(self, ComponentID.TransformComponent)
        self.pos: pygame.Vector2 = pos
        self.rot: pygame.Vector2 = rot
        self.scale: pygame.Vector2 = scale
        self.speed: float = speed
        self.dx: float = 0
        self.dy: float = 0

    def translate(self, dx: float, dy: float) -> None:
        self.dx = dx
        self.dy = dy

    def move(self, direction: 'Direction') -> None:
        if direction == Direction.up:
            self.dy -= self.speed
        elif direction == Direction.down:
            self.dy += self.speed
        elif direction == Direction.right:
            self.dx -= self.speed
        elif direction == Direction.left:
            self.dx += self.speed
        else:
            pass

    def stop(self, direction: 'Direction') -> None:
        if direction == Direction.horizontal:
            self.dx = 0
        elif direction == Direction.vertical:
            self.dy = 0
        elif direction == Direction.all:
            self.dx = 0
            self.dy = 0
        else:
            pass
    
    def update(self, delta: float) -> None:
        self.pos.x += self.dx
        self.pos.y += self.dy

    def render(self, screen: pygame.Surface) -> None:
        pass


class RenderComponent(Component, pygame.sprite.Sprite):
    def __init__(self, transform: TransformComponent, img_path: str = None, 
                 color: Tuple[int, int, int] = None,
                 size: Tuple[float, float] = None):
        
        Component.__init__(self, ComponentID.RenderComponent)
        self.transform = transform

        if img_path is not None:
            self.image: pygame.Surface = pygame.image.load(img_path).convert_alpha()
        else:
            self.image: pygame.Surface = pygame.Surface(size).convert_alpha()
            self.image.fill(color)
        
        self.mask: pygame.Mask = pygame.mask.from_surface(self.image)
        

    def update(self, delta: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.transform.pos)

    @property
    def rect(self) -> pygame.Rect:
        """
        The bounds of the sprite.
        
        Returns:
            pygame.Rect: The bounds.
        """

        rect: pygame.Rect = self.image.get_rect()
        rect.center = (self.transform.pos.x, self.transform.pos.y)
        return rect
    

class CollisionComponent(Component):
    def __init__(self, callback: Callable[['Entity'], 'Entity']):
        Component.__init__(self, ComponentID.CollisionComponent)
        self.callback = callback
        
    def on_collide(self, entity: 'Entity') -> 'Entity':
        return self.callback(entity)

    def update(self, delta: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass
  

class Axis(Enum):
    """
    Represents the Axes.
    """
    
    x = 1
    y = 2
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
