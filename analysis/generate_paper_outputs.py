import base64
import os
from datetime import datetime, timedelta

import jinja2
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedFormatter, PercentFormatter
from matplotlib.dates import TU, WeekdayLocator
import pandas as pd

from compute_uptake_for_paper import cols, demographic_cols, other_cols
from ethnicities import ethnicities, high_level_ethnicities
from groups import groups, at_risk_groups

# Ensure SVGs are created reproducibly
mpl.rcParams["svg.hashsalt"] = 42

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


title_starts = {
        "dose_1": "Vaccination Coverage",
        "unreached": "People Not Reached",
        "declined": "Vaccines declined"
    }

title_ends = {
        "dose_1": "who \n have received their first COVID vaccine",
        "unreached": "with\n no COVID vaccine-related records",
        "declined": "who\n have declined a COVID vaccine"
    }

subtitles = {
        "dose_1": "First dose",
        "unreached": "No Vaccine-Related Record",
        "declined": "Declined",
    }


# Add thousands separators to all integers in HTML output
class IntArrayFormatter(pd.io.formats.format.GenericArrayFormatter):
    def _format_strings(self):
        return [f" {v:,}" for v in self.values]

pd.io.formats.format.IntArrayFormatter = IntArrayFormatter


def run(base_path, earliest_date, latest_date):
    backend = base_path.rstrip("/").split("/")[-1]
    demographic_titles = get_demographic_titles()
    label_maps = get_label_maps()

    tables_path = f"{base_path}/tables"
    charts_path = f"{base_path}/charts"
    reports_path = f"{base_path}/reports"
    os.makedirs(tables_path, exist_ok=True)
    os.makedirs(charts_path, exist_ok=True)
    os.makedirs(reports_path, exist_ok=True)
    
    for wave in range(1, 9 +1):
        generate_stacked_charts_for_wave(
                    base_path,
                    charts_path,
                    wave,
                    earliest_date,
                    latest_date,
                    demographic_titles,
                    label_maps
                )

    for key in ["dose_1", 
                "unreached",
                "declined"]:
        in_path = f"{base_path}/cumulative_coverage/all/{key}/all_{key}_by_group.csv"
        title_start = title_starts[key]
        title_end = title_ends[key]
        generate_summary_table_for_all(
            in_path, tables_path, key, earliest_date, latest_date, title_start
        )
        generate_charts_for_all(in_path, charts_path, key, earliest_date, latest_date, title_end)
        generate_report_for_all(
            backend,
            tables_path,
            charts_path,
            reports_path,
            key,
            earliest_date,
            latest_date,
            subtitles
        )
        
        for wave in range(1, 9 + 1):
            in_path = f"{base_path}/cumulative_coverage/group_{wave}/{key}"

            generate_summary_table_for_wave(
                in_path,
                tables_path,
                wave,
                key,
                earliest_date,
                latest_date,
                demographic_titles,
                label_maps, 
                title_start
            )

            generate_charts_for_wave(
                in_path,
                charts_path,
                wave,
                key,
                earliest_date,
                latest_date,
                demographic_titles,
                label_maps, 
                title_start
            )

            generate_report_for_wave(
                backend,
                tables_path,
                charts_path,
                reports_path,
                wave,
                key,
                earliest_date,
                latest_date,
                subtitles
            )


def generate_summary_table_for_all(
    in_path, tables_path, key, earliest_date, latest_date, title_start
):
    uptake = load_uptake(in_path, earliest_date, latest_date)
    last_week_date = uptake.index[-9]
    summary = pd.DataFrame(
        {
            "latest": uptake.iloc[-2],
            "last_week": uptake.iloc[-8],
            "total": uptake.iloc[-1],
        }
    )
    summary.loc["total"] = summary.sum()

    summary["latest_pc"] = 100 * summary["latest"] / summary["total"]
    summary["last_week_pc"] = 100 * summary["last_week"] / summary["total"]
    summary["in_last_week_pc"] = summary["latest_pc"] - summary["last_week_pc"]

    columns = {
        "latest_pc": f"{title_start} at {latest_date} (%)",
        "latest": f"{title_start} at {latest_date} (n)",
        "total": "Population",
        "last_week_pc": f"{title_start} at {last_week_date} (%)",
        "in_last_week_pc": f"{title_start} in past week (%)",
    }
    summary = summary[list(columns)]
    summary.rename(columns=columns, inplace=True)

    rows = {str(wave): f"Group {wave}" for wave in range(1, 9 + 1)}
    rows["0"] = "Other"
    rows["total"] = "Population"
    summary = summary.loc[list(rows)]
    summary.rename(index=rows, inplace=True)

    summary.to_csv(f"{tables_path}/all_{key}.csv", float_format="%.1f%%")


def generate_charts_for_all(in_path, charts_path, key, earliest_date, latest_date, title_end):
    uptake = load_uptake(in_path, earliest_date, latest_date)
    if uptake.iloc[-2].max()>1_000_000:
        uptake_total = uptake.iloc[:-1] / 1_000_000
        units="millions"
    else: 
        uptake_total = uptake.iloc[:-1] / 1_000
        units="thousands"
    uptake_total["total"] = uptake_total.loc[:, "0":"9"].sum(axis=1)
    uptake_total["all_priority"] = uptake_total.loc[:, "1":"9"].sum(axis=1)
    uptake_total = uptake_total.loc[:, ["total", "all_priority", "0"]]
    uptake_total = uptake_total[
        [col for col in wave_column_headings if col in uptake_total.columns]
    ]
    uptake_total.rename(columns=wave_column_headings, inplace=True)
    plot_chart(
        uptake_total,
        f"Total number of patients {title_end} ({units})",
        f"{charts_path}/all_{key}_total.png",
        is_percent=False,
    )

    uptake_pc = 100 * uptake / uptake.loc["total"]
    uptake_pc.drop("total", inplace=True)
    uptake_pc.fillna(0, inplace=True)
    columns = {str(wave): f"Group {wave}" for wave in range(1, 9 + 1)}
    columns["0"] = "Other"
    uptake_pc = uptake_pc[
        [col for col in wave_column_headings if col in uptake_pc.columns]
    ]
    uptake_pc.rename(columns=wave_column_headings, inplace=True)
    plot_chart(
        uptake_pc,
        f"Proportion of patients {title_end}",
        f"{charts_path}/all_{key}_percent.png",
    )


def generate_report_for_all(
    backend, tables_path, charts_path, out_path, key, earliest_date, latest_date, subtitles
):

    subtitle = subtitles[key]

    summary = pd.read_csv(f"{tables_path}/all_{key}.csv", index_col=0)

    charts = []
    with open(f"{charts_path}/all_{key}_total.png", "rb") as f:
        charts.append(base64.b64encode(f.read()).decode("utf8"))
    with open(f"{charts_path}/all_{key}_percent.png", "rb") as f:
        charts.append(base64.b64encode(f.read()).decode("utf8"))

    ctx = {
        "subtitle": subtitle,
        "backend": backend,
        "latest_date": latest_date,
        "charts": charts,
        "table": summary.to_html(
            classes=["table", "table-sm"], border="0", float_format="%.1f%%"
        ),
    }

    with open("templates/summary.html") as f:
        template = jinja2.Template(f.read())

    with open(f"{out_path}/all_{key}.html", "w") as f:
        f.write(template.render(ctx))


def generate_summary_table_for_wave(
    in_path, out_path, wave, key, earliest_date, latest_date, demographic_titles, label_maps, title_start
):
    uptake = load_uptake(
        f"{in_path}/group_{wave}_{key}_by_ethnicity.csv", earliest_date, latest_date
    )
    if uptake is None:
        return

    last_week_date = uptake.index[-9]
    overall_summary = compute_summary(uptake)
    summaries = {"Overall": pd.DataFrame({"-": overall_summary.sum(axis=0)}).transpose()}

    at_risk_summary = {}
    other_summary = {}

    for col in cols:
        demographic_title = demographic_titles[col]
        labels = label_maps[col]
        uptake = load_uptake(
            f"{in_path}/group_{wave}_{key}_by_{col}.csv", earliest_date, latest_date
        )

        if col in demographic_cols:
            summaries[demographic_title] = compute_summary(uptake, labels)
        # elif col in at_risk_cols:
        #     summary = compute_summary(uptake)
        #     if "True" in summary.index:
        #         at_risk_summary[demographic_titles[col]] = summary.loc["True"]
        elif col in other_cols:
            summary = compute_summary(uptake)
            if "True" in summary.index:
                other_summary[demographic_titles[col]] = summary.loc["True"]
        else:
            assert False, col

    # summaries["Clinical Risk Groups"] = pd.DataFrame.from_dict(
    #     at_risk_summary, orient="index"
    # )
    summaries["Other Groups"] = pd.DataFrame.from_dict(other_summary, orient="index")
    summaries = {k: v for k, v in summaries.items() if not v.empty}

    summary = pd.concat(summaries.values(), keys=summaries.keys())
    summary["latest_pc"] = 100 * summary["latest"] / summary["total"]
    summary["last_week_pc"] = 100 * summary["last_week"] / summary["total"]
    summary["in_last_week_pc"] = summary["latest_pc"] - summary["last_week_pc"]

    columns = {
        "latest_pc": f"{title_start} at {latest_date} (%)",
        "latest": f"{title_start} at {latest_date} (n)",
        "total": "Population",
        "last_week_pc": f"{title_start} at {last_week_date} (%)",
        "in_last_week_pc": f"{title_start} in past week (%)",
    }
    summary = summary[list(columns)]
    summary.rename(columns=columns, inplace=True)

    summary.to_csv(f"{out_path}/group_{wave}_{key}.csv", float_format="%.1f%%")


def compute_summary(uptake, labels=None):
    latest_date = datetime.strptime(uptake.index[-2], "%Y-%m-%d").date()
    last_week_date = datetime.strptime(uptake.index[-9], "%Y-%m-%d").date()
    assert latest_date - last_week_date == timedelta(days=7)

    summary = pd.DataFrame(
        {
            "latest": uptake.iloc[-2],
            "last_week": uptake.iloc[-8],
            "total": uptake.iloc[-1],
        }
    )

    if labels is not None:
        summary.rename(index=labels, inplace=True)
    return summary


def generate_charts_for_wave(
    in_path, out_path, wave, key, earliest_date, latest_date, demographic_titles, label_maps, title_start
):
    for col in cols:
        title = f"{title_start} in Priority Group {wave}\nby {demographic_titles[col]}"
        labels = label_maps[col]
        uptake = load_uptake(
            f"{in_path}/group_{wave}_{key}_by_{col}.csv", earliest_date, latest_date
        )
        if uptake is None:
            return

        cohort_average = 100 * uptake.sum(axis=1).iloc[-2] / uptake.sum(axis=1).iloc[-1]
        uptake_pc = compute_uptake_percent(uptake, labels)
        plot_chart(
            uptake_pc, title, f"{out_path}/group_{wave}_{key}_{col}.png", cohort_average,
        )

        if col == "ethnicity":
            plot_chart(
                uptake_pc,
                title,
                f"{out_path}/group_{wave}_{key}_{col}_highlighting_bangladeshi_ethnicity.png",
                cohort_average,
                highlight_bangladeshi_ethnicity=True,
            )


def generate_stacked_charts_for_wave(
    base_path, out_path, wave, earliest_date, latest_date, demographic_titles, label_maps
):
    for col in cols: # e.g. ethnicity
        group_name = wave_column_headings[str(wave)]
        title = f"Vaccination and Decline rates among those in '{group_name}' group\n by {demographic_titles[col]}"
        labels = label_maps[col]
        uptake_by_dem = pd.Series()

        for key in subtitles: # e.g. declined
            in_path = f"{base_path}/cumulative_coverage/group_{wave}/{key}"
            uptake = load_uptake(
                f"{in_path}/group_{wave}_{key}_by_{col}.csv", earliest_date, latest_date
            )
            if uptake is None:
                return
            
            uptake = uptake.rename(index={uptake.index[-2]:key})
            if key=="dose_1":
                uptake = uptake.tail(2)
            else:
                uptake = uptake.iloc[-2]
            
            # combine keys (e.g. vaccinated, declined etc)
            uptake_by_dem = uptake_by_dem.append(uptake)

        uptake_pc = compute_uptake_percent(uptake_by_dem, labels)
        uptake_pc = uptake_pc.rename(columns=subtitles)
        uptake_pc = uptake_pc.transpose().drop(0)

        plot_stacked_chart(
            uptake_pc, title, f"{out_path}/wave_{wave}_{key}_{col}.png"
        )

            
def compute_uptake_percent(uptake, labels):
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
    uptake_pc.rename(columns=labels, inplace=True)
    return uptake_pc


def generate_report_for_wave(
    backend, tables_path, charts_path, out_path, wave, key, earliest_date, latest_date, subtitles
):

    subtitle = subtitles[key]

    subtitle = f"{subtitle} / Priority Group {wave}"

    try:
        summary = pd.read_csv(f"{tables_path}/group_{wave}_{key}.csv", index_col=[0, 1])
    except FileNotFoundError:
        return

    charts = []
    for col in cols:
        with open(f"{charts_path}/group_{wave}_{key}_{col}.png", "rb") as f:
            charts.append(base64.b64encode(f.read()).decode("utf8"))

    ctx = {
        "subtitle": subtitle,
        "backend": backend,
        "latest_date": latest_date,
        "charts": charts,
        "table": summary.to_html(
            classes=["table", "table-sm"], border="0", float_format="%.1f%%"
        ),
    }

    with open("templates/summary.html") as f:
        template = jinja2.Template(f.read())

    with open(f"{out_path}/group_{wave}_{key}.html", "w") as f:
        f.write(template.render(ctx))


def get_demographic_titles():
    demographic_titles = {
        "ethnicity": "Ethnicity",
        "high_level_ethnicity": "Ethnicity (broad categories)",
        "imd_band": "Index of Multiple Deprivation",
    }

    demographic_titles.update(groups)
    demographic_titles.update(at_risk_groups)

    return demographic_titles


def get_label_maps():
    labels = {
        "ethnicity": {str(k): v for k, v in ethnicities.items()},
        "high_level_ethnicity": {str(k): v for k, v in high_level_ethnicities.items()},
        "imd_band": {
            "0": "Unknown",
            "1": "1 (most deprived)",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5 (least deprived)",
        },
    }

    for group in groups:
        labels[group] = {"False": "no", "True": "yes"}

    for group in at_risk_groups:
        labels[group] = {"False": "no", "True": "yes"}

    return labels


def plot_chart(
    df,
    title,
    out_path,
    cohort_average=None,
    is_percent=True,
    highlight_bangladeshi_ethnicity=False,
):
    df.index = pd.to_datetime(df.index)
    ax = plt.gca()

    if highlight_bangladeshi_ethnicity:
        for col in df.columns:
            if "Bangladeshi" in col:
                c, alpha, thickness = "r", 1, 3
                label = "Asian or Asian British - Bangladeshi"
            elif "Asian or Asian British" in col:
                c, alpha, thickness = "r", 0.6, 1
                label = "Asian or Asian British"
            else:
                c, alpha, thickness = "b", 0.3, 1
                label = "Other ethnicities"
            ax.plot(df[col], alpha=alpha, c=c, label=label, linewidth=thickness)

        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(
            by_label.values(),
            by_label.keys(),
            bbox_to_anchor=(1.05, 1),
            loc=2,
            borderaxespad=0,
        )
    else:
        df.plot(ax=ax)
        ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)

    ax.set_title(title)

    # Add x-axis ticks for each Tuesday (the day that vaccines were first made
    # available.)
    week_days = df.loc[df.index.dayofweek == TU.weekday]
    tick_labels = [
        d.strftime("%d %b %Y")
        if ix == 0 or d.month == 1 and d.day <= 7
        else d.strftime("%d %b")
        for ix, d in enumerate(week_days.index)
    ]
    ax.xaxis.set_major_locator(WeekdayLocator(byweekday=TU, interval=1))
    ax.xaxis.set_major_formatter(FixedFormatter(tick_labels))
    ax.xaxis.set_tick_params(rotation=90)

    ax.set_ylim(ymin=0)

    if is_percent:
        ax.yaxis.set_major_formatter(PercentFormatter())
        if "declined" in out_path:
            ymax = df.max().max()*1.05
        else:
            ymax=100
        ax.set_ylim(ymax=ymax)

    if cohort_average is not None:
        ax.axhline(cohort_average, color="k", linestyle="--", alpha=0.5)
        ax.text(df.index[0], cohort_average * 1.02, "latest overall cohort rate")

    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_stacked_chart(df, title, out_path):
    ax = plt.gca()
    df.plot(kind='bar', stacked=True, ax=ax)

    ax.set_ylabel("Percent")
    ax.set_title(title)
    ax.set_ylim(ymax=100)
    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)

    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()

def load_uptake(path, earliest_date, latest_date):
    try:
        uptake = pd.read_csv(path, index_col=0)
    except FileNotFoundError:
        return

    return uptake.loc[
        ((uptake.index >= earliest_date) & (uptake.index <= latest_date))
        | (uptake.index == "total")
    ]


#if __name__ == "__main__":
#    import sys

#    run(*sys.argv[1:])
