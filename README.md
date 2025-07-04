﻿# Natural Computing Project Group 9 - The good boids and the bad boid

Hanna Hoogen, Luca Pattavina, Augusta van Haren

## Project Description

In this project, we investigated how the predator's hunting strategy impacts the optimal coefficient set for prey in a boid-like 2D simulation. All experiments were performed with 100 prey and 1 predator. We used an evolutionary strategy to find the best coefficients for six behaviors: "alignment", "cohesion", "separation", "dodge", "repel", "wiggle". These behaviors together and their weighting determine the acceleration vector of the prey boids. Overall, we find that (1) flocking is beneficial, (2) attack nearest is the best attack strategy for the predator, (3) attack centroid is the worst attack strategy for the predator, (4) attack peripheral and attack random are similar and elicit similar behaviors in the prey (flocking and slightly turning away from predator), (5) the ES finds the optimal strategies within a few generations, (6) some predator attack strategies (peripheral, random, centroid) are more 'forgiving' of variation in prey coefficients than others (nearest), and (7) the ES exploits the limitations of the simulation (e.g., no predator avoidance for nearest is optimal in this environment).

## Guide
The `Project Code` folder contains the full self-contained code for our project. All main experiments that we report on were performed in the `Experiments.ipynb` and `Sensitivity.ipynb` files. Uncommenting all code and running the `Experiments.ipynb` file generates the results for evolving coefficients using the ES for different predator strategies. Running these experiments takes multiple hours. Hence, we also provide the final files in the `Results` folder, which can be imported to generate the plots. Parts of the sensitivity analysis require setting values by hand in the `Constants.py` file, which specifies all main simulation parameters that were held constant throughout our experiments.

In the `Behaviours` folder are the files containing the specific prey and predator behaviors, while `Boid.py` handles the general boid behaviors. `WeightedPreyBehaviour.py` specifies all six prey behaviors and their combination into an acceleration vector. The `PredatorAttack[].py` files each specify one predator attack strategy.

The `ES.py` file is the heart of our evolutionary strategy used to evolve the coefficients; here all core functions of the ES are defined: mutation, crossover, fitness (running a single simulation, number of surviving prey), running a single simulation, running the ES for a specified predator strategy. It works with the simulation environment set up by Ojo et al. (2023) (Files: `main.py`, `Boid.py`, `Camera.py`, `Constants.py`, `Predator.py`, `SimEngine.py`, `Statistics.py`, `Torus.py`, `utils.py`).

The `Plots.py` file contains our plotting functions.

Below we show our results and videos of example simulations for each predator strategy using the evolved coefficients. The videos and plots are also provided as files. We further provide a video of an example ES run (sped up x16): `es_run_example.mp4`.

## Evolving Prey Coefficients for different Predator strategies

The fitness over generations for each predator strategy over 5 ES runs:

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/fitness_all.png)

The figures below show how the coefficients evolved over generations for each predator strategy and 5 ES runs each. The gifs show an excerpt of a characteristic evolved behavior for each strategy (using the optimal coefficients from one ES run).

### Attack Centroid Strategy

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/centroid_coef.png)

Example simulation using the final evolved coefficients from one ES run:

- Separation: 0.64  
- Cohesion: 0.31  
- Alignment: 0.10  
- Dodge: 0.58  
- Repel: 0.71  
- Wiggle: 0.23  
- Fitness: 88

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/centroid.gif)

### Attack Nearest Strategy

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/nearest_coef.png)

Example simulation using the final evolved coefficients from one ES run:

- Separation: 0.76  
- Cohesion: 0.11  
- Alignment: 0.47  
- Dodge: 0.43  
- Repel: 0.06  
- Wiggle: 0.06  
- Fitness: 62

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/nearest.gif)

### Attack Peripheral Strategy

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/peripheral_coef.png)

Example simulation using the final evolved coefficients from one ES run:

- Separation: 0.63  
- Cohesion: 0.45  
- Alignment: 1.00  
- Dodge: 0.23  
- Repel: 0.29  
- Wiggle: 0.94  
- Fitness: 73

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/peripheral.gif)

### Attack Random Strategy

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/random_coef.png)

Example simulation using the final evolved coefficients from one ES run:

- Separation: 0.30  
- Cohesion: 0.13  
- Alignment: 0.14  
- Dodge: 0.94  
- Repel: 0.00  
- Wiggle: 0.49  
- Fitness: 76

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/random.gif)

## Credit

This code builds upon the simulation code by Ojo et al. (2023), [GitHub Ojo Code](https://github.com/MOj0/Collective-Behavior-GroupB).
