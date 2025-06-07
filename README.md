# Natural Computing Project Group 9 - The good boids and the bad boid

Hanna Hoogen, Luca Pattavina, Augusta van Haren

## Project Description

In this project, we investigated how the predator's hunting strategy impacts the obtimal coefficient set for prey in a boid-like 2D simulation. All experiments were performed with 100 prey and 1 predator. We used an evolutionary strategy to find the best coefficients for six behaviors: "alignment", "cohesion", "seperation", "dodge", "repel", "wiggle". These behaviors together and their weighting determine the acceleration vector of the prey boids. 

## Guide
The `Project Code` Folder contains the full self-contained code for our project. All main experiments that we report on were performed in the `Experiments.ipynb` and `Sensitivity.ipynb` files. Uncommenting all code and running the `Experiments.ipynb` file generates the results for evolving coefficients using the ES for different predator strategies. Running these experiments takes multiple hours. Hence, we also provide the final files in the `Results` folder, which can be imported to generate the plots. Parts of the sensitivity analysis require setting values by hand in the `Constants.py` file, which specifies all main simulation parameters which were held constant throughout our experiments.
In the `Behaviours` folder are the file containing the specific prey and predator behaviors, while `Boid.py` handles the general boid behaviours. `WeightedPreyBehaviour.py` specifies all six prey behaivors and their combination into an acceleration vector. The `PredatorAttack[].py` files each specify one predator attack strategy.
The 






## Evolving Prey Coefficients for different Predator strategies

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/fitness_all.png)

### Attack Centroid Strategy

- Seperation: 0.64
- Cohesion:: 0.31
- Alignment: 0.10
- Dodge: 0.58
- Repel: 0.71
- Wiggle: 0.23
- Fitness: 

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/Centroid.gif)


![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/centroid_coef.png)

### Attack Nearest Strategy

separation_coef: 0.76, cohesion_coef: 0.11, alignment_coef: 0.47, dodge_coef: 0.43, repel_coef: 0.06, wiggle_coef: 0.06, fitness: 62.00

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/Nearest.gif)

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/nearest_coef.png)

### Attack Peripheral Strategy

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/Peripheral.gif)

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/peripheral_coef.png)


### Attack Random Strategy

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/Random.gif)

![](https://github.com/ivychad/NC-Project-Code-Boids/blob/main/random_coef.png)

