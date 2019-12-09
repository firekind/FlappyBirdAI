import random
import pygame
from pygame import Vector2
import core
from core.managers import EntityManager, KeyboardManager
from core.systems import CollisionSystem
from constants import WIDTH, HEIGHT, FPS, GRAVITY, PIPE_VGAP, PIPE_HGAP, PIPE_SPEED
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
        
        x = WIDTH
        for _ in range(5):
            EntityCreator.createPipePair(x=x)
            x += PIPE_HGAP

        # creating keyboard manager to handle keyboard inputs
        self.keyboard_manager = KeyboardManager(player=EntityCreator.player)
 
    def start(self):
        """
        Starts the game.
        """

        while self.running:
            # keeps frame rate constant and gets time passed since
            # previous call
            delta = self.clock.tick(FPS)
            delta /= 1e3

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


class EntityCreator:
    player: core.Entity

    @staticmethod
    def createPlayer():
        """
        Creates the player.
        """

        def on_window_exit(entity: core.Entity, direction: core.Direction, dpos: Vector2) -> None:
            EntityManager.remove_entity(entity)

        def on_collide(entity: core.Entity, other: core.Entity) -> core.Entity:
            return entity

        player = core.Entity()
        player.add_component(core.TransformComponent(player, pos=pygame.Vector2(200, 280)))
        player.add_component(core.TranslationComponent(player, accel=Vector2(0, GRAVITY)))
        player.add_component(core.RenderComponent(player, color=(255, 0, 0), size=(64, 64)))
        player.add_component(core.CollisionComponent(player, on_collide))
        player.add_component(core.AreaExitTriggerComponent(player, on_window_exit, pygame.Rect(0, 0, WIDTH, HEIGHT),
                                                           contain=False))

        EntityCreator.player = player
        EntityManager.add_entity(player)

    @staticmethod
    def createDummy():
        dummy = core.Entity()
        dummy.add_component(core.TransformComponent(dummy, pos=pygame.Vector2(200, 400)))
        # dummy.add_component(core.RenderComponent(dummy, color=(0, 255, 0), size=(32, 64)))
        dummy.add_component(core.RenderComponent(dummy, img_path=paths.player_img))
        dummy.add_component(core.CollisionComponent(dummy))
        
        EntityManager.add_entity(dummy)

    @staticmethod
    def createPipePair(x: int = 500) -> core.Entity:
        height = 400
        width = 100
        y_1 = random.randint(-350, -50)

        def on_window_exit(entity: core.Entity, direction: core.Direction, dpos: Vector2) -> None:
            if direction != core.Direction.left:
                return

            EntityManager.remove_entity(entity)
            x = 0
            for i in range(len(EntityManager.entities) - 1, -1, -1):
                if EntityManager.entities[i].tag == "pipe":
                    x = EntityManager.entities[i].transform_component.pos.x
                    break

            EntityCreator.createPipePair(x + PIPE_HGAP)

        pipe1 = core.Entity("pipe")
        pipe1.add_component(core.TransformComponent(pipe1, pos=Vector2(x, y_1)))
        pipe1.add_component(core.TranslationComponent(pipe1, vel=Vector2(-PIPE_SPEED, 0)))
        pipe1.add_component(core.RenderComponent(pipe1, color=(0, 255, 0), size=(width, height)))
        pipe1.add_component(core.CollisionComponent(pipe1))
        pipe1.add_component(core.AreaExitTriggerComponent(pipe1, on_window_exit, pygame.Rect(0, 0, WIDTH, HEIGHT),
                                                          offset=Vector2(100, 0)))

        EntityManager.add_entity(pipe1)

        pipe2 = core.Entity("pipe")
        pipe2.add_component(core.TransformComponent(pipe2, pos=Vector2(x, y_1 + height + PIPE_VGAP)))
        pipe2.add_component(core.TranslationComponent(pipe2, vel=Vector2(-PIPE_SPEED, 0)))
        pipe2.add_component(core.RenderComponent(pipe2, color=(0, 255, 0), size=(width, height)))
        pipe2.add_component(core.CollisionComponent(pipe2))
        pipe2.add_component(core.AreaExitTriggerComponent(pipe2, on_window_exit, pygame.Rect(0, 0, WIDTH, HEIGHT),
                                                          offset=Vector2(100, 0)))


        EntityManager.add_entity(pipe2)


if __name__ == "__main__":
    Game().start()
