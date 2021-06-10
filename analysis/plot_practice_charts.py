''' Functions to plot histograms, boxplots and heatmaps for vaccine declines recorded per practice,
either for single-backend or combined data'''

import os
from numpy.core.numeric import NaN
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def plot_hist(df=None, dfs= None, output_dir=None): 
    '''
    Plots 2 practice histograms, for (a) number of declined vaccines per 1000 population, and 
    (b) per 1000 vaccinated people

    Supply either df or dfs.

    Inputs:
    df (dataframe): contains a list of practices and their "decline_per_1000", "decline_per_1000_vacc"
    dfs (dict): (supply combined-backend results here),
                dict mapping "decline_per_1000" and "decline_per_1000_vacc" each to a df 
                with a column of the same name and index a series of ranges of values (e.g. "20-30")
    ''' 
    if df is not None: 
        out = df.copy()
            
        bins = {0: [0,5,10,15,20,25,30,35,40,45,50,100,500],
                1: [0,10,20,30,40,50,60,70,80,90,100,200,300,1000]}
        labels = {}

        dfs = {}
        for n, x in enumerate(["decline_per_1000", "decline_per_1000_vacc"]):
            labels[n] = [str(a)+"-<"+str(b) for (a,b) in zip(bins[n][:-1], bins[n][1:])]
            binned = pd.cut(out[x], bins=bins[n], labels=labels[n], retbins=False, include_lowest=True, right=False)
            
            # save with absolute counts (not %) to csv with suppression of low practice counts
            binnedcsv = pd.DataFrame(binned.value_counts()).sort_index().replace([0,1,2,3],np.NaN)
            binnedcsv.to_csv(f'{output_dir}/practice_list_size_{x}.csv')
            
            binned = pd.DataFrame(binned.value_counts(normalize=True)).sort_index()
            dfs[x] = binned

    # plot charts, either using supplied or generated `dfs`
    fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
    
    for n, label in enumerate(dfs): 
        dfp = dfs[label]          
        axs[n].bar(dfp.index, dfp[label])
        axs[n].set_xlabel("Rate per 1000")
        axs[n].yaxis.set_major_formatter(PercentFormatter(1))
        axs[0].set_ylabel("Percent of practices")
        for tick in axs[n].get_xticklabels():
            tick.set_rotation(90)

        title = "COVID Vaccines "+ label.replace("_"," ").replace("decline", "declined\n").replace("vacc","vaccinated").title()+" Patients"
        axs[n].set_title(title)

    fig.savefig(f"{output_dir}/declines_by_practice_hist.png")
  

def plot_boxplot(df=None, backend=None, output_dir=None): 
    '''Boxplot of declines per practice against practice list size. 
    ''' 
    out = df.copy()
    # ensure that at least 1% of people in each practice have been vaccinated
    # (those with a v young population e.g. student/military may have small numbers)
    out = out.loc[out["vacc_per_1000"]>10]

    # convert practice list sizes to bins
    if backend=="expectations":
        bins = [0, 10, 15, 20, 25, 100]
        labels = [str(a)+"-<"+str(b) for (a,b) in zip(bins[:-1], bins[1:])]
    else:
        bins = [0, 1_500, 2_000, 2_500, 3_000, 4_000, 5_000, 6_000, 7_000, 10_000, 100_000]
        labels = [str(round(a/1000,1))+"k-<"+str(round(b/1000,1))+"k" for (a,b) in zip(bins[:-1], bins[1:])]
    out["prac_size"] = pd.cut(out["patient_count"], bins=bins, labels=labels, retbins=False, include_lowest=True, right=False)

    out = out.set_index("prac_size")

    fig, axs = plt.subplots(2, 1, sharex=True, tight_layout=True, figsize=(6,8))
    for n, x in enumerate(["decline_group", "decline_per_1000_vacc"]):
        plotting = out[x]
        plotting_dict = {}
        for l in plotting.index.unique():
            # create a list of values for each practice size group
            if l is not NaN:
                temp = plotting.loc[l].to_list()
                plotting_dict[l] = temp
        axs[n].boxplot(list(plotting_dict.values()))
        if "per_1000_vacc" in x:
            title = "COVID Vaccines Declined per 1000 vaccinated patients\n in priority groups per practice"
            ylabel = "Rate per 1000"
        else:
            title = "COVID Vaccines Declined\n per practice"
            ylabel = "Vaccines Declined"
        axs[n].set_ylabel(ylabel)
        axs[n].set_title(title)
    ticks = axs[n].get_xticks()
    plt.xticks(ticks, list(plotting.index.unique()), rotation=90)
    axs[1].set_xlabel("Practice population size")

    fig.savefig(f"{output_dir}/declines_by_practice_boxplot.png")
            

def plot_heatmap(df=None, dfs=None, backend=None, output_dir=None): 
    if df is not None:
        out = df.copy()
        # ensure that at least 1% of people in each practice have been vaccinated
        # (those with a v young population e.g. student/military may have small numbers)
        out = out.loc[out["vacc_per_1000"]>10]

        # convert practice list sizes to bins
        if backend=="expectations":
            bins = [0, 10, 15, 20, 25, 100]
            labels = [str(a)+"-<"+str(b) for (a,b) in zip(bins[:-1], bins[1:])]
        else:
            bins = [0, 1_500, 2_000, 2_500, 3_000, 4_000, 5_000, 6_000, 7_000, 10_000, 100_000]
            labels = [str(round(a/1000,1))+"k-<"+str(round(b/1000,1))+"k" for (a,b) in zip(bins[:-1], bins[1:])]
        out["prac_size"] = pd.cut(out["patient_count"], bins=bins, labels=labels, retbins=False, include_lowest=True, right=False)

        dfs = {}
        for n, x in enumerate(["decline_group", "decline_per_1000_vacc"]):
            bins = {}
            if backend=="expectations":
                bins[0] = [0, 2, 4, 6, 8, 20]
                bins[1] = [0, 1, 2, 3, 4]
                _, edges = pd.cut(out[x], bins=bins[n], retbins=True)
                edges = [round(x,1) for x in edges]
            else:
                bins[0] = [0, 20, 40, 60, 80, 100, 120, 140, 160, 2000]
                bins[1] = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 1000]
                _, edges = pd.cut(out[x], bins=bins[n], retbins=True)
                edges = [int(x) for x in edges]

            out[f"{x}_binned"] = pd.cut(out[x], bins=bins[n], labels=edges[:-1], retbins=False, include_lowest=True)

            plotting = out.groupby([f"{x}_binned","prac_size"])[["patient_count"]].count().unstack()
            plotting.columns = plotting.columns.droplevel()

            # export csv
            plotting.replace([0,1,2,3],np.NaN).to_csv(f'{output_dir}/practice_list_size_2_{x}.csv')
            dfs[x] = plotting

    fig, axs = plt.subplots(2, 1, tight_layout=True, figsize=(6,8))
    
    for n, label in enumerate(dfs):
        plotting = dfs[label]
        # plot heat map
        im = axs[n].imshow(plotting, cmap='RdPu', interpolation='nearest')

        # Create colorbar
        fig.colorbar(im, ax=axs[n])
        #cbar.ax.set_ylabel("no of practices", ax=axs[n], rotation=-90, va="bottom")

        if "per_1000" in label:
            title = "COVID Vaccines recorded as Declined\n per 1000 vaccinated patients in priority groups\n per practice"
            ylabel = "Rate per 1000"
        else:
            title = "COVID Vaccines recorded as Declined\n per practice"
            ylabel = "Vaccines Declined"

        axs[n].set_ylabel(ylabel)
        axs[n].set_title(title)
        # We want to show all ticks...
        yticks = np.arange(len(plotting.index))
        # (adjust location of yticks to bottom of each category)
        yticks = [k-yticks[1]/2 for k in yticks]
        axs[n].set_xticks(np.arange(len(plotting.columns)))
        axs[n].set_yticks(yticks)
        # ... and label them with the respective list entries
        axs[n].set_xticklabels(plotting.columns, rotation=90)
        axs[n].set_yticklabels(plotting.index)  
        axs[n].invert_yaxis()
        axs[1].set_xlabel("Practice population size")

    fig.savefig(f"{output_dir}/declines_by_practice_heatmap.png")

