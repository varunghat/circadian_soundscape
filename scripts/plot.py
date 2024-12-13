from matplotlib import pyplot as plt
from matplotlib.patches import Patch
import numpy as np

from .process import smooth_data

#  TODO: generalize this
colors = ["blue", "green", "orange", "red", "purple"]
# Define frequency bins
bins = [0, 1500, 5000, 10000, 20000, 60000]
bin_labels = ["0-1500", "1500-5000", "5000-10000", "10k-20000", "20k-60000"]
# Initialize dictionaries to store results
average_results = {label: [] for label in bin_labels}
max_results = {label: [] for label in bin_labels}
median_results = {label: [] for label in bin_labels}
time_columns = []

# Plotting the results
def plot_results_line(df, title, day, save=False, save_path="", std=None):

    df = smooth_data(df)  # Smooth the data
    fig = plt.figure(figsize=(12, 8))
    for col, color in zip(df.columns, colors):
        plt.plot(df.index, df[col], label=col, color=color)
        if std is not None:
            plt.fill_between(
                df.index, df[col] - std[col], df[col] + std[col], color=color, alpha=0.2
            )
    plt.ylim(0, 300000)  # Set y-axis limits
    plt.title(f"{title} - {day}")
    plt.xlabel("Time (Hour)")
    plt.ylabel("Power-Minus-Noise")
    plt.legend(title="Frequency Bins")

    # Set x-ticks to every second hour and label them
    ax = plt.gca()
    ax.set_xticks(np.arange(0, 25, 2))
    ax.set_xticklabels([f"{int(hour)}:00" for hour in np.arange(0, 25, 2)])

    if save:
        plt.savefig(f"{save_path}{title.replace(' ', '_')}_{day}.png")
    # fig.savefig("test_fig.png")
    fig = plt.gcf()
    return fig


# Plotting the results
def plot_results_polar(df, title, day, save=False, save_path=""):
    df = smooth_data(df)  # Smooth the data

    r_max_list = []

    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    fig.set_size_inches(12, 8)

    for col, color in zip(df.columns, colors):
        r = df[col]
        theta = np.linspace(0, 2 * np.pi, len(r))
        ax.plot(theta, r, color=color)

        ax.set_theta_direction(-1)
        # ax.set_rmax(2)
        r_max_list.append(r.max())

        # ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
        ax.grid(True)

    r_max_list = np.array(r_max_list)
    # plt.ylim(0, 300000)  # Set y-axis limits
    plt.title(f"{title} - {day}")
    plt.xlabel("Time (Hour)")
    plt.ylabel("Power-Minus-Noise")
    plt.legend(title="Frequency Bins", labels=df.columns)

    ax.set_rticks([-r_max_list.max(), 0, r_max_list.max()])  # Less radial ticks
    ax.set_xticks(theta[::12], labels=[f"{i}:00" for i in range(0, 24)])

    # Set x-ticks to every second hour and label them
    # ax = plt.gca()
    # ax.set_xticks(np.arange(0, 25, 2))
    # ax.set_xticklabels([f"{int(hour)}:00" for hour in np.arange(0, 25, 2)])

    if save:
        plt.savefig(f"{save_path}{title.replace(' ', '_')}_{day}.png")
    fig = plt.gcf()
    return fig


# Plotting individual bins
def plot_individual_bins_line(df, title, day, save=False, save_path="", std=None):
    df = smooth_data(df)  # Smooth the data
    figs = []
    for col, color in zip(df.columns, colors):
        fig = plt.figure(figsize=(12, 8))
        plt.plot(df.index, df[col], label=col, color=color)
        if std is not None:
            plt.fill_between(
                df.index, df[col] - std[col], df[col] + std[col], color=color, alpha=0.2
            )
        plt.ylim(0, 300000)  # Set y-axis limits
        plt.title(f"{col} - {title} - {day}")
        plt.xlabel("Time (Hour)")
        plt.ylabel("Power-Minus-Noise")
        plt.legend(title="Frequency Bin")
        plt.tight_layout()

        # Set x-ticks to every second hour and label them
        ax = plt.gca()
        ax.set_xticks(np.arange(0, 25, 2))
        ax.set_xticklabels([f"{int(hour)}:00" for hour in np.arange(0, 25, 2)])

        if save:
            plt.savefig(
                f"{save_path}{title.replace(' ', '_')}_individual_bins_{col}_{day}.png"
            )
        fig = plt.gcf()
        figs.append(fig)
    return figs


def plot_individual_bins_polar(df, title, day, save=False, save_path=""):
    df = smooth_data(df)  # Smooth the data
    figs = []
    for col, color in zip(df.columns, colors):
        r = df[col]
        theta = np.linspace(0, 2 * np.pi, len(r))

        # theta = theta - 4.5

        # r = np.array(r)
        # theta = np.array(theta)
        # print(len(r))
        # print(theta)

        fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
        fig.set_size_inches(12, 8)
        ax.plot(theta, r, color=color)
        ax.set_theta_direction(-1)
        # ax.set_rmax(2)
        ax.set_rticks([-r.max(), 0, r.max()])  # Less radial ticks
        ax.set_xticks(theta[::12], labels=[f"{i}:00" for i in range(0, 24)])
        # ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
        ax.grid(True)

        plt.title(f"{col} - {title} - {day}")
        # plt.xlabel("Time (Hour)")
        plt.ylabel("Power-Minus-Noise")
        plt.legend(title="Frequency Bin")
        # plt.tight_layout()

        # Set x-ticks to every second hour and label them
        # ax = plt.gca()
        # ax.set_xticks(np.arange(0, 25, 2))
        # ax.set_xticklabels([f"{int(hour)}:00" for hour in np.arange(0, 25, 2)])

        if save:
            plt.savefig(
                f"{save_path}{title.replace(' ', '_')}_individual_bins_{col}_{day}.png"
            )
        fig = plt.gcf()
        figs.append(fig)
    return figs


def plot_results_color(df, title, day, selection=[0, 1, 2], save=False, save_path=""):
    all_frequency_columns = [col for col in df.columns]
    # print(all_frequency_columns)
    selected_columns = [all_frequency_columns[s] for s in selection]
    df2 = df.copy()

    df2 = df2[selected_columns]

    df2.loc[:, "sum"] = df2.sum(axis=1)
    df2["r"] = df2[selected_columns[0]] / df2["sum"]
    df2["g"] = df2[selected_columns[1]] / df2["sum"]
    df2["b"] = df2[selected_columns[2]] / df2["sum"]

    df2["color"] = df2.apply(lambda row: [row["r"], row["g"], row["b"]], axis=1)

    fig, ax = plt.subplots(1, 1, figsize=(20, 10))

    ax.bar(range(0, len(df2)), df2["sum"], color=df2["color"], width=1.0)

    ax.set_xticks(
        range(0, len(df2), len(df2) // 23),
        labels=[f"{hour}:00" for hour in range(0, 24)],
    )
    # ax.plot(df["time"],df["5000-10000"],color='green')
    # ax.plot(df["time"],df["10k-20000"],color='blue')

    # Add some labels
    ax.set_xlabel("Time (Hour)")
    ax.set_ylabel("Power-Minus-Noise")

    plt.title(f"{title} - {day}")
    plt.legend(title="Frequency Bin")
    plt.tight_layout()

    custom_lines = [
        Patch(facecolor="red", edgecolor="red", label=selected_columns[0]),
        Patch(facecolor="green", edgecolor="green", label=selected_columns[1]),
        Patch(facecolor="blue", edgecolor="blue", label=selected_columns[2]),
    ]

    ax.legend(handles=custom_lines, title="Frequency bins")

    if save:
        plt.savefig(f"{save_path}{title.replace(' ', '_')}_{day}.png")
    fig = plt.gcf()
    return fig


# Plot the results with color coding for each frequency bin in polar coordinates


def plot_results_color_polar(
    df, title, day, selection=[0, 1, 2], save=False, save_path=""
):

    theta = np.linspace(0, 2 * np.pi, len(df))

    # theta = theta - 4.5

    # r = np.array(r)
    # theta = np.array(theta)
    # print(len(r))
    # print(theta)

    all_frequency_columns = [col for col in df.columns]
    # print(all_frequency_columns)
    selected_columns = [all_frequency_columns[s] for s in selection]
    df2 = df.copy()

    df2 = df2[selected_columns]

    df2.loc[:, "sum"] = df2.sum(axis=1)
    df2["r"] = df2[selected_columns[0]] / df2["sum"]
    df2["g"] = df2[selected_columns[1]] / df2["sum"]
    df2["b"] = df2[selected_columns[2]] / df2["sum"]

    df2["color"] = df2.apply(lambda row: [row["r"], row["g"], row["b"]], axis=1)

    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    fig.set_size_inches(12, 8)
    ax.bar(theta, df2["sum"], color=df2["color"], width=0.02)
    ax.set_theta_direction(-1)
    # ax.set_rmax(2)
    ax.set_rticks([-df2["sum"].max(), 0, df2["sum"].max()])  # Less radial ticks
    ax.set_xticks(theta[::12], labels=[f"{i}:00" for i in range(0, 24)])
    # ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
    ax.grid(True)

    plt.title(f"{title} - {day}")
    plt.xlabel("Time (Hour)")
    plt.ylabel("Power-Minus-Noise")
    plt.legend(title="Frequency Bin")
    # plt.tight_layout()

    custom_lines = [
        Patch(facecolor="red", edgecolor="red", label=selected_columns[0]),
        Patch(facecolor="green", edgecolor="green", label=selected_columns[1]),
        Patch(facecolor="blue", edgecolor="blue", label=selected_columns[2]),
    ]

    ax.legend(handles=custom_lines, title="Frequency bins")

    # Set x-ticks to every second hour and label them
    # ax = plt.gca()
    # ax.set_xticks(np.arange(0, 25, 2))

    if save:
        plt.savefig(f"{save_path}{title.replace(' ', '_')}_{day}.png")
    fig = plt.gcf()
    return fig