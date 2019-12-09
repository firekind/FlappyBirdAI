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
        self.jump_val = 7
        self.speed = 0

    def down(self, event: 'Event') -> None:
        """
        Manages key down events.
        
        Args:
            event (Event): The keyboard event.
        """

        if event.key == pygame.K_SPACE:
            self.jump()
        if event.key == pygame.K_w:
            self.player.get_component(core.ComponentID.Translation).velocity = Vector2(0, -self.speed)
        if event.key == pygame.K_s:
            self.player.get_component(core.ComponentID.Translation).velocity = Vector2(0, self.speed)
        if event.key == pygame.K_a:
            self.player.get_component(core.ComponentID.Translation).velocity = Vector2(-self.speed, 0)
        if event.key == pygame.K_d:
            self.player.get_component(core.ComponentID.Translation).velocity = Vector2(self.speed, 0)
    

    def up(self, event: 'Event') -> None:
        """
        Manages key up events.
        
        Args:
            event (Event): The keyboard event.
        """

        if event.key == pygame.K_w or event.key == pygame.K_s:
            self.player.get_component(core.ComponentID.Translation).velocity.y = 0
        if event.key == pygame.K_a or event.key == pygame.K_d:
            self.player.get_component(core.ComponentID.Translation).velocity.x = 0    

    def jump(self) -> None:
        physics: core.TranslationComponent = self.player.get_component(core.ComponentID.Translation)
        physics.velocity = Vector2(0, -self.jump_val)
   