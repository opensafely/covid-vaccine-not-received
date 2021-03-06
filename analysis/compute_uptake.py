import os
import pandas as pd

from groups import groups


def compute_uptake(cohort, event_col, stratification_col):
    stratification_series = cohort[stratification_col]
    stratification_vals = sorted(stratification_series.value_counts().index)

    event_dates = cohort[cohort[event_col].notnull()][event_col]
    if event_dates.empty:
        return

    earliest, latest = min(event_dates), max(event_dates)
    index = [str(date.date()) for date in pd.date_range(earliest, latest)]

    uptake = pd.DataFrame(index=index)

    for stratification_val in stratification_vals:
        filtered = cohort[stratification_series == stratification_val]
        series = pd.Series(0, index=index)
        for date, count in filtered[event_col].value_counts().iteritems():
            series[str(date.date())] = count
        uptake[stratification_val] = series.cumsum()

    uptake.loc["total"] = stratification_series.value_counts()
    uptake.fillna(0, inplace=True)
    return ((uptake // 7) * 7).astype(int)


if __name__ == "__main__":
    run()
