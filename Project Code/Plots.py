import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.cm as cm
from matplotlib.lines import Line2D
from matplotlib.colors import to_rgba

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

    coeff_order = [2, 1, 0, 3, 4, 5]
    colors = ["red", "mediumblue", "purple", "darkcyan", "green"]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    legend_elements = []

    for plot_idx, coeff_idx in enumerate(coeff_order):
        ax = axes[plot_idx]

        for es_idx in range(num_es):
            es_data = all_es_data[es_idx]
            color = colors[es_idx]

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
            ax.scatter(x_vals, y_vals, alpha=0.08, s=100, color=color, zorder=100)

            # Final generation stats
            final_gen = es_data[-1]
            final_coeffs = [ind[0][coeff_idx] for ind in final_gen]
            mean_val = np.mean(final_coeffs)
            std_val = np.std(final_coeffs)

            error_x = num_gens + es_idx * 0.6
            ax.errorbar(
                error_x, mean_val, yerr=std_val, fmt='_', linewidth=2,
                color=color, capsize=5, zorder=100
            )

            best_final_val = best_values[-1][1]
            ax.scatter(error_x, best_final_val, marker='*', s=300, color=color, zorder=101)

            if plot_idx == 0:
                # Add legend entries only once
                legend_elements.append(Line2D(
                    [0], [0], linestyle='None', marker='o', color=color, alpha=0.5,
                    markersize=10, label=f'ES {es_idx+1} – simulation'
                ))
                legend_elements.append(Line2D(
                    [0], [0], linestyle='-', color=color, linewidth=2,
                    label=f'ES {es_idx+1} – mean ± std (last gen.)'
                ))
                legend_elements.append(Line2D(
                    [0], [0], linestyle='None', marker='*', color=color,
                    markersize=15, label=f'ES {es_idx+1} – fittest simulation (last gen.)'
                ))

        ax.set_xlabel("generation", fontsize=18)
        ax.set_ylabel(f"{coefficient_names[coeff_idx].lower()} coefficient", fontsize=18)
        ax.grid(True, axis='y', zorder=-100)
        ax.set_ylim(0, 1)
        ax.set_xlim(-0.5, num_gens + 3)
        ax.tick_params(labelsize=14)

    if legend_elements:
        fig.legend(
            handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, 0.05),
            ncol=num_es, fontsize=14
        )

    plt.tight_layout(rect=[0, 0.08, 1, 0.96])
    fig.subplots_adjust(bottom=0.22)  # make space for large legend
    plt.show()


def lighten_color(color, amount=0.5):
    """
    Lightens the given color by mixing it with white.

    Parameters:
    - color: matplotlib color string or RGB tuple
    - amount: float, 0 (original color) to 1 (white)
    """
    c = np.array(to_rgba(color))
    white = np.array([1, 1, 1, 1])
    return tuple((1 - amount) * c + amount * white)

def plot_fitness_evolution(fitness, legend=True):
    """
    Plot evolution of fitness over generations.

    Parameters:
    - fitness: shape (num_es_runs, num_gen, num_individuals)
    """
    num_es_runs, num_gen, num_individuals = fitness.shape
    base_colors = ["red", "mediumblue", "purple", "darkcyan", "green"]
    
    fig, ax = plt.subplots(figsize=(6, 5))

    for es_run in range(num_es_runs):
        run_fitness = fitness[es_run]
        line_color = base_colors[es_run]
        dot_color = lighten_color(line_color, amount=0.4)  # subtle lightening

        # Scatter all individuals
        for gen in range(num_gen):
            ax.scatter(
                [gen]*num_individuals, run_fitness[gen], 
                color=dot_color, alpha=0.08, s=100, zorder=100,
                label=f'ES {es_run+1} - simulation' if gen == 0 else None
            )

        # Mean per generation
        mean_values = run_fitness.mean(axis=1)
        ax.plot(
            np.arange(num_gen), mean_values,
            color=line_color, linewidth=1.5,
            label=f'ES {es_run+1} - mean', zorder=101
        )

    ax.set_xlabel('generation', fontsize=18)
    ax.set_ylabel('fitness', fontsize=18)
    ax.tick_params(labelsize=14)
    ax.set_ylim(0, 100)
    ax.grid(True, axis='y', zorder=-100)

    if legend:
        ax.legend(
            loc='lower center', bbox_to_anchor=(0.5, -0.45),
            ncol=num_es_runs, fontsize=14
        )

    plt.tight_layout()
    fig.subplots_adjust(bottom=0.25)
    plt.show()

def plot_fitness_scatter(all_fitnesses):
    generations = []
    fitness_values = []
    best_generations = []
    best_fitnesses = []
    median_fitnesses = []
    mean_fitnesses = []

    for gen_idx, gen_fitnesses in enumerate(all_fitnesses):
        generations.extend([gen_idx] * len(gen_fitnesses))
        fitness_values.extend(gen_fitnesses)

        max_fitness = max(gen_fitnesses)
        #median_fitness = np.median(gen_fitnesses)
        mean_fitness = np.mean(gen_fitnesses)

        best_generations.append(gen_idx)
        best_fitnesses.append(max_fitness)
        #median_fitnesses.append(median_fitness)
        mean_fitnesses.append(mean_fitness)


    generations = np.array(generations)
    fitness_values = np.array(fitness_values)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(generations, fitness_values, alpha=0.08, s=100, label='simulation', color='C1', zorder=100)
    #ax.plot(best_generations, median_fitnesses, color='k', linestyle='--', linewidth=3, label='median simulation')
    ax.plot(best_generations, mean_fitnesses, color='C1', linestyle='-', linewidth=1.5, label='simulation – mean', zorder=100)
    ax.set_xlabel('generation', fontsize=18)
    ax.set_ylabel('fitness', fontsize=18)
    ax.set_ylim(20,60)
    ax.set_yticks(np.arange(20, 61, 10))
    ax.set_xlim(-1,21)
    ax.set_xticks(np.arange(0, 21, 5))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=14)
    ax.tick_params(axis='both', labelsize=14)
    ax.grid(True, axis='y')

    plt.tight_layout()
    plt.show()

def plot_coefficients(all_generations_data, coefficient_names=None):
    coeff_order = [2, 1, 0, 4, 3, 5]
    num_coeffs = len(all_generations_data[0][0][0])  # Assuming genes are 1D arrays

    if coefficient_names is None:
        coefficient_names = [f"Coeff {i}" for i in range(num_coeffs)]

    fig, axes = plt.subplots(6, 1, figsize=(5, 20), sharex=True)
    axes = axes.flatten()

    for plot_idx, coeff_idx in enumerate(coeff_order):
        ax = axes[plot_idx]

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

        ax.scatter(x_vals, y_vals, alpha=0.08, c='k', s=100, label='simulation', zorder=100)
        ax.plot(best_x, best_y, color='C1', linestyle='--', linewidth=1.5, zorder=100)  # No label here

        # Orange star for final generation
        final_gen_idx, final_best_val = best_x[-1], best_y[-1]
        ax.plot(final_gen_idx, final_best_val, marker='*', linestyle='--', markersize=18, linewidth=1.5, color='C1', label='fittest simulation', zorder=101)

        ax.set_xticks(np.arange(0, 21, 5))
        ax.set_ylabel(f'{coefficient_names[coeff_idx].lower()} coefficient', fontsize=18)
        ax.tick_params(axis='both', labelsize=14)
        ax.grid(True, axis='y')
        ax.set_ylim(0, 1)

        if plot_idx == 5:
            ax.set_xlabel('generation', fontsize=18)
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=14)

    plt.tight_layout()
    plt.show()
