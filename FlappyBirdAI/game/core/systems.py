from typing import Optional

import pygame

import numpy as np

from game.core import Entity
from game.core.managers import EntityManager


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
                    # handle the collision, getting the entity to be removed
                    res = entity.collision_component.on_collide(other_entity)
                    # removing entity, if not None
                    if res is not None:
                        res.remove = True


class Controller:
    def __init__(self, player: Entity):
        self.player = player

    def update(self, actions: Optional[np.ndarray]) -> None:
        if actions is None:
            return

        if actions[1]:
            self.player.jump(entity=self.player)
        
    def reset(self, player: Entity) -> None:
        self.player = player
