import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from generate_paper_outputs import wave_column_headings

def plot_grouped_bar(backend="combined", output_dir="released_outputs/combined", breakdown="high_level_ethnicity"):
    ''' Plot a chart showing the percent of people of each ethnicity or imd band and by priority group
    who have a decline recorded.
    
    Note the necessary input csv is only available in combined data.
    '''

    df = pd.read_csv(f"released_outputs/{backend}/tables/waves_1_9_declined_{breakdown}.csv", index_col=0)

    df = df.rename(columns=wave_column_headings[""])
    print(df.head())
    labels = df.index
    n_labels = len(labels)
    n_cats = len(df.columns)
    spacing = (n_cats-1)/2

    x = np.arange(n_labels)  # the label locations
    width = 0.1  # the width of the bars
    locs = np.linspace(x-spacing*width, x+spacing*width, n_cats)

    fig, ax = plt.subplots()
    for n, c in enumerate(df.columns):
        y = df[c]
        rects1 = ax.bar(locs[n], y, width, label=c)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('%')
    breakdown_title = breakdown.replace("_"," ").title().replace("Imd","IMD")
    ax.set_title(f'Percent of people in each {breakdown_title}\n who have a decline recorded and are unvaccinated,\nby priority group')
    ax.set_xticks(x)
    labels_new = [l.replace(" ", "\n") for l in labels]
    ax.set_xticklabels(labels_new)
    ax.legend()

    fig.savefig(f"{output_dir}/additional_figures/declines_by_{breakdown}_by_priority_group.png")

