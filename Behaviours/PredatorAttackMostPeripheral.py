from Behaviours.Behaviour import Behaviour
from Boid import Boid
from Predator import Predator, HuntingState
from pygame import Vector2, Surface, draw
from Camera import Camera
import Constants
from math import radians
from typing import Optional
import Torus


class PredatorAttackMostPeripheral(Behaviour):
    def __init__(
        self,
        perceptionRadius: float = Constants.PREDATOR_PERCEPTION_RADIUS,
        separationDistance: float = Constants.PREDATOR_SEPARATION_DISTANCE,
        angleOfView: float = Constants.PREDATOR_FOV,
        confusionRadius: float = Constants.PREDATOR_CONFUSION_RADIUS,
    ) -> None:
        super().__init__()
        self._perceptionRadius: float = perceptionRadius
        self._separationDistance: float = separationDistance
        self._angleOfView: float = angleOfView
        self._confusionRadius: float = confusionRadius

    def __str__(self) -> str:
        return "PredatorAttackMostPeripheral"
    

    def get_neighbor_prey(self, predator: Predator, prey: list[Boid]):
        neigh_prey: list[Boid] = []
        for p in prey:
            dist_sq = predator.distance_sq_to(p)

            if (
                dist_sq < self._perceptionRadius**2
                and predator.angle_between(p) <= self._angleOfView
            ):
                angle_between_boids = predator.angle_between(p)

                # Boid occlusion
                occluded_neighbors_idx = predator.occludes_neighbors(
                    angle_between_boids, dist_sq, neigh_prey
                )
                if len(occluded_neighbors_idx) > 0:
                    # Boid is in front of the neighbors
                    # Neighbors should be replaced by the boid
                    for i in reversed(occluded_neighbors_idx):
                        del neigh_prey[i]
                    neigh_prey.append(p)
                elif not predator.is_occluded_by_neighbor(
                    angle_between_boids, dist_sq, neigh_prey
                ):
                    # Boid is not occluded by any neighbor
                    neigh_prey.append(p)

        return neigh_prey

    def _bound_position(self, curBoid: Boid):
        direction = Vector2(0, 0)
        if curBoid.getPosition().x <= self._minBounds.x:
            direction.x = 1
        elif curBoid.getPosition().x >= self._maxBounds.x:
            direction.x = -1

        if curBoid.getPosition().y <= self._minBounds.y:
            direction.y = 1
        elif curBoid.getPosition().y >= self._maxBounds.y:
            direction.y = -1

        return direction * 10

    def find_most_peripheral(self, prey: list[Boid]) -> Optional[Boid]:
        if len(prey) == 0:
            return None

        centroid = Vector2()
        for p in prey:
            centroid += p.getPosition()
        centroid /= len(prey)

        return max(
            prey,
            key=lambda p: Torus.ofs(centroid, p.getPosition()).length_squared(),
        )

    def predator_behavior(self, predator: Predator, prey: list[Boid], dt: float):
        prey = self.get_neighbor_prey(predator, prey)
        predator.setNumPreyInConfusionDist(
            sum(
                1
                for _ in filter(
                    lambda p: predator.distance_sq_to(p) <= self._confusionRadius**2,
                    prey,
                )
            )
        )

        match predator.huntingState:
            case HuntingState.SCOUT:
                most_peripheral_prey = self.find_most_peripheral(prey)
                if most_peripheral_prey is None:
                    return

                predator.setSelectedPrey(most_peripheral_prey)
                predator.setDesiredAcceleration(
                    Torus.ofs(
                        predator.getPosition(), predator.getSelectedPrey().getPosition()
                    )
                )

                predator.setPredation(len(prey) > 0)
                if predator.getPredation():
                    predator.huntingState = HuntingState.ATTACK
            case HuntingState.ATTACK:
                targetDir = Torus.ofs(
                    predator.getPosition(), predator.getSelectedPrey().getPosition()
                )
                predator.setDesiredAcceleration(targetDir)

                # NOTE: Switching to REST state is handeled in Predator
            case HuntingState.REST:
                predator.decreaseRestPeriod(dt)
                if predator.getRestPeriod() < 0:
                    predator.huntingState = HuntingState.SCOUT

    def update(self, friendlies: list[Predator], prey: list[Boid], dt: float) -> None:
        for predator in friendlies:
            self.predator_behavior(predator, prey, dt)

    def debug_draw(self, camera: Camera, surface: Surface, boids: list[Boid]):
        for boid in boids:
            _, heading = boid.getVelocity().as_polar()
            heading = radians(heading)

            arcCenter = camera.apply(
                boid.getPosition()
                - Vector2(self._perceptionRadius, self._perceptionRadius)
            )

            draw.arc(
                surface,
                (150, 150, 150),
                (
                    *arcCenter,
                    camera.apply(2 * self._perceptionRadius),
                    camera.apply(2 * self._perceptionRadius),
                ),
                -heading - radians(self._angleOfView),
                -heading + radians(self._angleOfView),
            )
            draw.circle(
                surface,
                (255, 100, 100),
                camera.apply(boid.getPosition()),
                camera.apply(self._separationDistance),
                width=1,
            )
