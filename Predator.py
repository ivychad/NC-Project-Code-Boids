from Boid import Boid
from typing import Optional
from enum import Enum
from pygame import Vector2, Surface, draw
from Camera import Camera
import utils
import random


class HuntingState(Enum):
    SCOUT = 0
    PURSUIT = 1
    ATTACK = 2
    REST = 3


class Predator(Boid):
    def __init__(
        self,
        id: int,
        cruise_velocity: float,
        max_velocity: float,
        max_acceleration: float,
        base_acceleration: float,
        max_rotation_angle: float,
        size=(10, 6),
        color=(0, 0, 255),
        position=Vector2(0, 0),
        velocity=Vector2(0, 0),
        acceleration=Vector2(0, 0),
        predation=False,
    ) -> None:
        super().__init__(
            id,
            cruise_velocity,
            max_velocity,
            max_acceleration,
            base_acceleration,
            max_rotation_angle,
            0,
            size,
            color,
            position,
            velocity,
            acceleration,
            predation,
        )

        self.huntingState = HuntingState.SCOUT
        self.selectedPrey: Optional[Boid] = None
        self.target: Optional[Vector2] = None
        self.n_prey_in_confusion_dist = 0
        self.restPeriod = 0

    def setSelectedPrey(self, prey):
        self.selectedPrey = prey

    def getSelectedPrey(self) -> Optional[Boid]:
        return self.selectedPrey

    def setNumPreyInConfusionDist(self, n_prey):
        self.n_prey_in_confusion_dist = n_prey

    def getNumPreyInConfusionDist(self) -> int:
        return self.n_prey_in_confusion_dist

    def setTarget(self, target: Vector2):
        self.target = target

    def getTarget(self) -> Vector2:
        return self.target

    def setRestPeriod(self, restPeriod: float):
        self.restPeriod = restPeriod

    def getRestPeriod(self) -> float:
        return self.restPeriod

    def decreaseRestPeriod(self, amount):
        self.restPeriod -= amount

    def attack_prey(self, prey: list[Boid]) -> list[int]:
        n = self.getNumPreyInConfusionDist()
        collision_indices = self.collide_with_others(prey)

        out = [
            idx
            for idx in collision_indices
            if random.random() <= utils.probability_distribution(n)
        ]

        # Handle hunting state
        if len(out) > 0:
            self.huntingState = HuntingState.REST
            self.setRestPeriod(0)
            self.setTarget(None)
            self.setSelectedPrey(None)
            self.setPredation(False)
        if len(collision_indices) > len(out):
            print("missed prey")

        return out

    def draw(self, camera: Camera, surface: Surface, debug_draw: bool) -> None:
        self._color = (255, 255, 0) if self.huntingState == HuntingState.REST else (255, 0, 0)
        super().draw(camera, surface, debug_draw)


        if self.getSelectedPrey() is not None:
            draw.circle(
                surface,
                (255, 0, 0),
                camera.apply(self.getSelectedPrey().getPosition()),
                10 * 2,
                width=2,
            )
        if self.getTarget() is not None:
            draw.circle(
                surface,
                (255, 0, 0),
                camera.apply(self.getTarget()),
                10 * 2,
                width=2,
            )
