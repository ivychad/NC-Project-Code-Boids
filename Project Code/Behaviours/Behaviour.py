from abc import ABC, abstractmethod
from Boid import Boid
from pygame import Vector2, Surface
from Constants import *
from Camera import Camera


class Behaviour(ABC):
    def __init__(
        self,
        minBounds: Vector2 = Vector2(-BOUNDARY_WIDTH * 0.95, -BOUNDARY_HEIGHT * 0.95),
        maxBounds: Vector2 = Vector2(BOUNDARY_WIDTH * 0.95, BOUNDARY_HEIGHT * 0.95),
    ) -> None:
        super().__init__()
        self._minBounds: Vector2 = minBounds
        self._maxBounds: Vector2 = maxBounds

    @abstractmethod
    def update(self, friendlies: list[Boid], enemies: list[Boid], dt: float) -> None:
        raise Exception("Missing implementation!")

    @abstractmethod
    def debug_draw(self, camera: Camera, surface: Surface, boids: list[Boid]) -> None:
        raise Exception("Missing implementation!")

    # https://rs.figshare.com/articles/journal_contribution/Supplementary_material_and_Model_description_from_Emergence_of_splits_and_collective_turns_in_pigeon_flocks_under_predation/19188065?backTo=/collections/Supplementary_material_from_Emergence_of_splits_and_collective_turns_in_pigeon_flocks_under_predation_/5847047?backTo=/collections/Supplementary_material_from_Emergence_of_splits_and_collective_turns_in_pigeon_flocks_under_predation_/5847047?backTo=/collections/Supplementary_material_from_Emergence_of_splits_and_collective_turns_in_pigeon_flocks_under_predation_/5847047
    # `dist_to_predator` is in meters [m]
    def manuever_chance(self, dist_to_predator: float) -> float:
        if dist_to_predator < 10:
            return 0.0075
        if dist_to_predator < 20:
            return 0.005
        if dist_to_predator < 30:
            return 0.00375
        if dist_to_predator < 40:
            return 0.0025
        if dist_to_predator < 50:
            return 0.001875

        return 0.00125
