import argparse

parser = argparse.ArgumentParser(description="Predator and Prey boid simulation. Press 'd' to toggle debug mode, 'r' to reset, 'space' to pause/unpause, 'right' to step once, 's' to save a screenshot, 'a' to plot the simulation, and 'p' to toggle predator following.")
parser.add_argument("--n_preys", type=int, help="Number of preys at the beginning of the simulation") # Note, the input type is always string with command line prompts, type here is used to convert it to int once the argument is passed
parser.add_argument("--n_predators", type=int, help="Number of predators at the beginning of the simulation")
parser.add_argument("--separation_coef", type=float, help="Separation coefficient for the prey behaviour")
parser.add_argument("--cohesion_coef", type=float, help="Cohesion coefficient for the prey behaviour")
parser.add_argument("--alignment_coef", type=float, help="Alignment coefficient for the prey behaviour")
parser.add_argument("--dodge_coef", type=float, help="Dodge coefficient for the prey behaviour (predator direction based)")
parser.add_argument("--repel_coef", type=float, help="Repel coefficient for the prey behaviour (predator position based)")
parser.add_argument("--wiggle_coef", type=float, help="Wiggle coefficient for the prey behaviour")
parser.add_argument("--render", type=bool, help="Boolean: show the simulation in a window o not")
parser.add_argument("--predator_strategy", type=str, help="Predator strategy to use. Options: 'nearest', 'centroid', 'random', 'peripheral'")
args = parser.parse_args()

import pygame as pg
import random
import os
import json
import time
from pygame import Vector2

from Constants import *
from SimEngine import SimEngine
from Boid import *
from Predator import Predator
import Camera

# PREYS BEHAVIOURS

from Behaviours.WeightedPreyBehaviour import WeightedPreyBehaviour

# PREDATORS BEHAVIOURS
from Behaviours.PredatorAttackCentroid import PredatorAttackCentroid
from Behaviours.PredatorAttackNearest import PredatorAttackNearest
from Behaviours.PredatorAttackRandom import PredatorAttackRandom
from Behaviours.PredatorAttackMostPeripheral import PredatorAttackMostPeripheral

pg.init()

###################
# Dynamics
###################

if args.predator_strategy == "nearest":
    predator_strategy = PredatorAttackNearest()
elif args.predator_strategy == "centroid":
    predator_strategy = PredatorAttackCentroid()
elif args.predator_strategy == "random":
    predator_strategy = PredatorAttackRandom()
elif args.predator_strategy == "peripheral":
    predator_strategy = PredatorAttackMostPeripheral()
else:
    raise ValueError("Invalid predator strategy. Choose from 'nearest', 'centroid', 'random', or 'peripheral'.")

simEngine: SimEngine = SimEngine(
    WeightedPreyBehaviour(
        separationCoef=args.separation_coef,
        cohesionCoef=args.cohesion_coef,
        alignmentCoef=args.alignment_coef,
        dodgeCoef=args.dodge_coef,
        repelCoef=args.repel_coef,
        wiggleCoef=args.wiggle_coef
    ),
    predator_strategy,
    toroidalCoords=USE_TOROIDAL_COORD
)


def add_predators(n_predators):
    left_margin = 10  # pixels from left edge
    center_y = HEIGHT / 2
    velocity_right = Vector2(1, 0) * PREDATOR_CRUISE_VELOCITY

    for i in range(n_predators):
        # Spread predators vertically a bit around center_y
        y_offset = (i - (n_predators - 1) / 2) * 30  # 30 px spacing vertically
        position = Vector2(left_margin, center_y + y_offset)

        simEngine.addPredator(
            Predator(
                -i - 1,
                size=(40, 24),
                color=(255, 0, 0),
                position=position,
                velocity=velocity_right,
                cruise_velocity=PREDATOR_CRUISE_VELOCITY,
                max_velocity=PREDATOR_MAX_VELOCITY,
                max_acceleration=PREDATOR_MAX_ACCELERATION,
                base_acceleration=PREDATOR_BASE_ACCELERATION,
                max_rotation_angle=PREDATOR_MAX_ROTATION_ANGLE,
            )
        )


def add_prey(n_prey):
    # Place prey on the right side, leave space between predator start and prey start
    right_start_x = WIDTH * 0.15  # start prey at 60% width (to the right)
    right_end_x = WIDTH * 0.95   # end a bit before right edge

    # Vertically, place prey within 40% to 80% of height (some band in vertical middle)
    y_start = HEIGHT * 0.05
    y_end = HEIGHT * 0.95

    # Compute grid size to fit n_prey in this rectangle
    grid_cols = math.ceil(math.sqrt(n_prey * (right_end_x - right_start_x) / (y_end - y_start)))
    grid_rows = math.ceil(n_prey / grid_cols)

    x_spacing = (right_end_x - right_start_x) / (grid_cols + 1)
    y_spacing = (y_end - y_start) / (grid_rows + 1)

    count = 0
    for row in range(grid_rows):
        for col in range(grid_cols):
            if count >= n_prey:
                break

            x = right_start_x + (col + 1) * x_spacing
            y = y_start + (row + 1) * y_spacing

            position = Vector2(x, y)

            # Velocity roughly away from predator start (left edge), so generally towards right or random
            # Here, for simplicity, give them random directions to start
            angle = 90  # +/- 45 degrees around right direction
            direction = Vector2(1, 0) #.rotate_rad(angle)

            velocity = PREY_CRUISE_VELOCITY * direction

            simEngine.addPrey(
                Boid(
                    count,
                    size=(20, 12),
                    color=(255, 255, 255),
                    position=position,
                    velocity=velocity,
                    cruise_velocity=PREY_CRUISE_VELOCITY,
                    max_velocity=PREY_MAX_VELOCITY,
                    max_acceleration=PREY_MAX_ACCELERATION,
                    base_acceleration=PREY_BASE_ACCELERATION,
                    max_rotation_angle=PREY_MAX_ROTATION_ANGLE,
                    escape_reaction_time=PREY_ESCAPE_REACTION_TIME,
                )
            )
            count += 1



# n preyes and predators can be fixed in the Constants.py file or passed as runtime parameters
n_preys = args.n_preys or N_PREY
n_predators = args.n_predators or N_PREDATORS

def add_boids():
    add_prey(n_preys)
    add_predators(n_predators)


add_boids()

running: bool = True
debug_draw: bool = False
is_update_on: bool = True
do_single_update: bool = True
follow_predator: bool = False

camera_zoom = 1.2
camera_view = Vector2(WIDTH * camera_zoom, HEIGHT * camera_zoom)
camera_center = Vector2(WIDTH / 2, HEIGHT / 2)
mouse_drag = False
camera = Camera.Camera(Camera.simple_camera, camera_view.x, camera_view.y)
camera.update(camera_center)


    ###########
    # Paths
    ###########

wd = os.getcwd()

match wd:
    case wd if os.path.basename(wd) == "Simulation":

        parent_folder = os.path.abspath(os.path.join(wd, os.pardir))

        #analysis_path = os.path.join(parent_folder, "analysis")
   # case wd if os.path.basename(wd) == "analysis":
    #    analysis_path = wd
    
  #  case _:
   #     raise Exception("Please run the script from the src or analysis folder, thanks :)")

#if not os.path.exists(analysis_path):
 #   os.mkdir(analysis_path)        
#log_file = os.path.join(analysis_path, "log.csv")
#fig_path = os.path.join(analysis_path, "fig")
#if not os.path.exists(fig_path):
 #   os.mkdir(fig_path)

while running and simEngine.getTime() <= MAX_TIME:
    mouseDelta = pg.mouse.get_rel()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            elif event.key == pg.K_d:
                debug_draw = not debug_draw
            elif event.key == pg.K_r:
                simEngine.reset()
                add_boids()
            elif event.key == pg.K_SPACE:
                is_update_on = not is_update_on
            elif event.key == pg.K_RIGHT:
                do_single_update = True
            #elif event.key == pg.K_s:
             #   pg.image.save(screen, os.path.join(fig_path, f"boids_step_{simEngine.getSteps()-1}.jpg"))
            elif event.key == pg.K_a:
                simEngine.plot()
            elif event.key == pg.K_p:
                follow_predator = not follow_predator
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_drag = True
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            mouse_drag = False
        elif event.type == pg.MOUSEWHEEL:
            camera_zoom -= event.y / 10
            camera_zoom = max(0.1, camera_zoom)

        if mouse_drag:
            camera_center -= Vector2(mouseDelta[0], mouseDelta[1])

    if is_update_on or do_single_update:
        simEngine.update(DT)
        do_single_update = False

    ###########
    # Rendering
    ###########

    if not args.render:
        screen = None
        clock = None
        font = None
        
    else:
        #pg.display.set_caption("Predator and Prey boid simulation")
        screen = pg.display.set_mode([WIDTH, HEIGHT], pg.DOUBLEBUF)
        clock = pg.time.Clock()
        font = pg.font.SysFont("monospace", 22)

        screen.fill((0, 0, 0))

        if follow_predator and len(simEngine._predators) > 0:
            camera.update(simEngine._predators[0].getPosition())
        else:
            camera.scale(camera_zoom)
            camera.update(camera_center)

        simEngine.draw(camera, screen, debug_draw)

        if debug_draw:
            pass
            # screen.blit(
            #     font.render(f"FPS: {int(clock.get_fps())}", 1, (0, 255, 255)), (20, 20)
            # )
            # screen.blit(
            #     font.render(f"steps: {simEngine.getSteps()-1}", 1, (0, 255, 255)), (20, 50)
            # )

        pg.display.flip()

        if clock:
            clock.tick(FPS)

# Write stats in the log file at the end of the simulation in csv format
# with open(log_file, "a") as file:
    #     file.write(f"{simEngine.getSteps()},{len(simEngine._prey)},{len(simEngine._predators)},{simEngine.getTime()}\n")
        
print(simEngine.getSteps(),len(simEngine._prey),len(simEngine._predators),simEngine.getTime())
pg.quit()

#---------------------------------------------------------------------------------------------------



# Initialize pygame clock & timer
# clock = pg.time.Clock()

# if args.render:
#     screen = pg.display.set_mode([WIDTH, HEIGHT], pg.DOUBLEBUF)
#     font = pg.font.SysFont("monospace", 22)
# else:
#     screen = None
#     font = None

# start_time = time.perf_counter()  # high-precision real time
# running = True

# while running:
#     # Calculate elapsed real time
#     current_time = time.perf_counter()
#     elapsed_time = current_time - start_time
    
#     if elapsed_time > MAX_TIME:
#         # Time's up, stop the simulation
#         break

#     # Handle pygame events
#     for event in pg.event.get():
#         if event.type == pg.QUIT:
#             running = False
#         elif event.type == pg.KEYDOWN:
#             if event.key == pg.K_ESCAPE:
#                 running = False
#             elif event.key == pg.K_d:
#                 debug_draw = not debug_draw
#             elif event.key == pg.K_r:
#                 simEngine.reset()
#                 add_boids()
#             elif event.key == pg.K_SPACE:
#                 is_update_on = not is_update_on
#             elif event.key == pg.K_RIGHT:
#                 do_single_update = True
#             #elif event.key == pg.K_s and args.render and screen:
#               #  pg.image.save(screen, os.path.join(fig_path, f"boids_step_{step}.jpg"))
#             elif event.key == pg.K_a:
#                 simEngine.plot()
#             elif event.key == pg.K_p:
#                 follow_predator = not follow_predator
#         elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
#             mouse_drag = True
#         elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
#             mouse_drag = False
#         elif event.type == pg.MOUSEWHEEL:
#             camera_zoom -= event.y / 10
#             camera_zoom = max(0.1, camera_zoom)

#         # Optional mouse dragging camera update
#         if mouse_drag:
#             mouseDelta = pg.mouse.get_rel()
#             camera_center -= Vector2(mouseDelta[0], mouseDelta[1])

#     # Calculate dt since last frame (variable timestep)
#     # You can also fix dt = DT if you want fixed timestep updates
#     dt = clock.tick(FPS) / 1000.0  # seconds elapsed since last frame, limited by FPS cap
#     #dt = 0.02

#     # Update simulation with dt
#     if is_update_on or do_single_update:
#         simEngine.update(dt)
#         do_single_update = False

#     # Render if requested
#     if args.render and screen:
#         screen.fill((0, 0, 0))
#         if follow_predator and len(simEngine._predators) > 0:
#             camera.update(simEngine._predators[0].getPosition())
#         else:
#             camera.scale(camera_zoom)
#             camera.update(camera_center)

#         simEngine.draw(camera, screen, debug_draw)

#         if debug_draw and font:
#             fps_text = font.render(f"FPS: {clock.get_fps():.2f}", True, (0, 255, 255))
#             steps_text = font.render(f"Steps: {simEngine.getSteps()}", True, (0, 255, 255))
#             screen.blit(fps_text, (20, 20))
#             screen.blit(steps_text, (20, 50))

#         pg.display.flip()

#     # Debug prints for FPS and sim time
#     #print(f"Elapsed real time: {elapsed_time:.3f}s, Sim time: {simEngine.getTime():.3f}s, FPS: {clock.get_fps():.2f}, DT: {dt:.3f}s")
#     #print(clock.tick(FPS), "ms per frame")

# print(simEngine.getSteps(), len(simEngine._prey), len(simEngine._predators), simEngine.getTime())


# pg.quit()
