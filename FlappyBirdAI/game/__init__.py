import os
import random

import pygame
from pygame import Vector2

import game.core as core
from game.core.managers import EntityManager, KeyboardManager, GUIManager
from game.core.systems import CollisionSystem, Controller
from game.constants import *
from game import paths

class GameState:
    def __init__(self, attach_keyboard=False, res_folder="res/"):
        # initializing pygame
        pygame.init()
        # creating screen
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # creating clock to manage FPS
        self.clock = pygame.time.Clock()
        # creating player
        EntityCreator.init()

        # initializing manager
        EntityManager.init(player=EntityCreator.player)

        # creating keyboard manager to handle keyboard inputs
        self.keyboard_manager = KeyboardManager(player=EntityCreator.player)

        # creating controller to controller the player
        self.controller = Controller(player=EntityCreator.player)

        # score
        self.score = 0

        # initializing keyboard attached flag
        self.keyboard_attached = attach_keyboard

        # setting the score font
        self.score_font = pygame.font.Font(
            os.path.join(res_folder, "fonts", "Flappy-Bird.ttf"), 
            100
        )

        # creating GUI manager
        self.gui = GUIManager(self.screen, self.score_font)
 
    def step(self, actions: List[int] = None):
        """
        Starts the game.
        """
        # intializing reward
        reward = 0.1
        # initialzing is_terminal
        is_terminal = False

        # clearing events or processing them, if the keyboard is attached
        if self.keyboard_attached:
            self.handle_keyboard()
        else:
            pygame.event.pump()
        
        # applying action
        self.controller.update(actions)
        # updating entities
        player_dead, delta_score = EntityManager.update_entities(delta=1)
        # updating collision system
        CollisionSystem.update()
        # updating score
        self.score += delta_score
        if (delta_score != 0):
            reward = 1
        # rendering entities
        EntityManager.render_entities(self.screen)
        # getting the state before the score is rendered on the screen
        state = pygame.surfarray.array3d(pygame.display.get_surface())
        # rendering score
        self.gui.render_score(self.score)
        # updating display
        pygame.display.update()

        # checking if the player is dead
        if player_dead:
            reward = -1
            is_terminal = True
            self.reset()

        # keeps frame rate constant and gets time passed since
        # previous call
        self.clock.tick(FPS)

        return state, reward, is_terminal

    def handle_keyboard(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.keyboard_manager.down(event)
            if event.type == pygame.KEYUP:
                self.keyboard_manager.up(event)
                

    def reset(self) -> None:
        # clearing events
        pygame.event.pump()

        # flushing old entities
        EntityManager.flush()

        # creating new player and initial pipes
        EntityCreator.init()

        # initializing manager
        EntityManager.init(EntityCreator.player)

        # updating the keyboard manager's player
        self.keyboard_manager.reset(EntityCreator.player)

        # updating the controller's player
        self.controller.reset(EntityCreator.player)

        # reseting score
        self.score = 0


class EntityCreator:
    player: core.Entity

    @staticmethod
    def init(num_pipes: int=5) -> None:
        # creating the player
        EntityCreator.createPlayer()

        # creating the pipes
        x = WIDTH
        for _ in range(num_pipes):
            EntityCreator.createPipePair(x=x)
            x += PIPE_HGAP

    @staticmethod
    def createPlayer() -> None:
        """
        Creates the player.
        """

        def on_window_exit(entity: core.Entity, direction: core.Direction, dpos: Vector2) -> None:
            entity.remove = True

        def on_collide(entity: core.Entity, other: core.Entity) -> core.Entity:
            return entity

        def jump(entity: core.Entity) -> None:
            physics: core.TranslationComponent = entity.get_component(core.ComponentID.Translation)
            physics.velocity = Vector2(0, -JUMP_SPEED)

        player = core.Entity(tag="player")
        player.add_component(core.TransformComponent(player, pos=pygame.Vector2(200, 280)))
        player.add_component(core.TranslationComponent(player, accel=Vector2(0, GRAVITY)))
        player.add_component(core.RenderComponent(player, color=(255, 0, 0), size=(64, 64)))
        player.add_component(core.CollisionComponent(player, on_collide))
        player.add_component(core.AreaExitTriggerComponent(player, on_window_exit, pygame.Rect(0, 0, WIDTH, HEIGHT),
                                                           contain=False))
        player.add_component(core.AttachCallbacksComponent(player, {
            'jump': jump
        }))

        EntityCreator.player = player
        EntityManager.add_entity(player)

    @staticmethod
    def createPipePair(x: int = 500) -> None:
        height = 400
        width = 100
        y_1 = random.randint(-350, -50)

        def on_window_exit(entity: core.Entity, direction: core.Direction, dpos: Vector2) -> None:
            if direction != core.Direction.left:
                return

            entity.remove = True
            x = 0
            for i in range(len(EntityManager.entities) - 1, -1, -1):
                if EntityManager.entities[i].tag == "u_pipe":
                    x = EntityManager.entities[i].transform_component.pos.x
                    break

            EntityCreator.createPipePair(x + PIPE_HGAP)

        pipe1 = core.Entity(tag="u_pipe")
        pipe1.add_component(core.TransformComponent(pipe1, pos=Vector2(x, y_1)))
        pipe1.add_component(core.TranslationComponent(pipe1, vel=Vector2(-PIPE_SPEED, 0)))
        pipe1.add_component(core.RenderComponent(pipe1, color=(0, 255, 0), size=(width, height)))
        pipe1.add_component(core.CollisionComponent(pipe1))
        pipe1.add_component(core.AreaExitTriggerComponent(pipe1, on_window_exit, pygame.Rect(0, 0, WIDTH, HEIGHT),
                                                          offset=Vector2(100, 0)))

        EntityManager.add_entity(pipe1)

        pipe2 = core.Entity(tag="d_pipe")
        pipe2.add_component(core.TransformComponent(pipe2, pos=Vector2(x, y_1 + height + PIPE_VGAP)))
        pipe2.add_component(core.TranslationComponent(pipe2, vel=Vector2(-PIPE_SPEED, 0)))
        pipe2.add_component(core.RenderComponent(pipe2, color=(0, 255, 0), size=(width, height)))
        pipe2.add_component(core.CollisionComponent(pipe2))
        pipe2.add_component(core.AreaExitTriggerComponent(pipe2, on_window_exit, pygame.Rect(0, 0, WIDTH, HEIGHT),
                                                          offset=Vector2(100, 0)))


        EntityManager.add_entity(pipe2)
