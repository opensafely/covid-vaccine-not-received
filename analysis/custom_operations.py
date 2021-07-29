''' This module generates charts from cohort.pickle rather than from the cumulative csvs.
''' 

import os
from numpy.core.numeric import NaN
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from ethnicities import high_level_ethnicities

wave_column_headings = {
    "total": "All",
    "all_priority": "Priority groups",
    "1": "In care home",
    "2": "80+",
    "3": "70-79",
    "4": "CEV",
    "5": "65-69",
    "6": "At risk",
    "7": "60-64",
    "8": "55-59",
    "9": "50-54",
    "0": "Other",
}

group_names = {
    "vacc_group":"Vaccinated", 
    "decline_group":"Declined", 
    "decline_total_group":"Declined - all",
    "other_reason_group":"Other reason",
    "declined_accepted_group": "Declined then received",
    "patient_id":"total"
    }

backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
out_path = f"output/{backend}/additional_figures"
os.makedirs(out_path, exist_ok=True)

def compute_uptake_percent(uptake):#, labels):
    uptake_pc = 100 * uptake / uptake.loc["total"]
    uptake_pc.drop("total", inplace=True)
    uptake_pc.fillna(0, inplace=True)
    if set(uptake_pc.columns) == {"True", "False"}:
        # This ensures that chart series are always same colour.
        uptake_pc = uptake_pc[["True", "False"]]
    else:
        # Sort DataFrame columns so that legend is in the same order as chart series.
        uptake_pc.sort_values(
            uptake_pc.last_valid_index(), axis=1, ascending=False, inplace=True
        )
    #uptake_pc.rename(columns=labels, inplace=True)
    return uptake_pc


def practice_variation(input_path="output/cohort.pickle", output_dir=out_path):
    ''' Calculates total patients per practice and of whom how many have had a vaccine to date, or declined
    Note: those declining only include those who have not later received a vaccine.
    '''
    cohort = pd.read_pickle(input_path)

    # limit to priority groups (ages 50+ and clinical priority groups)
    cohort = cohort.loc[cohort["wave"]!=0]

    practice_figures = cohort[["practice", "vacc_group", "decline_group", "patient_id"]]\
                        .groupby("practice").agg({"vacc_group":"sum", 
                                                  "decline_group":"sum", 
                                                  "patient_id":"nunique"})
    practice_figures = practice_figures.rename(columns={"patient_id":"patient_count"})
    
    # remove tiny practices by setting a minimum no of people in the priority groups
    #  and ensure that at least 10 patients have been vaccinated in each practice
    if backend=="expectations":
        practice_figures = practice_figures.loc[(practice_figures["patient_count"]>10)&(practice_figures["vacc_group"]>0)]
        
    else:
        practice_figures = practice_figures.loc[(practice_figures["patient_count"]>250)&(practice_figures["vacc_group"]>10)]
    
    # summarise data
    practice_count = len(practice_figures.index)
    counts = practice_figures.loc[practice_figures["decline_group"]>0]["decline_group"].count()
    d = {"practices with declines":counts, "total practices":practice_count}
    out = pd.Series(d, index=["practices with declines", "total practices"])
    out.to_csv(f"{output_dir}/practice_decline_summary.csv")

    practice_figures = practice_figures.assign(
        decline_per_1000 = 1000*practice_figures["decline_group"]/practice_figures["patient_count"],
        decline_per_1000_vacc = 1000*practice_figures["decline_group"]/practice_figures["vacc_group"],
        vacc_per_1000 = 1000*practice_figures["vacc_group"]/practice_figures["patient_count"]
    )

    for plot_type in ["hist","boxplot", "heatmap"]:
        if plot_type=="hist":
            out = practice_figures.copy()
            fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
            bins = {0: [0,5,10,15,20,25,30,35,40,45,50,100,500],
                    1: [0,10,20,30,40,50,60,70,80,90,100,200,300,1000]}
            labels = {}

            for n, x in enumerate(["decline_per_1000", "decline_per_1000_vacc"]):
                labels[n] = [str(a)+"-<"+str(b) for (a,b) in zip(bins[n][:-1], bins[n][1:])]
                binned = pd.cut(out[x], bins=bins[n], labels=labels[n], retbins=False, include_lowest=True, right=False)
                
                binnedcsv = pd.DataFrame(binned.value_counts()).sort_index().replace([0,1,2,3],np.NaN)
                binnedcsv.to_csv(f'{output_dir}/practice_counts_{x}.csv')
                
                binned = pd.DataFrame(binned.value_counts(normalize=True)).sort_index()

                axs[n].bar(binned.index, binned[x])
                axs[n].set_xlabel("Rate per 1000")
                axs[n].yaxis.set_major_formatter(PercentFormatter(1))
                axs[0].set_ylabel("Percent of practices")
                for tick in axs[n].get_xticklabels():
                    tick.set_rotation(90)

                title = "COVID Vaccines "+ x.replace("_"," ").replace("decline", "declined\n").replace("vacc","vaccinated").title()+" Patients"
                axs[n].set_title(title)

        if (plot_type=="boxplot") | (plot_type=="heatmap"):
            out = practice_figures.copy()
            # ensure that at least 1% of people in each practice have been vaccinated
            # (those with a v young population e.g. student/military may have small numbers)
            out = out.loc[out["vacc_per_1000"]>10]

            # convert practice list sizes to bins
            if backend=="expectations":
                bins = [0, 10, 15, 20, 25, 100]
                labels = [str(a)+"-<"+str(b) for (a,b) in zip(bins[:-1], bins[1:])]
            else:
                bins = [250, 750, 1_000, 1_250, 1_500, 1_750, 2_000, 2_250, 2_500, 2_750, 3_000, 3_250, 3_500, 3_750, 4_000,
                        4_330, 4_660, 5_000, 5_330, 5_660, 6_000, 6_500, 7_000, 8_000, 10_000, 100_000]
                labels = ["<"+str(f'{b:,}') for b in bins[1:]]
                labels[-2] = "<"+str(int(bins[-2]/1000))+"k"
                labels[-1] = ">="+str(int(bins[-2]/1000))+"k"
            out["prac_size"] = pd.cut(out["patient_count"], bins=bins, labels=labels, retbins=False, include_lowest=True, right=False)
            

            if (plot_type=="boxplot"):
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
                        title = "COVID Vaccines Recorded as Declined per 1000 vaccinated patients\n in priority groups per practice"
                        ylabel = "Rate per 1000"
                    else:
                        title = "COVID Vaccines Recorded as Declined\n per practice"
                        ylabel = "Vaccines Recorded as Declined"
                    axs[n].set_ylabel(ylabel)
                    axs[n].set_title(title)
                ticks = axs[n].get_xticks()
                plt.xticks(ticks, list(plotting.index.unique()), rotation=90)
                axs[1].set_xlabel("Practice population size")
            

        if plot_type=="heatmap":
            
            fig, axs = plt.subplots(2, 1, tight_layout=True, figsize=(6,8))
            for n, x in enumerate(["decline_per_1000", "decline_per_1000_vacc"]):
                #bins = {}
                if backend=="expectations":
                    #bins[0] = [0, 2, 4, 6, 8, 20]
                    bins = [0, 1, 2, 3, 4]
                    _, edges = pd.cut(out[x], bins=bins, retbins=True)
                    edges = [round(x,1) for x in edges]
                else:
                    #bins[0] = [0, 20, 40, 60, 80, 100, 120, 140, 160, 2000]
                    bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 100, 1000]
                    _, edges = pd.cut(out[x], bins=bins, retbins=True)
                    edges = [int(x) for x in edges]

                out[f"{x}_binned"] = pd.cut(out[x], bins=bins, labels=edges[:-1], retbins=False, include_lowest=True)

                plotting = out.groupby([f"{x}_binned","prac_size"])[["patient_count"]].count().unstack()
                plotting.columns = plotting.columns.droplevel()

                # replace low numbers with 2 
                plotting = plotting.replace([1,2,3], 2)

                # export csv
                plotting.to_csv(f'{output_dir}/practice_list_size_{x}.csv')

                # plot heat map
                im = axs[n].imshow(plotting, cmap='RdPu', interpolation='nearest')

                # Create colorbar
                fig.colorbar(im, ax=axs[n])
                #cbar.ax.set_ylabel("no of practices", ax=axs[n], rotation=-90, va="bottom")

                if "per_1000" in x:
                    ylabel = "Rate per 1000"
                    title = "COVID Vaccines recorded as Declined\n per 1000 patients in priority groups\n per practice"
                elif "per_1000_vacc" in x:
                    ylabel = "Rate per 1000"
                    title = "COVID Vaccines recorded as Declined\n per 1000 _vaccinated_ patients in priority groups\n per practice"
                else:
                    title = "COVID Vaccines recorded as Declined\n per practice"
                    ylabel = "Vaccines Recorded as Declined"

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

        fig.savefig(f"{output_dir}/declines_by_practice_{plot_type}.png")



def declined_vaccinated(input_path="output/cohort.pickle", output_dir=out_path):
    ''' Counts patients who went from "Declined" to "Vaccinated".
        Creates a chart. 
    '''

    cohort_all = pd.read_pickle(input_path)
    
    # limit to priority groups (ages 50+ and clinical priority groups)
    cohort_all = cohort_all.loc[cohort_all["wave"]!=0]

    cohort_all["wave"] = cohort_all["wave"].astype(str)
    
    cohort = cohort_all.copy()[["wave", "vacc_group", "declined_accepted_group", "decline_total_group", "patient_id"]]

    # look at all priority groups
    cohort = cohort.groupby("wave").agg({"vacc_group":"sum", 
                                        "declined_accepted_group":"sum", 
                                        "decline_total_group":"sum", 
                                        "patient_id":"nunique"})
    cohort = cohort.rename(columns=group_names, index=wave_column_headings)
    cohort = ((cohort // 7) * 7).astype(int)
    cohort.to_csv(f'{output_dir}/declined_then_accepted.csv')
    cohort = cohort.assign(
        per_1000 = 1000*cohort["Declined then received"]/cohort["total"],
        per_1000_vacc = 1000*cohort["Declined then received"]/cohort["Vaccinated"],
        converted = 1000*cohort["Declined then received"]/cohort["Declined - all"]
    )

    # plot charts
    plot_decl_acc_charts(df=cohort, output_dir=output_dir, chart="all")
    

    # look at priority groups split by demographics

    cohort = cohort_all[["wave", "vacc_group", "declined_accepted_group", "decline_total_group", "patient_id", 
                        "high_level_ethnicity"]]

    # group by wave and ethnicity
    cohort = cohort.groupby(["wave", "high_level_ethnicity"]).agg({"vacc_group":"sum", 
                                    "declined_accepted_group":"sum", 
                                    "decline_total_group":"sum", 
                                    "patient_id":"nunique"})
 
    # rename column headers and indices (2 levels)
    cohort = cohort.rename(index=high_level_ethnicities, columns=group_names)
    cohort = cohort.rename(index=wave_column_headings)

    # low number suppression and rounding
    cohort = cohort.replace([1,2,3,4,5,6], 0)
    cohort = ((cohort // 7) * 7).astype(int)

    cohort = cohort.assign(
        per_1000 = 1000*cohort["Declined then received"]/cohort["total"],
        per_1000_vacc = 1000*cohort["Declined then received"]/cohort["Vaccinated"],
        converted = 1000*cohort["Declined then received"]/cohort["Declined - all"]
    )

    cohort.to_csv(f'{output_dir}/declined_then_accepted_by_wave.csv')


def decl_acc_time_delay(input_path="output/cohort.pickle", output_dir=out_path):
    '''
    Measures the time between recorded decline and vaccination for each pt in the declined-then-accepted group,
    and groups to number of weeks.
    '''

    cohort = pd.read_pickle(input_path)

    # limit to priority groups (ages 50+ and clinical priority groups)
    cohort = cohort.loc[cohort["wave"]!=0]

    # filter to the declined-then-accepted group
    cohort = cohort.loc[cohort["declined_accepted_group"]==1]
    cohort = cohort[["wave", "declined_accepted_group", "patient_id", "vacc1_dat", "decl_first_dat", "high_level_ethnicity"]]
    cohort["wave"] = cohort["wave"].astype(str)
    # calculate no of days between recorded decline and vaccination.
    cohort["date_diff"] = cohort["vacc1_dat"] - cohort['decl_first_dat']
    
    # bin the data
    bins = [
        pd.Timedelta(days = 0),
        pd.Timedelta(days = 14),
        pd.Timedelta(days = 28),
        pd.Timedelta(weeks = 8),
        pd.Timedelta(weeks = 120)
        ]
    labels = ["0-<2 weeks", "2-<4 weeks", "1-<2 months", ">=2 months"]

    cohort["weeks_diff"] = pd.cut(cohort["date_diff"], bins=bins, labels=labels, retbins=False, include_lowest=True, right=False)
    

    # summarise for each group
    cohort_a = cohort.groupby(["wave","weeks_diff"])["patient_id"].count()
    cohort_a = cohort_a.rename(index=wave_column_headings)
    
    # low number suppression and rounding
    cohort_a = cohort_a.replace([1,2,3,4,5,6], 0)
    cohort_a = ((cohort_a // 7) * 7).astype(int)

    cohort_a.to_csv(f"{output_dir}/declined_accepted_weeks_by_wave.csv")

    
    # look at priority groups split by demographics

    cohort_b = cohort.copy()

    # group by wave and ethnicity
    cohort_b = cohort_b.groupby(["wave", "high_level_ethnicity","weeks_diff"])["patient_id"].count()
 
    # rename column headers and indices (2 levels)
    cohort_b = cohort_b.rename(index=high_level_ethnicities)
    cohort_b = cohort_b.rename(index=wave_column_headings)

    # low number suppression and rounding
    cohort_b = cohort_b.replace([1,2,3,4,5,6], 0)
    cohort_b = ((cohort_b // 7) * 7).astype(int)

    cohort_b.to_csv(f"{output_dir}/declined_accepted_weeks_by_wave_and_ethnicity.csv")
    

def plot_decl_acc_charts(df, output_dir, chart="all"):
    '''
    Plots one or 3 charts of vaccines declined-then-accepted.
    'chart' can be one of "per_1000", "per_1000_vacc", "converted", or "all"
    '''

    cohort = df
    titles = {"per_1000_vacc":"Patients Declining and later Receiving COVID Vaccines\n per 1000 vaccinated patients",  
              "converted": "Patients Declining and later Receiving COVID Vaccines\n per 1000 patients recorded as declining",
              "per_1000": "Patients Declining and later Receiving COVID Vaccines\n per 1000 patients"
    }

    if chart=="all": # plot 3 charts
        fig, axs = plt.subplots(3, 1, sharex=True, tight_layout=True, figsize=(6,12))
        for n, x in enumerate(["per_1000", "per_1000_vacc", "converted"]):
            cohort[x].plot(kind='bar', stacked=True, ax=axs[n])
            title = titles[x]
            axs[n].set_ylabel("Rate per 1000")
            axs[n].set_title(title)
        axs[1].set_xlabel("Priority group")
    else: # plot a single chart as specified
        fig, ax = plt.subplots(figsize=(10,10))
        cohort[chart].plot(kind='bar', stacked=True, ax=ax)
        title = titles[chart]
        ax.set_ylabel("Rate per 1000")
        ax.set_title(title)
        ax.set_xlabel("Priority group")
    
    fig.savefig(f"{output_dir}/{chart}_declined_then_accepted_by_wave.png")


def invert_df(df, group="all"):
    ''' "Inverts" df: 
    calculates the difference between the total population ("total" row) and 
    each other row in turn, so if `df` counts "patients vaccinated", the resulting
    df counts "patients NOT vaccinated".
    '''
    for i in df.index.drop("total"):
        df.loc[i] = df.loc["total"] - df.loc[i]

    return df
