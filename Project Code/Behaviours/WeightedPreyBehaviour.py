from Behaviours.Behaviour import Behaviour
from Boid import Boid
from pygame import Vector2, Surface, draw
import Constants
from math import radians, copysign, sin
from random import randrange, uniform
import utils
from Constants import *
from Camera import Camera
import time

class WeightedPreyBehaviour(Behaviour):
    def __init__(
        self,
        perceptionRadius: float = Constants.PREY_PERCEPTION_RADIUS,
        separationDistance: float = Constants.PREY_SEPARATION_DISTANCE,
        angleOfView: float = Constants.PREY_FOV,
        separationCoef: float = Constants.PREY_SEPARATION_COEFFICIENT,
        cohesionCoef: float = Constants.PREY_COHESION_COEFFICIENT,
        alignmentCoef: float = Constants.PREY_ALIGNMENT_COEFFICIENT,
        dodgeCoef: float = Constants.PREY_DODGE_COEFFICIENT,
        repelCoef: float = Constants.PREY_REPEL_COEFFICIENT,
        repelDistance: float = Constants.PREY_PREDATOR_REPEL_DISTANCE,
        wiggleCoef: float = Constants.PREY_WIGGLE_COEFFICIENT,

    ) -> None:
        super().__init__()
        self._perceptionRadius: float = perceptionRadius
        self._separationDistance: float = separationDistance
        self._angleOfView: float = angleOfView

        self._separationCoef: float = separationCoef
        self._cohesionCoef: float = cohesionCoef
        self._alignmentCoef: float = alignmentCoef
        self._dodgeCoef: float = dodgeCoef
        self._repelCoef: float = repelCoef
        self._repelDistance : float = repelDistance
        self._wiggleCoef: float = wiggleCoef

    def _get_neighbors(self, curBoid: Boid, boids: list[Boid]) -> list[Boid]:
        neighbors: list[Boid] = []
        for boid in boids:
            if boid is not curBoid:
                dist_sq = curBoid.distance_sq_to(boid)

                if (
                    dist_sq < self._perceptionRadius**2
                    and curBoid.angle_between(boid) <= self._angleOfView
                ):
                    neighbors.append(boid)

        return neighbors

    def align_action(self, curBoid: Boid, neighbors: list[Boid]) -> Vector2:
        direction = Vector2(0, 0)
        for boid in neighbors:
            direction += boid.getVelocity()

        if len(neighbors) > 0:
            direction /= len(neighbors)
        direction -= curBoid.getVelocity()

        return direction

    def cohere_turn_action(self, curBoid: Boid, neighbors: list[Boid]) -> Vector2:
        direction = Vector2(0, 0)
        for boid in neighbors:
            direction += curBoid.dirTo(boid).normalize()

        if len(neighbors) > 0:
            direction /= len(neighbors)
        return direction

    def cohere_speed_action(self, curBoid: Boid, neighbors: list[Boid]) -> float:
        speed = curBoid.getVelocity().magnitude()
        for boid in neighbors:
            speed += boid.getVelocity().magnitude()

        speed /= len(neighbors) + 1
        return speed

    def avoid_friendly_action(self, curBoid: Boid, neighbors: list[Boid]) -> Vector2:
        direction = Vector2(0, 0)
        for boid in neighbors:
            if curBoid.distance_sq_to(boid) < self._separationDistance**2:
                direction -= curBoid.dirTo(boid)

        return direction

  
    def wiggle_action(self, curBoid: Boid, predators: list[Boid], dt: float) -> Vector2:
        # Returns: (wiggle_vector, new_wiggleCooldown, new_zigzagDirection, new_wigglePhase)
        
        velocity = curBoid.getVelocity()
        if velocity.length_squared() == 0:
            return Vector2(0, 0)  # no movement, reset

        predator_nearby = any(
            curBoid.distance_sq_to(predator) < self._perceptionRadius**2
            for predator in predators
        )
        
        wigglePhase = curBoid._wigglePhase
        max_wiggle_angle = curBoid._max_wiggle_angle
        frequency = curBoid._wiggle_frequency

        if predator_nearby:
            wigglePhase += frequency * dt
            # wigglePhase %= 2 * 3.141592653589793
            wiggleAngle = max_wiggle_angle * sin(wigglePhase)
            wiggle_vector = velocity.rotate(wiggleAngle)

        else:
            # No predator: reset state
            wiggle_vector = velocity
            wigglePhase = 0.0

        curBoid._wigglePhase = wigglePhase
        return wiggle_vector




    # https://github.com/marinapapa/a-new-HoPE-model/blob/master/actions/avoid_pred_actions.hpp#L58-L98
    
    # Direction based predator avoidance
    def dodge_enemy_action(self, curBoid: Boid, predators: list[Boid]) -> Vector2:
        direction = Vector2()

        for predator in predators:
            radAwayPred = -utils.radBetween(
                predator.getVelocity(), curBoid.getVelocity()
            )
            weight = copysign(self._dodgeCoef, radAwayPred)

            direction += utils.perpDot(curBoid.getVelocity()) * weight

        return direction
    
    # Position based predator avoidance
    def repel_enemy_action(self, curBoid: Boid, predators: list[Boid]) -> Vector2:
        direction = Vector2(0, 0)
        for predator in predators:
            if curBoid.distance_sq_to(predator) < self._repelDistance**2:
                direction -= curBoid.dirTo(predator) * self._repelCoef

        return direction


    
    def update(self, friendlies: list[Boid], enemies: list[Boid], dt: float) -> None:
        for boid in friendlies:
            neighbors = self._get_neighbors(boid, friendlies)
            predators = self._get_neighbors(boid, enemies)
            boid.setPredation(len(predators) > 0)

            s = self.avoid_friendly_action(boid, neighbors) * self._separationCoef
            c = self._cohesionCoef * self.cohere_turn_action(boid, neighbors)
            a = self.align_action(boid, neighbors) * self._alignmentCoef

            # Call wiggle_action and get wiggle vector + new state
            w_vec = self.wiggle_action(boid, predators, dt)
            w = w_vec * self._wiggleCoef

            d = self.dodge_enemy_action(boid, predators)
            r = self.repel_enemy_action(boid, predators)

            boid.setDesiredAcceleration(s + c + a + w + d + r)
            #boid._velocityCheck()


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
