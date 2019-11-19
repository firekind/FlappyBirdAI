from typing import Tuple, Callable
from abc import ABC, abstractmethod
import pygame

from core import Direction, Entity

class Component(ABC):
    @abstractmethod
    def update(self, delta: float) -> None:
        raise NotImplementedError

    def render(self, screen: pygame.Surface) -> None:
        raise NotImplementedError


class TransformComponent(Component):
    def __init__(self, pos: pygame.Vector2 = pygame.Vector2(0, 0), 
                 rot: pygame.Vector2 = pygame.Vector2(0, 0),
                 scale: pygame.Vector2 = pygame.Vector2(1, 1),
                 speed: float = 0.5):
        self.pos: pygame.Vector2 = pos
        self.rot: pygame.Vector2 = rot
        self.scale: pygame.Vector2 = scale
        self.speed: float = speed
        self.dx: float = 0
        self.dy: float = 0

    def translate(self, dx: float, dy: float) -> None:
        self.dx = dx
        self.dy = dy

    def move(self, direction: Direction) -> None:
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

    def stop(self, direction: Direction) -> None:
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
    def __init__(self, callback: Callable[[], Entity]):
        self.callback = callback
        
    def on_collide(self) -> Entity:
        return self.callback()

    def update(self, delta: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass
