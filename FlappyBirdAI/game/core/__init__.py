from typing import List, Tuple, Callable, Dict, Union
from abc import ABC, abstractmethod
from enum import Enum
import pygame
from pygame import Vector2

class Entity:
    """
    Represents an entity in the game.
    """
    def __init__(self, tag=None):
        self.components: Dict['ComponentID', 'Component'] = {}
        self.tag = tag
        self.remove = False

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
    def x(self) -> float:
        return self.transform_component.pos.x

    @property
    def y(self) -> float:
        return self.transform_component.pos.y

    @property
    def width(self) -> float:
        return self.render_component.image.get_rect().width

    @property
    def height(self) -> float:
        return self.render_component.image.get_rect().height
        
    @property
    def transform_component(self) -> 'TransformComponent':
        return self.components.get(ComponentID.Transform)

    @property
    def render_component(self) -> 'RenderComponent':
        return self.components.get(ComponentID.Render)

    @property
    def collision_component(self) -> 'CollisionComponent':
        return self.components.get(ComponentID.Collision)

    @property
    def is_collidable(self):
        return bool(self.collision_component)

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
    Translation = 4
    AreaExitTrigger = 5
    AttachCallbacks = 6


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


class TranslationComponent(Component):
    def __init__(self, parent: Entity, accel: Vector2 = Vector2(0, 0), vel: Vector2 = Vector2(0, 0)):
        Component.__init__(self, ComponentID.Translation, parent)
        self.transform = parent.transform_component
        self.velocity = vel
        self.acceleration = accel

    def update(self, delta: float) -> None:
        self.velocity.x += self.acceleration.x * delta
        self.velocity.y += self.acceleration.y * delta
        self.transform.pos += self.velocity

    def render(self, screen: pygame.Surface) -> None:
        pass


class RenderComponent(Component):
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

    def update(self, delta: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.transform.pos)
    

class CollisionComponent(Component, pygame.sprite.Sprite):
    def __init__(self, parent: Entity, callback: Callable[[Entity], Entity] = None):
        Component.__init__(self, ComponentID.Collision, parent)
        pygame.sprite.Sprite.__init__(self)

        self.transform: TransformComponent = parent.transform_component
        self.image: pygame.Surface = parent.render_component.image
        self.mask: pygame.Mask = pygame.mask.from_surface(self.image)

        self.callback = callback
        
    def on_collide(self, entity: Entity) -> Entity:
        if self.callback is not None:
            return self.callback(self.parent, entity)
        return None

    @property
    def rect(self) -> pygame.Rect:
        """
        The bounds of the sprite.
        
        Returns:
            pygame.Rect: The bounds.
        """

        rect: pygame.Rect = self.image.get_rect()
        rect.x = self.transform.pos.x
        rect.y = self.transform.pos.y
        return rect

    def update(self, delta: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass
  


class AreaExitTriggerComponent(Component):
    def __init__(self, parent: Entity, callback: Callable[[Entity, 'Direction', Vector2], None], 
                 area: pygame.Rect, contain: bool = False, offset: Vector2 = Vector2(0, 0)):
        Component.__init__(self, ComponentID.AreaExitTrigger, parent)
        self.parent = parent
        self.transform = parent.transform_component
        self.callback = callback
        self.area: pygame.Rect = area
        self.contain = contain
        render_component = self.parent.render_component

        # getting the image dimensions, if they exist
        if render_component is not None:
            self.image_dim: Vector2 = Vector2(render_component.image.get_rect().width,
                                              render_component.image.get_rect().height)
        else:
            self.image_dim: Vector2 = Vector2(0, 0)

        if contain:
            self.offset = Vector2(self.image_dim.x / 2 + offset.x, self.image_dim.y / 2 + offset.y)
        else:
            self.offset = Vector2(-self.image_dim.x / 2 - offset.x, -self.image_dim.y / 2 - offset.y)
            

    def update(self, delta: float) -> None:
        if self.callback is None:
            return 

        center_x = self.transform.pos.x + (self.image_dim.x / 2)
        center_y = self.transform.pos.y + (self.image_dim.y / 2)

        if center_x - self.offset.x < self.area.x:
            self.callback(self.parent, Direction.left, Vector2(self.area.x - (center_x - self.offset.x), 0))

        elif center_x + self.offset.x > self.area.x + self.area.width:
            self.callback(self.parent, Direction.right,
                          Vector2((self.area.x + self.area.width) - (center_x + self.offset.x), 0))

        elif center_y - self.offset.y < self.area.y:
            self.callback(self.parent, Direction.up, Vector2(0, self.area.y - (center_y - self.offset.y)))

        elif center_y + self.offset.y > self.area.y + self.area.height:
            self.callback(self.parent, Direction.down,
                          Vector2(0, (self.area.y + self.area.height) - (center_y + self.offset.y)))
    

    def render(self, screen: pygame.Surface) -> None:
        pass


class AttachCallbacksComponent(Component):
    def __init__(self, parent: Entity, callbacks: Dict[str, Callable]):
        super(AttachCallbacksComponent, self).__init__(ComponentID.AttachCallbacks, parent)

        for name, callback in callbacks.items():
            setattr(parent, name, callback)

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
