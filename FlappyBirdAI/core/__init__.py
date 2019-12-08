from typing import List, Tuple, Callable, Dict, Union
from abc import ABC, abstractmethod
from enum import Enum
import pygame
from pygame import Vector2

class Entity:
    """
    Represents an entity in the game.
    """
    def __init__(self):
        self.components: Dict['ComponentID', 'Component'] = {}

    def add_component(self, component: 'Component') -> None:
        self.components.update({component.id: component})

    def remove_component(self, component_id: 'ComponentID') -> None:
        try:
            del self.components[component_id]
        except KeyError:
            pass

    def get_component(self, component_id: 'ComponentID') -> 'Component':
        return self.components.get(component_id)
        
    @property
    def transform_component(self):
        return self.components.get(ComponentID.Transform)

    @property
    def render_component(self):
        return self.components.get(ComponentID.Render)

    @property
    def collision_component(self):
        return self.components.get(ComponentID.Collision)

    @property
    def is_collidable(self):
        return bool(self.collision_component)

class EntityGroup:
    def __init__(self):
        self.entities = {}

    def add_entity(self, tag: str, entity: Entity) -> None:
        self.entities[tag] = entity

    def remove_entity(self, tag: str) -> None:
        try:
            del self.entities[tag]
        except KeyError:
            pass

    def get_entity(self, tag: str) -> Union[Entity, None]:
        return self.entities.get(tag)


class Component(ABC):
    def __init__(self, ID: 'ComponentID', parent: Entity):
        self.parent = parent
        self.id: 'ComponentID' = ID

    @abstractmethod
    def update(self, delta: float) -> None:
        raise NotImplementedError

    def render(self, screen: pygame.Surface) -> None:
        raise NotImplementedError


class ComponentID(Enum):
    Transform = 1
    Render = 2
    Collision = 3
    Gravity = 4
    WindowExitTrigger = 5

class TransformComponent(Component):
    def __init__(self, parent: Entity, pos: Vector2 = Vector2(0, 0), 
                 rot: Vector2 = Vector2(0, 0),
                 scale: Vector2 = Vector2(1, 1),
                 speed: float = 5):
        Component.__init__(self, ComponentID.Transform, parent)
        self.pos: Vector2 = pos
        self.rot: Vector2 = rot
        self.scale: Vector2 = scale
    
    def update(self, delta: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass


class GravityComponent(Component):
    def __init__(self, parent: Entity, mass: float):
        Component.__init__(self, ComponentID.Gravity, parent)
        self.transform = parent.transform_component
        self.velocity = Vector2(0, 0)
        self.gravity = 15

    def update(self, delta: float) -> None:
        self.transform.pos += self.velocity * delta
        self.velocity.y += self.gravity * delta

    def render(self, screen: pygame.Surface) -> None:
        pass


class RenderComponent(Component, pygame.sprite.Sprite):
    def __init__(self, parent: Entity, img_path: str = None, 
                 color: Tuple[int, int, int] = None,
                 size: Tuple[float, float] = None):
        
        Component.__init__(self, ComponentID.Render, parent)
        self.transform = parent.transform_component

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
    def __init__(self, parent: Entity, callback: Callable[[Entity], Entity] = None):
        Component.__init__(self, ComponentID.Collision, parent)
        self.callback = callback
        
    def on_collide(self, entity: Entity) -> Entity:
        if self.callback is not None:
            return self.callback(entity)
        return None

    def update(self, delta: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass
  


class WindowExitTriggerComponent(Component):
    def __init__(self, parent: Entity, callback: Callable[[Entity, 'Direction', Vector2], None], 
                 window_width: int, window_height: int):
        Component.__init__(self, ComponentID.WindowExitTrigger, parent)
        self.parent = parent
        self.transform = parent.transform_component
        self.callback = callback
        self.width = window_width - parent.render_component.rect.width
        self.height = window_height - parent.render_component.rect.height

    def update(self, delta: float) -> None:
        if self.callback is None:
            return 

        if self.transform.pos.x < 0:
            self.callback(self.parent, Direction.left, Vector2(-self.transform.pos.x, 0))
        elif self.transform.pos.x > self.width:
            self.callback(self.parent, Direction.right, Vector2(self.width - self.transform.pos.x, 0))

        if self.transform.pos.y < 0:
            self.callback(self.parent, Direction.up, Vector2(0, -self.transform.pos.y))
        elif self.transform.pos.y > self.height:
            self.callback(self.parent, Direction.down, Vector2(0, self.height - self.transform.pos.y))
            


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
