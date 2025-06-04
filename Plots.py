import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.cm as cm

def plot_coefficients(all_generations_data, coefficient_names=None):
    num_coeffs = len(all_generations_data[0][0][0])  # Assuming genes are 1D arrays

    if coefficient_names is None:
        coefficient_names = [f"Coeff {i}" for i in range(num_coeffs)]

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    # Plot the 5 coefficients
    for coeff_idx in range(num_coeffs):
        ax = axes[coeff_idx]

        all_values = []
        best_values = []
        for gen_idx, generation in enumerate(all_generations_data):
            coeffs = [ind[0][coeff_idx] for ind in generation]
            fitnesses = [ind[1] for ind in generation]
            best_idx = np.argmax(fitnesses)
            best_value = generation[best_idx][0][coeff_idx]

            all_values.extend([(gen_idx, val) for val in coeffs])
            best_values.append((gen_idx, best_value))
        
        x_vals, y_vals = zip(*all_values)
        best_x, best_y = zip(*best_values)

        ax.scatter(x_vals, y_vals, alpha=0.5, label='All individuals')
        ax.plot(best_x, best_y, color='red', markersize=12, label='Best individual')
        ax.set_title(f"Evolution of {coefficient_names[coeff_idx]}")
        ax.set_xlabel("Generation")
        ax.set_ylabel(coefficient_names[coeff_idx])
        ax.grid(True)
        ax.legend()
        ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.show()

def plot_fitness(avg_fitnesses, std_fitnesses, highest_fitnesses):
    plt.figure(figsize=(10, 6))
    plt.plot(avg_fitnesses, label='Average Fitness', color='blue')
    plt.fill_between(range(len(avg_fitnesses)), np.array(avg_fitnesses) - np.array(std_fitnesses), 
                        np.array(avg_fitnesses) + np.array(std_fitnesses), color='blue', alpha=0.2, label='Std Dev')
    plt.plot(highest_fitnesses, label='Highest Fitness', color='red')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Genetic Algorithm Fitness Over Generations')
    plt.legend()
    plt.grid()
    plt.show()


def plot_fitness_scatter(all_fitnesses):
    generations = []
    fitness_values = []
    best_generations = []
    best_fitnesses = []
    median_fitnesses = []

    for gen_idx, gen_fitnesses in enumerate(all_fitnesses):
        generations.extend([gen_idx] * len(gen_fitnesses))
        fitness_values.extend(gen_fitnesses)

        max_fitness = max(gen_fitnesses)
        median_fitness = np.median(gen_fitnesses)

        best_generations.append(gen_idx)
        best_fitnesses.append(max_fitness)
        median_fitnesses.append(median_fitness)

    generations = np.array(generations)
    fitness_values = np.array(fitness_values)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(generations, fitness_values, alpha=0.6, label='Fitness', color='blue')
    #plt.scatter(best_generations, best_fitnesses, color='orange', s=60, edgecolors='black', label='Max per Generation')
    plt.plot(best_generations, median_fitnesses, color='red', linestyle='--', linewidth=2, label='Median Fitness')

    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    #plt.title('Fitness Scatter Plot with Max and Median per Generation')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_multiple_ga_runs(all_runs_data, all_avg_fitnesses, all_std_fitnesses, all_highest_fitnesses, coefficient_names=None):
    """
    Plot coefficients and fitness over generations for multiple GA runs in a 6-row, N-column grid.

    Args:
        all_runs_data: list of GA run data, each is a list of generations with (genes, fitness)
        all_avg_fitnesses: list of average fitness arrays (1 per run)
        all_std_fitnesses: list of std fitness arrays (1 per run)
        all_highest_fitnesses: list of highest fitness arrays (1 per run)
        coefficient_names: optional list of coefficient names
    """
    num_runs = len(all_runs_data)
    num_coeffs = len(all_runs_data[0][0][0][0])  # shape: [run][generation][individual][gene]
    num_rows = num_coeffs + 1  # last row for fitness
    num_cols = num_runs

    if coefficient_names is None:
        coefficient_names = [f"Coeff {i}" for i in range(num_coeffs)]

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(4 * num_cols, 3 * num_rows), sharex='col')
    axes = np.array(axes)

    for run_idx in range(num_runs):
        run_data = all_runs_data[run_idx]
        avg_fit = all_avg_fitnesses[run_idx]
        std_fit = all_std_fitnesses[run_idx]
        high_fit = all_highest_fitnesses[run_idx]

        # Plot each coefficient in a row
        for coeff_idx in range(num_coeffs):
            ax = axes[coeff_idx, run_idx]

            all_values = []
            best_values = []

            for gen_idx, generation in enumerate(run_data):
                coeffs = [ind[0][coeff_idx] for ind in generation]
                fitnesses = [ind[1] for ind in generation]
                best_idx = np.argmax(fitnesses)
                best_value = generation[best_idx][0][coeff_idx]

                all_values.extend([(gen_idx, val) for val in coeffs])
                best_values.append((gen_idx, best_value))

            x_vals, y_vals = zip(*all_values)
            best_x, best_y = zip(*best_values)

            ax.scatter(x_vals, y_vals, alpha=0.5, label='All individuals')
            ax.plot(best_x, best_y, color='red', markersize=12, label='Best individual')

            if run_idx == 0:
                ax.set_ylabel(coefficient_names[coeff_idx])
            if coeff_idx == 0:
                ax.set_title(f"Run {run_idx + 1}")

            ax.grid(True)

        # Plot fitness in the last row
        ax = axes[-1, run_idx]
        generations = range(len(avg_fit))
        ax.plot(generations, avg_fit, label='Average Fitness', color='blue')
        ax.fill_between(generations,
                        np.array(avg_fit) - np.array(std_fit),
                        np.array(avg_fit) + np.array(std_fit),
                        color='blue', alpha=0.2, label='Std Dev')
        ax.plot(generations, high_fit, label='Highest Fitness', color='red')
        if run_idx == 0:
            ax.set_ylabel("Fitness")
        ax.set_xlabel("Generation")
        ax.grid(True)

    # Only add legend to one plot
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=3)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.suptitle("GA Runs: Coefficients and Fitness Over Generations", fontsize=16)
    plt.show()


def plot_coefficients_evolution(all_es_data, coefficient_names=None):
    """
    Plot coefficient evolution for multiple ES runs.

    Parameters:
    - all_es_data: list/array of shape [num_es][num_gen][num_individuals] = (coeffs, fitness)
    - coefficient_names: optional list of coefficient names
    """
    num_es = len(all_es_data)
    num_gens = len(all_es_data[0])
    num_coeffs = len(all_es_data[0][0][0][0])  # Get length of coefficient vector

    if coefficient_names is None:
        coefficient_names = [f"Coeff {i}" for i in range(num_coeffs)]

    #colors = ["red", "blue", "purple", "darkorange", "green"]
    colors = ["darkgrey", "darkgreen" , "darkblue", "purple", "darkred"]
    colors_best = ["black", "forestgreen" , "blue", "darkviolet", "red"]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    for coeff_idx in range(num_coeffs):
        ax = axes[coeff_idx]

        for es_idx in range(num_es):
            es_data = all_es_data[es_idx]
            color = colors[es_idx]
            color_best = colors_best[es_idx]

            all_values = []
            best_values = []

            for gen_idx, generation in enumerate(es_data):
                coeffs = [ind[0][coeff_idx] for ind in generation]
                fitnesses = [ind[1] for ind in generation]
                best_idx = np.argmax(fitnesses)
                best_value = generation[best_idx][0][coeff_idx]

                all_values.extend([(gen_idx, val) for val in coeffs])
                best_values.append((gen_idx, best_value))

            x_vals, y_vals = zip(*all_values)
            best_x, best_y = zip(*best_values)

            ax.scatter(x_vals, y_vals, alpha=0.1, s=50, color=color)
            #ax.plot(best_x, best_y, color=color, label=f'ES {es_idx+1}', linewidth=1.5)
            ax.scatter(30, best_y[-1], color=color_best, s=500, marker='*',  label=f'ES {es_idx+1} Best')

        ax.set_title(f"Evolution of {coefficient_names[coeff_idx]}")
        ax.set_xlabel("Generation")
        ax.set_ylabel(coefficient_names[coeff_idx])
        ax.grid(True)
        #ax.legend()
        ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.show()


def plot_fitness_evolution(fitness):
    """
    Plot evolution of fitness over generations.

    Parameters:
    - fitness: shape (num_es_runs, num_gen, num_individuals)
    - save_path: optional path to save figure
    """
    num_es_runs, num_gen, num_individuals = fitness.shape
    colors = ["darkgrey", "darkgreen" , "darkblue", "purple", "darkred"]
    colors_mean = ["black", "forestgreen" , "blue", "darkviolet", "red"]
    
    plt.figure(figsize=(10, 6))

    for es_run in range(num_es_runs):
        run_fitness = fitness[es_run]  # shape: (num_gen, num_individuals)
        color = colors[es_run]
        color_mean = colors_mean[es_run]

        # Scatter all individuals
        for gen in range(num_gen):
            plt.scatter([gen]*num_individuals, run_fitness[gen], 
                        color=color, s=50, alpha=0.1)

        # Line for best individual per generation
        best_values = run_fitness.mean(axis=1)
        plt.plot(np.arange(num_gen), best_values, color=color_mean, linewidth=1.5, label=f'ES {es_run+1}')

    plt.title('Fitness Evolution')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    plt.show()
