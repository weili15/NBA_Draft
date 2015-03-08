""" Read in and analyze NBA Draft data since 1980
Author : Wei
Date : Mar 7 2015

"""
import pandas as pd
import matplotlib.pyplot as plt

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

x=all_drafts['Pk'][pd.notnull(all_drafts['WS/48'])].tolist()
y=all_drafts['WS/48'][pd.notnull(all_drafts['WS/48'])].tolist()
plt.scatter(map (int,x),map(float,y))
plt.xlabel('Pick')
plt.ylabel('Win shares')
plt.tight_layout(pad=1)
plt.ylim([-.5,.5])
plt.xlim([-5,20])
plt.show()
