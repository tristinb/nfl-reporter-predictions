
import sqlite3
import pandas as pd
import scipy.stats

filename = 'nfl_predictions.sqlite'
conn = sqlite3.connect(filename)

predictions = pd.read_sql_query('SELECT week,pundit,team1,team2,score1 AS pred1,score2 AS pred2 FROM Predictions', conn)



file2 = '/Users/tristinbeckman/Dropbox/stat/nfl/nfl_stats.sqlite'
conn2 = sqlite3.connect(file2)

# Need to use subquery to get team names
nfl_stats = pd.read_sql_query('SELECT Week,(SELECT team from Team WHERE id = team_id) AS team1,(SELECT team from Team WHERE id = opp_id) AS team2, Points_off AS points1, Points_def AS points2 FROM Stats WHERE Year=2017', conn2)

# First file only contains team name; not city
nfl_stats['team1'] = nfl_stats['team1'].str.split().str[-1]
nfl_stats['team2'] = nfl_stats['team2'].str.split().str[-1]

# Make buccaneers consistent
predictions.loc[predictions.team1 == 'Bucs', 'team1'] = 'Buccaneers'
predictions.loc[predictions.team2 == 'Bucs', 'team2'] = 'Buccaneers'

# Michael Rothstein is more commonly called Mike
predictions.loc[predictions.pundit=='Michael Rothstein','pundit'] = 'Mike Rothstein'

data = pd.merge(predictions,nfl_stats, how='left',left_on=['week','team1','team2'],right_on=['Week','team1','team2'])

data = data.drop(columns=['Week'])

# Get point spreads
    # Favorite always listed first; min data['spread'] is one
data['spread'] = data['pred1'] - data['pred2']

# Get probability (see 'On the probability of winning a football game')
data['pred_prob'] = scipy.stats.norm(0,14).cdf(data['spread'])

# Did predicted team win?
data['win'] = data['points1'] > data['points2']
data['win'] = data['win']*1 # turn into 1, 0

# Brier score: MSE of forecast 1/n sum (pred_prob - win)^2
data['squared_error'] = (data['pred_prob'] - data['win'])**2


data_group = data[['pundit','week','team1','team2','spread','win','squared_error']].copy()

# Note: using data_group.groupby(['pundit'])['team1'].count() shows counts for each pundit

# Find each pundit's team
data_group = data_group.sort_values(by=['pundit','week'])
data_group['pundit_team'] = 'No team' # This is column 8
for i in range(len(data_group['pundit'])-1):
    if data_group.iloc[i,0] == data_group.iloc[i+1,0]:
        if data_group.iloc[i,7]!='No team':
            data_group.iloc[i+1,7] = data_group.iloc[i,7]
        elif data_group.iloc[i,2] == data_group.iloc[i+1,2]: # 1, 1
            data_group.iloc[i,7] = data_group.iloc[i,2]
            data_group.iloc[i+1,7] = data_group.iloc[i,2]
        elif data_group.iloc[i,2] == data_group.iloc[i+1,3]: # 1, 2
            data_group.iloc[i,7] = data_group.iloc[i,2]
            data_group.iloc[i+1,7] = data_group.iloc[i,2]
        elif data_group.iloc[i,3] == data_group.iloc[i+1,2]: # 2, 1
            data_group.iloc[i,7] = data_group.iloc[i,3]
            data_group.iloc[i+1,7] = data_group.iloc[i,3]
        elif data_group.iloc[i,3] == data_group.iloc[i+1,3]: # 2, 2
            data_group.iloc[i,7] = data_group.iloc[i,3]
            data_group.iloc[i+1,7] = data_group.iloc[i,3]

# Get total wins for Year
tot_wins= pd.read_sql_query('SELECT Week,(SELECT team from Team WHERE id = team_id) AS team, Tot_wins as tot_wins FROM Stats WHERE Year=2017 ', conn2)

# remove city from team name
tot_wins['team'] = tot_wins['team'].str.split().str[-1]

data_group = pd.merge(data_group, tot_wins, left_on=['pundit_team','week'], right_on=['team','Week'])

data_group

data_group = data_group[data_group.pundit_team!='No team']
data_group.to_csv('pundit_data.csv', index=False)


# Include total wins for 2016, 2017 season in grouped data

win_tots_16 = pd.read_sql_query('SELECT Year,(SELECT team from Team WHERE id = team_id) AS team, Tot_Wins as tot_wins_16 FROM Stats WHERE Week=17 and Year=2016 ', conn2)
win_tots_16 = win_tots_16.drop('Year',axis=1) # SLOPPY, figure out better query
win_tots_16['team'] = win_tots_16['team'].str.split().str[-1]

win_tots_17 = pd.read_sql_query('SELECT Year,(SELECT team from Team WHERE id = team_id) AS team, Tot_Wins as tot_wins_17 FROM Stats WHERE Week=17 and Year=2017 ', conn2)
win_tots_17 = win_tots_17.drop('Year',axis=1)
win_tots_17['team'] = win_tots_17['team'].str.split().str[-1]

#
win_tots = pd.merge(win_tots_16, win_tots_17, on='team')

data_standing = data_group.groupby(['pundit','pundit_team'], as_index=False).mean()

# Make sure all groups are same size
print(data_group.groupby(['pundit','pundit_team'], as_index=False).size())



data_standing = data_standing.sort_values(by=['squared_error'])

data_standing['standing'] = range(1, len(data_standing['pundit'])+1, 1)
data_standing = pd.merge(data_standing, win_tots, left_on='pundit_team', right_on='team')
data_standing = data_standing.drop('team', axis=1)
print(data_standing)
data_standing.to_csv('pundit_standings.csv', index=False)
