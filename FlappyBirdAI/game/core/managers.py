from typing import List, Tuple
import pygame
from pygame import Vector2
import game.core as core
from game.constants import WIDTH, HEIGHT


class EntityManager:
    """
    Manages all the entities in the game.
    """

    entities: List[core.Entity] = []
    player: core.Entity

    @staticmethod
    def init(player: core.Entity) -> None:
        EntityManager.player = player

    @staticmethod
    def update_entities(delta: float) -> Tuple[bool, int]:
        """
        Updates all the entities in the game.
        
        Args:
            delta (float): time passed since the last update.
        """
        player_dead = False
        count = 0

        for entity in EntityManager.entities:
            # checking if entity has to be removed
            if entity.remove:
                # removing entity
                EntityManager.remove_entity(entity)
                # checking if the removed entity was the player
                if entity.tag == "player":
                    # setting flag as true
                    player_dead = True

                continue

            for component in entity.components.values():
                component.update(delta)

            # updating score
            if entity.tag == "u_pipe":
                player_mid = EntityManager.player.x + (EntityManager.player.width / 2)
                pipe_mid = entity.x + (entity.width / 2)
                if pipe_mid < player_mid < pipe_mid + 4:
                    count+=1

        return player_dead, count

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

    @staticmethod
    def flush() -> None:
        EntityManager.entities = []


class KeyboardManager:
    """
    Manages keyboard events.
    """

    def __init__(self, player: core.Entity):
        self.player = player
        self.speed = 0

    def down(self, event: 'Event') -> None:
        """
        Manages key down events.
        
        Args:
            event (Event): The keyboard event.
        """

        if event.key == pygame.K_SPACE:
            self.player.jump(entity=self.player)
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

    def reset(self, player: core.Entity) -> None:
        self.player = player  


class GUIManager:
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        self.screen = screen
        self.font = font
        
    def render_score(self, score: int) -> None:
        text = self.font.render(str(score), False, (255, 255, 255))
        self.screen.blit(text, ((WIDTH / 2) - 20, HEIGHT * 0.1))
