import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from generate_paper_outputs import wave_column_headings

def plot_grouped_bar(backend="combined", output_dir="released_outputs/combined", measure="declined", breakdown="high_level_ethnicity"):
    ''' Plot a chart showing the percent of people of each ethnicity or imd band and by priority group
    who have a decline recorded.
    
    Note the necessary input csv is only available in combined data.
    '''
    if measure == "declined":
        df = pd.read_csv(f"released_outputs/{backend}/tables/waves_1_9_declined_{breakdown}.csv", index_col=0)
        df = df.rename(columns=wave_column_headings[""])
        df = df[[c for c in df.columns if c!="Other"]]
        breakdown_title = breakdown.replace("_"," ").title().replace("Imd","IMD")
        title = f'Percent of people in each {breakdown_title}\n who have a decline recorded and are unvaccinated,\nby priority group'
        ylabel = "% with a decline recorded"
        width = 0.1 # the width of the bars
    
    elif measure == "declined_then_accepted" and breakdown=="high_level_ethnicity":
        df = pd.read_csv(f"released_outputs/{backend}/additional_figures/declined_then_accepted_by_wave.csv", index_col=[0,1])
        df = df[["converted"]].unstack()/10
        df.columns = df.columns.droplevel()
        # reorder ethnicity for consistency
        df = df[["White", "Mixed", "South Asian", "Black", "Other", "Unknown"]]
        # reorder cohorts into priority order using list of cohorts
        groups = list(wave_column_headings[''].values())
        groups = [g for g in groups if g in df.index and g!="Other"]
        df = df.transpose()[groups]

        breakdown_title = breakdown.replace("_"," ").title().replace("Imd","IMD")
        title = f'Percent of people in each {breakdown_title}\n who had a decline recorded and were later vaccinated,\nby priority group'
        ylabel = "% later vaccinated"
        width = 0.09 # the width of the bars

    elif measure == "declined_then_accepted" and breakdown=="weeks_diff":
        df = pd.read_csv(f"released_outputs/{backend}/additional_figures/declined_accepted_weeks_by_wave.csv", index_col=[0])
    
        # reorder cohorts into priority order using list of cohorts
        groups = list(wave_column_headings[''].values())
        groups = [g for g in groups if g in df.index and g!="Other"]
        data_labels = df.copy().loc[groups][["0-<2 weeks_percent", "2-<4 weeks_percent", "1-<2 months_percent", ">=2 months_percent"]].round(0).astype(int)
        df = df.loc[groups][["0-<2 weeks", "2-<4 weeks", "1-<2 months", ">=2 months"]]

        breakdown_title = breakdown.replace("_"," ").title().replace("Imd","IMD")
        title = f'Length of time between a decline being recorded and\n later receiving a vaccination, by priority group'
        ylabel = "number of patients"
        width = 0.2 # the width of the bars

    print(df.head())
    labels = df.index
    n_labels = len(labels)
    n_cats = len(df.columns)
    spacing = (n_cats-1)/2

    x = np.arange(n_labels)  # the label locations
    locs = np.linspace(x-spacing*width, x+spacing*width, n_cats)

    fig, ax = plt.subplots()
    for n, c in enumerate(df.columns):
        y = df[c]
        rects1 = ax.bar(locs[n], y, width, label=c)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x)
    labels_new = [l.replace(" ", "\n") for l in labels]
    ax.set_xticklabels(labels_new)
    legend = ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    # add data labels on bars
    if measure == "declined_then_accepted" and breakdown=="weeks_diff":
        rects = ax.patches
        for rect, label in zip(rects, data_labels.transpose().stack().values):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height + 5, label,
                    ha='center', va='bottom',
                    fontsize=6)

    fig.savefig(f"{output_dir}/additional_figures/{measure}_by_{breakdown}_by_priority_group.png", bbox_extra_artists=(legend,), bbox_inches='tight')



def plot_simple_bar(backend="combined", output_dir="released_outputs/combined", exclude_other_group=True):
        
    df = pd.read_csv(f"released_outputs/{backend}/additional_figures/declined_then_accepted.csv", index_col=0)
    df = df[["converted"]]/10
    
    # reorder cohorts into priority order using list of cohorts
    groups = list(wave_column_headings[''].values())
    if exclude_other_group==True:
        groups.remove("Other")
    groups = [g for g in groups if g in df.index]
    df = df.transpose()[groups].transpose()

    title = f'Percent of people in each priority group\n who had a decline recorded and were later vaccinated'
    
    fig , ax = plt.subplots()
    print(df)
    df.plot(kind='bar', ax=ax)

    ax.set_title(title)
    ax.get_legend().remove()
    ax.set_ylabel('%')

    fig.savefig(f"{output_dir}/additional_figures/declined_then_accepted_by_priority_group.png", bbox_inches='tight')

