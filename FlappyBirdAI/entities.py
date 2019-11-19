from typing import Optional
import pygame
from core import Entity, Direction, Axis
from constants import WIDTH, HEIGHT


class Player(Entity, pygame.sprite.Sprite):
    def __init__(self, x: int = 370, y: int = 480):
        """
        Represents the player
        
        Args:
            x (int, optional): The x coordinate of the player. Defaults to 370.
            y (int, optional): the y coordinate of the player. Defaults to 480.
        """

        self.image: pygame.Surface = pygame.image.load('res/images/player.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.img_x: int = self.image.get_rect().size[0]
        self.img_y: int = self.image.get_rect().size[1]
        self.x: float = x
        self.dx: float = 0
        self.y: float = y
        self.dy: float = 0
        self.speed: float = 0.1
        
    def update(self, delta: float):
        """
        Updates the player.
        
        Args:
            delta (float): The time passed since the last update.
        """

        # checking if the player is out of screen bounds (x axis)
        # if not, updates the player's position.
        if self.x + self.dx > WIDTH - self.img_x:
            self.x = WIDTH - self.img_x
        elif self.x + self.dx < 0:
            self.x = 0
        else:
            self.x += self.dx * delta

        # checking if the player is out of screen bounds (y axis)
        # if not, updates the player's position.
        if self.y + self.dy > HEIGHT - self.img_y:
            self.y = HEIGHT - self.img_y
        elif self.y + self.dy < 0:
            self.y = 0
        else:
            self.y += self.dy * delta

    def move(self, direction: Direction):
        """
        Stores the direction and the amount the player should
        move.
        
        Args:
            direction (Direction): The direction to move.
        """

        # checking the direction to move and updating the dx and dy
        # values.

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
    
    def stop(self, direction: Axis):
        """
        Stops the player's movement in an axis.
        
        Args:
            direction (Axis): The axis, horizontal, vertical or all.
        """

        # checking the axis to stop and updating the dx and dy values.
        if direction == Axis.horizontal:
            self.dx = 0
        elif direction == Axis.vertical:
            self.dy = 0
        elif direction == Axis.all:
            self.dx = 0
            self.dy = 0
        else:
            pass

    def on_collide(self, entity: Entity) -> Optional[Entity]:
        """
        Action to perform on collision.
        
        Args:
            entity (Entity): The entity the player has collided with.
        
        Returns:
            Optional[Entity]: The entity to destroy.
        """
        print("Player collide")
    
    @property
    def rect(self) -> pygame.Rect:
        """
        The bounds of the player.
        
        Returns:
            pygame.Rect: The bounds.
        """

        rect: pygame.Rect = self.image.get_rect()
        rect.center = (self.x, self.y)
        return rect
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Renders the player on the screen
        
        Args:
            screen (pygame.Surface): The screen to render on.
        """

        screen.blit(self.image, (self.x, self.y))


class Dummy(Entity, pygame.sprite.Sprite):
    def __init__(self, x: int = 400, y: int = 400):
        """
        Represents the player
        
        Args:
            x (int, optional): The x coordinate of the dummy. Defaults to 400.
            y (int, optional): the y coordinate of the dummy. Defaults to 400.
        """

        self.image: pygame.Surface = pygame.Surface((64, 64)).convert_alpha()
        # self.image = pygame.image.load('res/images/player.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.image.fill((255, 0, 0))
        self.x: float = x
        self.y: float = y
        
    def update(self, delta: float):
        pass

    def on_collide(self, entity: Entity) -> Optional[Entity]:
        pass
    
    @property
    def rect(self) -> pygame.Rect:
        """
        The bounds of the dummy.
        
        Returns:
            pygame.Rect: The bounds.
        """

        rect: pygame.Rect = self.image.get_rect()
        rect.center = (self.x, self.y)
        return rect
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Renders the dummmy on the screen
        
        Args:
            screen (pygame.Surface): The screen to render on.
        """

        screen.blit(self.image, (self.x, self.y)) 
