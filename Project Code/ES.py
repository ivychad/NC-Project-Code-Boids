import subprocess
import os
from joblib import Parallel, delayed
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('font', family='serif', serif='Times New Roman')


# define class of Behaviour parameters
class BehaviourParameters:
    """
    Define the behaviour parameters for the simulation.
    If not specified, the parameters are randomly generated with a uniform random (note, this is useful at the beginning of the simulation, to initialize the simulation).

    Note: those parameters, defining the behaviour of the agents in the simulation, define the fitness of the boids' population
    """
    def __init__(self, separation_coef=None, cohesion_coef=None, alignment_coef=None, dodge_coef=None, repel_coef = None, wiggle_coef=None, predator_strategy=None):
        # self.n_preys = 20
        # self.n_predators = 2
        self.predator_strategy = predator_strategy if predator_strategy is not None else "nearest"
        self.separation_coef = separation_coef if separation_coef is not None else np.random.uniform(0, 1)
        self.cohesion_coef = cohesion_coef if cohesion_coef is not None else np.random.uniform(0, 1)
        self.alignment_coef = alignment_coef if alignment_coef is not None else np.random.uniform(0, 1)
        self.dodge_coef = dodge_coef if dodge_coef is not None else np.random.uniform(0, 1)
        self.repel_coef = repel_coef if repel_coef is not None else np.random.uniform(0, 1)
        self.wiggle_coef = wiggle_coef if wiggle_coef is not None else np.random.uniform(0, 1)
        self.gene = np.array([self.separation_coef, self.cohesion_coef, self.alignment_coef, self.dodge_coef, self.repel_coef, self.wiggle_coef])
        self.gene_plot = np.array([self.separation_coef, self.cohesion_coef, self.alignment_coef, self.dodge_coef, self.repel_coef, self.wiggle_coef])
        self.fitness = 0 #self.compute_fitness()  # Initialize fitness of parameters according to the simulation results

    def crossover(self, other):
        """
        Perform crossover between two BehaviourParameters objects to create two new BehaviourParameters objects.
        This is done by combining the genes of the two parents at a random crossover point, as a uniform crossover.
        """
        # Crossover point
        crossover_point = np.random.randint(1, len(self.gene))
        # Create new genes by combining the genes of the two parents
        child1 = np.concatenate((self.gene[:crossover_point], other.gene[crossover_point:]))
        child2 = np.concatenate((other.gene[:crossover_point], self.gene[crossover_point:]))
        return BehaviourParameters(*child1), BehaviourParameters(*child2)
    
    def mutate(self, mutation_rate=0.1):
        """
        Perform mutation on the genes of the BehaviourParameters object.
        """
        # Mutate each gene with a certain probability
        for i in range(len(self.gene)):
            if np.random.rand() < mutation_rate:
                # Mutate the gene by adding a small random value
                self.gene[i] += np.random.uniform(-0.1,0.1)
                # Ensure the gene value is within bounds [0, 1]
                self.gene[i] = np.clip(self.gene[i], 0, 1)
        # Update the parameters with the mutated genes
        self.separation_coef, self.cohesion_coef, self.alignment_coef, self.dodge_coef, self.repel_coef, self.wiggle_coef = self.gene
        self.gene_plot = np.array([self.separation_coef, self.cohesion_coef, self.alignment_coef, self.dodge_coef, self.repel_coef, self.wiggle_coef])
    


    def compute_fitness(self, render=False):
        """
        Compute the fitness of the BehaviourParameters object based on the simulation results.
        The fitness is defined as the ratio of preys to steps.
        """
        simulation = Simulation(self, render=render) # create a simulation object with the given parameters
        output = simulation.run_single_simulation() # run the simulation with the given parameters

        n_steps, n_preys, _, _ = simulation.parse_simulation_output(output)

        fitness =  n_preys 
        self.fitness = fitness 
        
        return fitness

    def __lt__(self, other):
        """
        Compare two BehaviourParameters = genes objects based on their fitness values.
        """
        return self.fitness < other.fitness
    
    def __str__(self):
        """
        String representation of the BehaviourParameters object.
        """
        return f"separation_coef: {self.separation_coef:.2f}, cohesion_coef: {self.cohesion_coef:.2f}, alignment_coef: {self.alignment_coef:.2f}, dodge_coef: {self.dodge_coef:.2f}, repel_coef: {self.repel_coef:.2f}, wiggle_coef: {self.wiggle_coef:.2f}, fitness: {self.fitness:.2f}"


    
    

class Simulation:
    """
    Simulation class to run the simulation of the boids model with the given parameters.
    The simulation is run in a subprocess, and the parameters are passed to the subprocess via command line arguments.
    """
    def __init__(self, behaviour_parameters:BehaviourParameters, render=False):
        self.behaviour_par = behaviour_parameters
        if render:
            self.render = "True"
        else:
            self.render = "" # Parsed as false by the parser (type=bool) in the main.py file

    def run_single_simulation(self):
        """
        Run a single simulation with the given parameters.
        """
        main_file = "main.py" # files that runs the simulation
        results = subprocess.run(["python", main_file, 
                        # "--n_preys", str(behaviour_par.n_preys),                      # can be fixed in the constants.py file
                        # "--n_predators", str(behaviour_par.n_predators),              # can be fixed in the constants.py file
                        "--separation_coef", str(self.behaviour_par.separation_coef),   # Note: being a command line argument, the value has to be passed as a string
                        "--cohesion_coef", str(self.behaviour_par.cohesion_coef),
                        "--alignment_coef", str(self.behaviour_par.alignment_coef),
                        "--dodge_coef", str(self.behaviour_par.dodge_coef),
                        "--repel_coef", str(self.behaviour_par.repel_coef),
                        "--wiggle_coef", str(self.behaviour_par.wiggle_coef),
                        "--predator_strategy", str(self.behaviour_par.predator_strategy),
                        "--render", self.render],
                        capture_output=True, text=True
                        )
        if results.returncode != 0:
            raise ValueError(f"Simulation subprocess failed: {results.stderr}")

        return results.stdout

    def parse_simulation_output(self, output: str):
        """
        Extract the last line of the output, being the system condition at the end of the simulation
        """
        lines = output.splitlines()
        if not lines:
            raise ValueError("Simulation returned no output!")
        else:
            last_line = lines[-1].strip()
            try:
                n_steps, n_preys, n_predators, time = last_line.split(" ")
            except ValueError:
                raise ValueError(f"Unexpected output format: {last_line}")

        print(f"Simulation finished with {n_preys} preys and {n_predators} predators after {n_steps} steps and {float(time):.2f} seconds.")
        return int(n_steps), int(n_preys), int(n_predators), float(time)
    

class EvolutionaryStrategy:
    """
    Genetic Algorithm class to run the genetic algorithm for optimizing the behaviour parameters.
    The genetic algorithm is run for a certain number of generations, and the best parameters are selected based on their fitness values.
    """
    def __init__(self, population:list= None, population_size: int =10, mutation_rate: float =0.1, max_generations: int =10, render: bool = False, predator_strategy: str = None):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.max_generations = max_generations
        self.predator_strategy = predator_strategy if predator_strategy is not None else "nearest" 
        self.render = render
        
        if not population:
            self.population = [BehaviourParameters(predator_strategy=self.predator_strategy) for _ in range(population_size)]
        else:
            self.population = population

    def compute_population_fitness(self):
        """
        Exploiting the function above and parallel routine, compute the fitness of the whole population of BehaviourParameters objects in parallel
        Note: since subprocesses/multiprocessing do not share memory, i.e. each subprocess has its own memory space with objects copies,
        we need to capture the fitness of each BehaviourParameters object in the population and update it after the fitness computation.
        """
        # Compute fitness of the population in parallel
        fitnesses = Parallel(n_jobs=-1)(delayed(rp.compute_fitness)(render=self.render)
                                        for rp in self.population
            )
        
        # Update the fitness of each BehaviourParameters object in the population
        for rp, fitness in zip(self.population, fitnesses):
            rp.fitness = fitness

    
    def fitness_proportional_parent_selection(self):
        fitnesses = np.array([p.fitness for p in self.population])
        
        # Add a small value to avoid zero probabilities
        probabilities = (fitnesses + 1e-8) / (np.sum(fitnesses) + 1e-8)
        
        # Normalize to ensure they sum to 1
        probabilities /= np.sum(probabilities)  # Ensure it sums to 1

        nonzero_indices = np.nonzero(probabilities)[0]

        if len(nonzero_indices) < 2:
            # fallback if not enough non-zero fitness individuals
            parent1, parent2 = np.random.choice(self.population, size=2, replace=True)
        else:
            parent1, parent2 = np.random.choice(self.population, size=2, p=probabilities, replace=False)

        return parent1, parent2

    def generation(self, parent_selection_method=None):
        """
        Generate 2 childrens of BehaviourParameters objects by performing crossover and mutation.
        Note, we need to parallelize this step to compute the fitness of the children in parallel.
        """
        parent1, parent2 = self.fitness_proportional_parent_selection()
        child1, child2 = parent1.crossover(parent2)
        child1.mutate(self.mutation_rate)
        child2.mutate(self.mutation_rate)

        child1.predator_strategy = parent1.predator_strategy
        child2.predator_strategy = parent2.predator_strategy

        return child1, child2

    def run_ES(self):
        """
        Run the genetic algorithm for a certain number of generations.
        Collect and return coefficient values and fitnesses for each individual across generations.
        """
 
        fitnesses_all = []
        all_generations_data = []  # Will hold a list of (genes, fitness) for each generation

        # Compute initial population fitness
        self.compute_population_fitness()
        #print(f"Initial population: {[str(p) for p in self.population]}")

        # Sort population by fitness in descending order
        self.population.sort()

        # Save initial generation data
        gen_data = [(p.gene_plot, p.fitness) for p in self.population]
        all_generations_data.append(gen_data)

        for generation in range(self.max_generations):
            print(f"Generation {generation + 1}/{self.max_generations}")
            
            # Select top k elite individuals
            elite_size = 2
            elites = self.population[-elite_size:]  # Best individuals

            # Create offspring through crossover and mutation
            offspring = Parallel(n_jobs=-1)(delayed(self.generation)() 
                                            for _ in range((self.population_size - elite_size) // 2))
            flat_offspring = [child for pair in offspring for child in pair]

            # New population: elites + offspring
            self.population = elites + flat_offspring

            # Compute fitness after mutation
            self.compute_population_fitness()
            self.population.sort()

            # Collect fitness statistics
            fitnesses = np.array([p.fitness for p in self.population]) + 1e-8
            fitnesses_all.append(fitnesses)

            # Save generation data
            gen_data = [(p.gene_plot, p.fitness) for p in self.population]
            all_generations_data.append(gen_data)
            print([str(p) for p in self.population])

        # Return data for plotting
        return fitnesses_all, all_generations_data
