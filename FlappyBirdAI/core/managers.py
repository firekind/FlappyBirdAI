from typing import List
import pygame
from entities import Player, Dummy
from core import Entity, Direction, Axis


class EntityManager:
    """
    Manages all the entities in the game.
    """

    entities: List[Entity] = []
    player: Player

    @staticmethod
    def update_entities(delta: float):
        """
        Updates all the entities in the game.
        
        Args:
            delta (float): time passed since the last update.
        """

        for entity in EntityManager.entities:
            entity.update(delta)

    @staticmethod
    def render_entities(screen: pygame.Surface):
        """
        Renders all the entities in the game.
        
        Args:
            screen (pygame.Surface): The screen to render on.
        """

        screen.fill((0, 0, 0))
        for entity in EntityManager.entities:
            entity.render(screen)

    @staticmethod
    def createPlayer():
        """
        Creates the player.
        """

        EntityManager.player = Player()
        EntityManager.add_entity(EntityManager.player)

    @staticmethod
    def createDummy():
        EntityManager.add_entity(Dummy())

    @staticmethod
    def add_entity(entity: 'Entity') -> None:
        """
        Adds an entity to the game.
        
        Args:
            entity (Entity): The entity to add.
        """

        EntityManager.entities.append(entity)

    @staticmethod
    def remove_entity(entity: 'Entity') -> None:
        """
        removes an entity from the game.
        
        Args:
            entity (Entity): The entity to remove
        """

        EntityManager.entities.remove(entity)


class KeyboardManager:
    """
    Manages keyboard events.
    """

    def __init__(self, player: Player):
        self.player = player

    def down(self, event: 'Event') -> None:
        """
        Manages key down events.
        
        Args:
            event (Event): The keyboard event.
        """

        if event.key == pygame.K_d:
            self.player.move(Direction.left)
        if event.key == pygame.K_a:
            self.player.move(Direction.right)
        if event.key == pygame.K_w:
            self.player.move(Direction.up)
        if event.key == pygame.K_s:
            self.player.move(Direction.down)

    def up(self, event: 'Event') -> None:
        """
        Manages key up events.
        
        Args:
            event (Event): The keyboard event.
        """

        if event.key == pygame.K_d or event.key == pygame.K_a:
            self.player.stop(Axis.horizontal)
        if event.key == pygame.K_w or event.key == pygame.K_s:
            self.player.stop(Axis.vertical)
   