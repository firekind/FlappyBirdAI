import pygame
from core.managers import EntityManager, KeyboardManager
from core.systems import CollisionSystem
from constants import WIDTH, HEIGHT, FPS

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
        EntityManager.createPlayer()
        EntityManager.createDummy()
        # creating keyboard manager to handle keyboard inputs
        self.keyboard_manager = KeyboardManager(player=EntityManager.player)
 
    def start(self):
        """
        Starts the game.
        """

        while self.running:
            # keeps frame rate contant and gets time passed since
            # previous call
            delta = self.clock.tick(FPS)

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

if __name__ == "__main__":
    Game().start()
