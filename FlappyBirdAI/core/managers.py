from typing import List
import pygame
from pygame import Vector2
import core


class EntityManager:
    """
    Manages all the entities in the game.
    """

    entities: List[core.Entity] = []

    @staticmethod
    def update_entities(delta: float):
        """
        Updates all the entities in the game.
        
        Args:
            delta (float): time passed since the last update.
        """

        for entity in EntityManager.entities:
            for component in entity.components.values():
                component.update(delta)

    @staticmethod
    def render_entities(screen: pygame.Surface):
        """
        Renders all the entities in the game.
        
        Args:
            screen (pygame.Surface): The screen to render on.
        """

        screen.fill((0, 0, 0))
        for entity in EntityManager.entities:
            for component in entity.components.values():
                component.render(screen)

    
    @staticmethod
    def add_entity(entity: core.Entity) -> None:
        """
        Adds an entity to the game.
        
        Args:
            entity (core.Entity): The entity to add.
        """

        EntityManager.entities.append(entity)

    @staticmethod
    def remove_entity(entity: core.Entity) -> None:
        """
        removes an entity from the game.
        
        Args:
            entity (core.Entity): The entity to remove
        """

        EntityManager.entities.remove(entity)


class KeyboardManager:
    """
    Manages keyboard events.
    """

    def __init__(self, player: core.Entity):
        self.player = player
        self.val = 50

    def down(self, event: 'Event') -> None:
        """
        Manages key down events.
        
        Args:
            event (Event): The keyboard event.
        """

        if event.key == pygame.K_SPACE:
            self.jump(Vector2(0, -self.val))

    def up(self, event: 'Event') -> None:
        """
        Manages key up events.
        
        Args:
            event (Event): The keyboard event.
        """

        

    def jump(self, value: Vector2) -> None:
        gravity: core.GravityComponent = self.player.get_component(core.ComponentID.Gravity)
        gravity.velocity = value
   