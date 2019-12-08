from typing import List
import random
import pygame
from pygame import Vector2
import paths
import core
from constants import WIDTH, HEIGHT


class EntityManager:
    """
    Manages all the entities in the game.
    """

    entities: List[core.Entity] = []
    player: core.Entity

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
    def createPlayer():
        """
        Creates the player.
        """

        def on_window_exit(entity: core.Entity, direction: core.Direction, dpos: Vector2) -> None:
            if direction == core.Direction.up:
                return
            entity.transform_component.pos += dpos

        player = core.Entity()
        player.add_component(core.TransformComponent(player, pos=pygame.Vector2(370, 480)))
        player.add_component(core.PhysicsComponent(player, 100))
        player.add_component(core.RenderComponent(player, color=(255, 0, 0), size=(64, 64)))
        player.add_component(core.CollisionComponent(player, lambda x: print("Player collide")))
        player.add_component(core.WindowExitTriggerComponent(player, on_window_exit, WIDTH, HEIGHT))

        EntityManager.player = player
        EntityManager.add_entity(player)

    @staticmethod
    def createDummy():
        dummy = core.Entity()
        dummy.add_component(core.TransformComponent(dummy, pos=pygame.Vector2(400, 400)))
        # dummy.add_component(core.RenderComponent(player, color=(255, 0, 0), size=(64, 64)))
        dummy.add_component(core.RenderComponent(dummy, img_path=paths.player_img))
        dummy.add_component(core.CollisionComponent(dummy))
        
        EntityManager.add_entity(dummy)

    @staticmethod
    def createBlock() -> core.Entity:
        height = 400
        width = 100
        y_1 = random.randint(-350, -50)
        x = 500
        gap = 200

        block1 = core.Entity()
        block1.add_component(core.TransformComponent(block1, pos=Vector2(x, y_1)))
        block1.add_component(core.RenderComponent(block1, color=(0, 255, 0), size=(width, height)))
        block1.add_component(core.CollisionComponent(block1))

        EntityManager.add_entity(block1)

        block2 = core.Entity()
        block2.add_component(core.TransformComponent(block2, pos=Vector2(x, y_1 + height + gap)))
        block2.add_component(core.RenderComponent(block2, color=(0, 255, 0), size=(width, height)))
        block2.add_component(core.CollisionComponent(block2))

        EntityManager.add_entity(block2)

        return block1

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
        physics: core.PhysicsComponent = self.player.get_component(core.ComponentID.Physics)
        physics.velocity = value
   