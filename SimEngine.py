from Boid import Boid
from Predator import Predator
from Behaviours.Behaviour import Behaviour
from Camera import Camera
from pygame import Surface, draw, Vector2, Rect, font
from Constants import WIDTH, HEIGHT, DT, BOUNDARY_HEIGHT, BOUNDARY_WIDTH
from Statistics import Statistics


class SimEngine:
    def __init__(
        self,
        preyBehaviour: Behaviour,
        predatorBehaviour: Behaviour,
        toroidalCoords: bool = False,
    ) -> None:
        self._preyBehaviour: Behaviour = preyBehaviour
        self._predatorBehaviour: Behaviour = predatorBehaviour
        self._prey: list[Boid] = []
        self._predators: list[Predator] = []
        self.toroidalCoords: bool = toroidalCoords
        self._telemetry: Statistics = Statistics()
        self._step: int = 0
        self._time: int = 0

    def addPrey(self, object: Boid) -> None:
        self._prey.append(object)

    def addPredator(self, predator: Predator) -> None:
        self._predators.append(predator)

    def reset(self) -> None:
        self._step = 0
        self.clearPrey()
        self.clearPredators()
        self._telemetry.reset()

    def getCaughtPrey(self, upToStep: int) -> int:
        return sum(self._telemetry.caughtPrey[s] for s in self._telemetry.caughtPrey if s <= upToStep)

    def clearPrey(self) -> None:
        self._prey.clear()

    def clearPredators(self) -> None:
        self._predators.clear()

    def getSteps(self) -> int:
        return self._step

    def getTime(self) -> int:
        return self._time

    def update(self, dt: float):
        remove_prey_indices = set()
        for predator in self._predators:
            remove_prey_indices.update(predator.attack_prey(self._prey))

        for remove_prey_idx in sorted(remove_prey_indices, reverse=True):
            del self._prey[remove_prey_idx]

        self._preyBehaviour.update(self._prey, self._predators, dt)
        self._predatorBehaviour.update(self._predators, self._prey, dt)

        #self._telemetry.update(
         #   self._step, self._prey, self._predators, len(remove_prey_indices), dt
        #)

        for p in self._prey:
            p.update(dt)
            p.rolloverAcc()
            p.is_targeted = False
            if self.toroidalCoords:
                p.rolloverCoords()
        for p in self._predators:
            p.update(dt)
            p.rolloverAcc()
            if self.toroidalCoords:
                p.rolloverCoords()
            
            selected_prey = p.getSelectedPrey()
            if selected_prey is not None:
                selected_prey.is_targeted = True
        
        self._step += 1
        self._time += dt

    def _draw_bounds(self, camera: Camera, surface: Surface):
        if self.toroidalCoords:
            bounds = (camera.apply(Vector2(0, 0)), camera.apply(Vector2(WIDTH, HEIGHT)))
            draw.rect(surface, (255, 255, 255), Rect(bounds[0], bounds[1] - bounds[0]), 1)
        else:
            bounds = (camera.apply(Vector2(-BOUNDARY_WIDTH,-BOUNDARY_HEIGHT)), camera.apply(Vector2(BOUNDARY_WIDTH, BOUNDARY_HEIGHT)))
            draw.rect(surface, (255, 255, 255), Rect(bounds[0], bounds[1] - bounds[0]), 1)


    def draw(self, camera: Camera, surface: Surface, debug_draw: bool):
        self._draw_bounds(camera, surface)
        for p in self._prey:
            p.draw(camera, surface, debug_draw)
        for p in self._predators:
            p.draw(camera, surface, debug_draw)
        if debug_draw:
            self._preyBehaviour.debug_draw(camera, surface, self._prey)
            self._predatorBehaviour.debug_draw(camera, surface, self._predators)

    def plot(self):
        self._telemetry.plotResults(self._step)
