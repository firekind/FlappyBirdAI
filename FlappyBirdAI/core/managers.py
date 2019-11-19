from typing import List
import pygame
import paths
from core import Entity, Direction
from core import TransformComponent
from core import RenderComponent
from core import CollisionComponent


class EntityManager:
    """
    Manages all the entities in the game.
    """

    entities: List[Entity] = []
    player: Entity

    @staticmethod
    def update_entities(delta: float):
        """
        Updates all the entities in the game.
        
        Args:
            delta (float): time passed since the last update.
        """

        for entity in EntityManager.entities:
            for component in entity.components:
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
            for component in entity.components:
                component.render(screen)

    @staticmethod
    def createPlayer():
        """
        Creates the player.
        """

        player = Entity()
        tc = TransformComponent(pos=pygame.Vector2(370, 480))
        player.add_component(tc)
        player.add_component(RenderComponent(tc, img_path=paths.player_img))
        player.add_component(CollisionComponent(lambda x: print("Player collide")))
        player.is_collidable = True

        EntityManager.player = player
        EntityManager.add_entity(player)

    @staticmethod
    def createDummy():
        dummy = Entity()
        tc = TransformComponent(pos=pygame.Vector2(400, 400))
        dummy.add_component(tc)
        # dummy.add_component(RenderComponent(tc, color=(255, 0, 0), size=(64, 64)))
        dummy.add_component(RenderComponent(tc, img_path=paths.player_img))
        dummy.is_collidable = True

        EntityManager.add_entity(dummy)

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

    def __init__(self, player: Entity):
        self.player = player

    def down(self, event: 'Event') -> None:
        """
        Manages key down events.
        
        Args:
            event (Event): The keyboard event.
        """

        if event.key == pygame.K_d:
            self.player.transform_component.move(Direction.left)
        if event.key == pygame.K_a:
            self.player.transform_component.move(Direction.right)
        if event.key == pygame.K_w:
            self.player.transform_component.move(Direction.up)
        if event.key == pygame.K_s:
            self.player.transform_component.move(Direction.down)

    def up(self, event: 'Event') -> None:
        """
        Manages key up events.
        
        Args:
            event (Event): The keyboard event.
        """

        if event.key == pygame.K_d or event.key == pygame.K_a:
            self.player.transform_component.stop(Direction.horizontal)
        if event.key == pygame.K_w or event.key == pygame.K_s:
            self.player.transform_component.stop(Direction.vertical)
   