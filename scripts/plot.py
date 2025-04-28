from matplotlib import pyplot as plt
from matplotlib.patches import Patch

import plotly.graph_objects as go
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

def plot_results_line_plotly(df, title, day, save=False, save_path="", std=None):

    df = smooth_data(df)  # Smooth the data

    fig = go.Figure()

    for idx, col in enumerate(df.columns):
        color = colors[idx % len(colors)]

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=col,
            line=dict(color=color),
        ))

        if std is not None:
            fig.add_trace(go.Scatter(
                x=np.concatenate([df.index, df.index[::-1]]),
                y=np.concatenate([df[col] - std[col], (df[col] + std[col])[::-1]]),
                fill='toself',
                fillcolor=color,
                opacity=0.2,
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=False,
            ))

    fig.update_layout(
        title=f"{title} - {day}",
        xaxis_title="Time (Hour)",
        yaxis_title="Power-Minus-Noise",
        yaxis=dict(range=[0, 300000]),
        legend_title="Frequency Bins",
        template="plotly_white",
        width=1200,
        height=800,
    )

    # Set x-ticks (every 2 hours)
    fig.update_xaxes(
        tickmode='array',
        tickvals=np.arange(0, 25, 2),
        ticktext=[f"{int(hour)}:00" for hour in np.arange(0, 25, 2)]
    )

    if save:
        fig.write_image(f"{save_path}{title.replace(' ', '_')}_{day}.png")

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


def plot_results_polar_plotly(df, title, day, save=False, save_path=""):
    df = smooth_data(df)  # Smooth the data

    fig = go.Figure()

    for idx, col in enumerate(df.columns):
        r = df[col]
        theta = np.linspace(0, 360, len(r))  # Degrees
        color = colors[idx % len(colors)]

        fig.add_trace(go.Scatterpolar(
            r=r,
            theta=theta,
            mode='lines',
            name=col,
            line=dict(color=color),
        ))

    # Calculate rmax for nice scaling
    r_max = df.max().max()

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-r_max, r_max],  # Set the range of the radial axis
                tickvals=[-r_max, 0, r_max],
            ),
            angularaxis=dict(
                tickmode='array',
                tickvals=np.linspace(0, 330, 12),  # Every 30 degrees
                ticktext=[f"{i}:00" for i in range(0, 24, 2)],  # Label every 2 hours
                direction="clockwise",
            ),
        ),
        title=f"{title} - {day}",
        showlegend=True,
        legend_title="Frequency Bins",
        width=800,
        height=600,
        template="plotly_white",
    )

    if save:
        fig.write_image(f"{save_path}{title.replace(' ', '_')}_{day}.png")

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


def plot_individual_bins_line_plotly(df, title, day, save=False, save_path="", std=None):
    df = smooth_data(df)  # Smooth the data
    figs = []

    for idx, col in enumerate(df.columns):
        color = colors[idx % len(colors)]

        fig = go.Figure()

        # Plot the main line
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=col,
            line=dict(color=color),
        ))

        # Plot the standard deviation area if available
        if std is not None:
            fig.add_trace(go.Scatter(
                x=np.concatenate([df.index, df.index[::-1]]),
                y=np.concatenate([df[col] - std[col], (df[col] + std[col])[::-1]]),
                fill='toself',
                fillcolor=color,
                opacity=0.2,
                line=dict(color='rgba(255,255,255,0)'),  # Invisible border
                hoverinfo="skip",
                showlegend=False,
            ))

        # Configure layout
        fig.update_layout(
            title=f"{col} - {title} - {day}",
            xaxis_title="Time (Hour)",
            yaxis_title="Power-Minus-Noise",
            yaxis=dict(range=[0, 300000]),
            legend_title="Frequency Bin",
            template="plotly_white",
            width=1200,
            height=800,
        )

        # Set x-ticks to every 2 hours
        fig.update_xaxes(
            tickmode='array',
            tickvals=np.arange(0, 25, 2),
            ticktext=[f"{int(hour)}:00" for hour in np.arange(0, 25, 2)]
        )

        # Save figure if requested
        if save:
            fig.write_image(
                f"{save_path}{title.replace(' ', '_')}_individual_bins_{col}_{day}.png"
            )

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


def plot_individual_bins_polar_plotly(df, title, day, save=False, save_path=""):
    df = smooth_data(df)  # Smooth the data
    figs = []


    for idx, col in enumerate(df.columns):
        r = df[col]
        theta = np.linspace(0, 360, len(r))  # Degrees
        color = colors[idx % len(colors)]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=r,
            theta=theta,
            mode='lines',
            name=col,
            line=dict(color=color),
        ))

        r_max = r.max()

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-r_max, r_max],
                    tickvals=[-r_max, 0, r_max],
                ),
                angularaxis=dict(
                    tickmode='array',
                    tickvals=np.linspace(0, 345, 24),  # 24 ticks for 24 hours
                    ticktext=[f"{i}:00" for i in range(24)],
                    direction="clockwise",
                ),
            ),
            title=f"{col} - {title} - {day}",
            showlegend=True,
            legend_title="Frequency Bin",
            width=800,
            height=600,
            template="plotly_white",
        )

        if save:
            fig.write_image(
                f"{save_path}{title.replace(' ', '_')}_individual_bins_{col}_{day}.png"
            )

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

def plot_results_color_plotly(df, title, day, selection=[0, 1, 2], save=False, save_path=""):
    all_frequency_columns = [col for col in df.columns]
    selected_columns = [all_frequency_columns[s] for s in selection]
    df2 = df.copy()

    df2 = df2[selected_columns]

    df2["sum"] = df2.sum(axis=1)
    df2["r"] = df2[selected_columns[0]] / df2["sum"]
    df2["g"] = df2[selected_columns[1]] / df2["sum"]
    df2["b"] = df2[selected_columns[2]] / df2["sum"]

    # Create color strings for Plotly (must be in "rgb(r,g,b)" format 0-255)
    df2["color"] = df2.apply(lambda row: f'rgb({int(row["r"]*255)}, {int(row["g"]*255)}, {int(row["b"]*255)})', axis=1)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=np.arange(len(df2)),
        y=df2["sum"],
        marker_color=df2["color"],
        marker_line_width=0,
        width=1.1,
        hoverinfo='x+y',
        name='Power-Minus-Noise',
        showlegend=False,
    ))

    # Set up x-ticks every hour
    tickvals = np.linspace(0, len(df2)-1, 24).astype(int)
    ticktext = [f"{hour}:00" for hour in range(24)]

    fig.update_layout(
        title=f"{title} - {day}",
        xaxis_title="Time (Hour)",
        yaxis_title="Power-Minus-Noise",
        width=1200,
        height=600,
        xaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext,
        ),
        template="plotly_white",
        showlegend=True,
    )

    # Add a manual color legend (simulate using colored markers)
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='red',line=dict(width=0)),
        marker_line_width=0,
        name=selected_columns[0]
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='green',line=dict(width=0)),
        marker_line_width=0,
        name=selected_columns[1]
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='blue',line=dict(width=0)),
        marker_line_width=0,
        name=selected_columns[2]
    ))

    if save:
        fig.write_image(f"{save_path}{title.replace(' ', '_')}_{day}.png")

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


def plot_results_color_polar_plotly(df, title, day, selection=[0, 1, 2], save=False, save_path=""):
    # Prepare theta in degrees for Plotly
    theta = np.linspace(0, 360, len(df))  # Plotly expects degrees, not radians

    all_frequency_columns = [col for col in df.columns]
    selected_columns = [all_frequency_columns[s] for s in selection]
    df2 = df.copy()
    df2 = df2[selected_columns]

    df2["sum"] = df2.sum(axis=1)
    df2["r"] = df2[selected_columns[0]] / df2["sum"]
    df2["g"] = df2[selected_columns[1]] / df2["sum"]
    df2["b"] = df2[selected_columns[2]] / df2["sum"]

    # Create color strings for Plotly
    df2["color"] = df2.apply(lambda row: f'rgb({int(row["r"]*255)}, {int(row["g"]*255)}, {int(row["b"]*255)})', axis=1)

    fig = go.Figure()

    fig.add_trace(go.Barpolar(
        r=df2["sum"],
        theta=theta,
        width=[360/len(df2)]*len(df2),  # Equal width for each bar (fills full circle)
        marker=dict(
            color=df2["color"],
            line=dict(width=0)  # No white border
        ),
        opacity=1,
        hoverinfo='theta+r',
        showlegend=False
    ))

    r_max = df2["sum"].max()

    fig.update_layout(
        title=f"{title} - {day}",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-r_max, r_max],  # Just like your ax.set_rticks
                tickvals=[-r_max, 0, r_max],
            ),
            angularaxis=dict(
                direction="clockwise",
                tickmode='array',
                tickvals=np.linspace(0, 345, 24),  # 24 ticks, one for each hour
                ticktext=[f"{i}:00" for i in range(24)],
            ),
        ),
        width=800,
        height=800,
        template="plotly_white",
        showlegend=True,
    )

    # Add a manual color legend
    fig.add_trace(go.Scatterpolar(
        r=[None], theta=[None],
        mode='markers',
        marker=dict(size=10, color='red'),
        name=selected_columns[0]
    ))
    fig.add_trace(go.Scatterpolar(
        r=[None], theta=[None],
        mode='markers',
        marker=dict(size=10, color='green'),
        name=selected_columns[1]
    ))
    fig.add_trace(go.Scatterpolar(
        r=[None], theta=[None],
        mode='markers',
        marker=dict(size=10, color='blue'),
        name=selected_columns[2]
    ))

    if save:
        fig.write_image(f"{save_path}{title.replace(' ', '_')}_{day}.png")

    return fig
