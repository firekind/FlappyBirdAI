import pygame
from core.managers import EntityManager
from core import Entity

class CollisionSystem:
    """
    Checks for collisions within the game.
    """

    @staticmethod
    def update():
        """
        Checks for collisions.
        """

        # getting number of entities in the game.
        num = len(EntityManager.entities)
        to_remove = []

        # for every entity
        for i in range(num):
            entity: Entity = EntityManager.entities[i]
            if not entity.is_collidable:
                continue

            # for every other entity
            for j in range(i+1, num):
                other_entity: Entity = EntityManager.entities[j]
                if not other_entity.is_collidable:
                    continue

                # if there is a collision   
                if pygame.sprite.collide_mask(entity.collision_component, other_entity.collision_component):
                    # handle the collision, add result to array
                    to_remove.append(entity.collision_component.on_collide(other_entity))

        # for every entity marked to be removed
        for entity in to_remove:
            # if entity is not None
            if entity is not None:
                # remove the entity from the game.
                EntityManager.remove_entity(entity)
