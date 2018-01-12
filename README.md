# Ranking ESPN NFL Nation Reporters

Every week during the regular season, each ESPN *NFL Nation* reporter provided predicted spreads for their team.

The data are unstructured, with various inconsistencies in the HTML across weeks. Furthermore, because week 1 predictions are behind a paywall and reporters did not forecast Thursday night games, these games are not included in the analysis. The script predict_links.py gathers the data.

To rank the forecasts, the script predictions.py combines data from an SQL table derived from pro-football-reference.com, the script for this data are in a previous [GitHub Repo](https://github.com/tristinb/pro-football-reference).

Plots and a more complex model are built in the script Brier_analysis.R

The writeup was converted from markdown to TeX using pandoc.
