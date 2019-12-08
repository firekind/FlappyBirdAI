import random
from typing import List

import pygame
from pygame import Vector2

import core
from core.managers import EntityManager, KeyboardManager
from core.systems import CollisionSystem

from constants import WIDTH, HEIGHT, FPS
import paths

class Game:
    def __init__(self):
        # initializing pygame
        pygame.init()
        # creating screen
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # creating clock to manage FPS
        self.clock = pygame.time.Clock()
        # defining variable to control game loop
        self.running = True
        # creating player
        EntityCreator.createPlayer()
        EntityCreator.createPipes()
        # creating keyboard manager to handle keyboard inputs
        self.keyboard_manager = KeyboardManager(player=EntityCreator.players[0])
 
    def start(self):
        """
        Starts the game.
        """

        delta = 0
        
        while self.running:
            # managing events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    self.keyboard_manager.down(event)
                if event.type == pygame.KEYUP:
                    self.keyboard_manager.up(event)

            # updating entities
            EntityManager.update_entities(delta)
            # updating collision system
            CollisionSystem.update()
            # rendering entities
            EntityManager.render_entities(self.screen)
            # updating display
            pygame.display.update()

            # keeps frame rate contant and gets time passed since
            # previous call
            delta = self.clock.tick(FPS)
            delta /= 1e2


class EntityCreator:
    players: List[core.Entity] = []

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
        player.add_component(core.GravityComponent(player, 100))
        player.add_component(core.RenderComponent(player, color=(255, 0, 0), size=(64, 64)))
        player.add_component(core.CollisionComponent(player, lambda x: print("Player collide")))
        player.add_component(core.WindowExitTriggerComponent(player, on_window_exit, WIDTH, HEIGHT))

        EntityCreator.players.append(player)
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
    def createPipes() -> None:
        height = 400
        width = 100
        y_1 = random.randint(-350, -50)
        x = 500
        gap = 200

        up_pipe = core.Entity()
        up_pipe.add_component(core.TransformComponent(up_pipe, pos=Vector2(x, y_1)))
        up_pipe.add_component(core.RenderComponent(up_pipe, color=(0, 255, 0), size=(width, height)))
        up_pipe.add_component(core.CollisionComponent(up_pipe))

        EntityManager.add_entity(up_pipe)

        down_pipe = core.Entity()
        down_pipe.add_component(core.TransformComponent(down_pipe, pos=Vector2(x, y_1 + height + gap)))
        down_pipe.add_component(core.RenderComponent(down_pipe, color=(0, 255, 0), size=(width, height)))
        down_pipe.add_component(core.CollisionComponent(down_pipe))

        EntityManager.add_entity(down_pipe)


if __name__ == "__main__":
    Game().start()
