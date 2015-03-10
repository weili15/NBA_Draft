""" Read in and analyze NBA Draft data since 1980
Author : Wei
Date : Mar 7 2015

"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

all_draft_names=[]
for year in range(1980,2015):
    all_draft_names.append('draft_NBA_%s_stats.csv' % str(year))
all_drafts_list=[]
for draft in all_draft_names:
    this_draft = pd.read_csv(draft, header=2)
    this_draft=this_draft[~this_draft['Player'].str.contains('Round|Player')] #Drop any other headers embedded in the data
    all_drafts_list.append(this_draft)

#Make one large pandas dataframe from list.  Each year's draft is indexed
#For example, to get just 1993's draft, we reference all_drafts.ix['1993']
all_drafts=pd.concat(all_drafts_list, keys=map(str, range(1980,2015)))
all_drafts=all_drafts.convert_objects(convert_numeric=True)
all_drafts=clean_draft(all_drafts)


#WIN SHARE ANALYSIS
def Avg_WS_Picks(draft_db, plot=False):
    x=draft_db[['Pk','WS/48']]
    #Find the range of picks (#1-?)
    pick_list=sorted(set(x['Pk'].tolist())) #set function gets unique elements of picks
    pick_means=[]
    for pick in pick_list:
        x1=x['WS/48'][x['Pk']==pick].tolist() #Get win shares for each pick
        pick_mean=np.nanmean(x1)
        pick_means.append(pick_mean)

    #Graph
    if plot:
        plt.scatter(pick_list,pick_means)
        #Plot with average WS for an NBA Player
        avg_WS=np.nanmean(x['WS/48'].tolist())
        plt.plot(pick_list,np.ones(len(pick_list))*avg_WS)
        plt.xlabel('Pick')
        plt.ylabel('Average WS/48')
        plt.ylim([-.5,.5])
        plt.xlim([0,200])
        plt.xticks([0,10,25,40,50,100])
        plt.savefig('Avg_WS_vs_pick')
        plt.show()
    else:
        return pd.DataFrame({
            'Pk': pick_list,
            'Avg_WS/48' : pick_means
        })



#Plot Win shares vs. pick #
def WS_plot(draft_db):
    x=draft_db['Pk'][pd.notnull(draft_db['WS/48'])].tolist()
    y=draft_db['WS/48'][pd.notnull(draft_db['WS/48'])].tolist()
    plt.scatter(map (int,x),map(float,y))
    plt.xlabel('Pick')
    plt.ylabel('Win shares')
    plt.tight_layout(pad=1)
    plt.ylim([-.5,.5])
    #plt.xlim([-5,20])
    plt.savefig('WS_vs_pick')
    plt.show()

#Plot win share distributions for top 5 picks, 5-20, 20-30 and 30+
def WS_hist(draft_db):
    x=draft_db['Pk'][pd.notnull(draft_db['WS/48'])]
    x5=x[x<=5].tolist()
    x20=x[(x>5) & (x<=20)].tolist()
    x30=x[(x>20) & (x<=30)].tolist()
    x30_plus=x[x>30].tolist()

    y=draft_db['WS/48'][pd.notnull(draft_db['WS/48'])]
    y5=y[x<=5].tolist()
    y20=y[(x>5) & (x<=20)].tolist()
    y30=y[(x>20) & (x<=30)].tolist()
    y30_plus=y[x>30].tolist()

    plt.hist([y5,y20,y30,y30_plus], label=['Top 5','5 to 20', '20 to 30', '30+'], bins=50)
    plt.legend()
    plt.xlim(-.5,.5)
    plt.savefig('WS_hist')
    plt.show()

def clean_draft(draft_db):
    #Remove all players with WS/48>.26 (Since Michael Jordan should have the highest WS at .25).  Also remove any rows without WS data
    ret=draft_db[draft_db['WS/48']<.26]

    return ret

def WS_above_avg_team(draft_db,team):
    #Return DataFrame with this team's pick, Player, WS/48, and WS above avg
    #Requires: draft DataFrame, Expected WS/pick dataframe (taken from Avg_WS_Picks function), and team name as a string
    WS_Picks_db=Avg_WS_Picks(all_drafts)
    x1=draft_db[['Pk','Player','WS/48']][draft_db['Tm']==team] #Get win shares and picks for each team
    WS_above_avg_list=[]
    for idx in range(len(x1['Pk'].tolist())): #Iterate over this team's picks
        this_pick=x1['Pk'][idx] #Get the pick
        this_WS=x1['WS/48'][idx] #Get the Win share
        this_WS_predicted=WS_Picks_db['Avg_WS/48'][WS_Picks_db['Pk']==this_pick].values # Get expected Winshares
        WS_above_avg_list.append(round(this_WS-this_WS_predicted,4))
    x1['WS/48_above_avg']=WS_above_avg_list
    return x1

def WS_above_avg_ALL_teams(draft_db):
    #Returns Dataframe of all teams as well as their median WS above avg
    #Make list of all teams
    team_list=set(all_drafts['Tm'].tolist()) #set function gets unique elements of teams
    WS_above_avg_teams=[]
    for team in team_list:
        this_team_db=WS_above_avg_team(all_drafts,team)
        this_WS_above_avg_mean=np.nanmedian(this_team_db['WS/48_above_avg'].tolist()) #We take the median to avoid the effects of extreme outliers
        WS_above_avg_teams.append(this_WS_above_avg_mean)
    ret=pd.DataFrame({
        'Tm': list(team_list),
        'WS_above_avg' : WS_above_avg_teams
    }).sort('WS_above_avg',ascending=False)

