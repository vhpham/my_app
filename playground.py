# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 21:49:34 2018

@author: vietpham

"""
import pandas as pd
import sqlite3
import os
import datetime
import math

def check_odd_type(df):
	"""
	return if the odd_id has 1x2, 1/2, Goal, Over/Under
	"""
	tmp = df.isnull().sum()
	result = dict()
	typ = ['Home (1)','1/2','AH','Over']
	for t in typ:
		result[t] = False
	for c,v in tmp.iteritems():
		for t in typ:
			if t in c:
				if v<len(df): # if v=len(df) => all are null , if v=0 => all the odd are available, if 0<v<len(df) => the odd remove
					result[t] = True
					break
		if result[t]:
			typ.remove(t)
		if len(typ)==0:
			break
	result['1x2'] = result.pop('Home (1)')
	result['OU'] = result.pop('Over')			
	return result



file_name = os.path.join(os.getcwd(),'Works/data/sp.db')
conn = sqlite3.connect(file_name)
match_df = pd.read_sql_query("SELECT * FROM Match_info",con=conn)
match_id = match_df['id'].values.tolist()
df = match_df['id_live'].fillna(0)
match_id_live = df.unique().tolist()
match_id_live.remove(0)
match_id_live.remove('')

odd_live_df = pd.DataFrame()
for tID in match_id_live:
    df = pd.read_sql_query("SELECT * FROM Odd_{}".format(tID),con=conn)
    odd_live_df = odd_live_df.append(df, ignore_index=True)

odd_live_df.sort_values('datetime',inplace=True)
odd_live_df['isLive'] = 1
odd_df['isLive'] = 0
bet_list = []
odd_df = pd.DataFrame()
for tID in match_id:
    df = pd.read_sql_query("SELECT * FROM Odd_{}".format(tID),con=conn)
    #bet_list.append(check_odd_type(df))
    odd_df = odd_df.append(df, ignore_index=True)

odd_df.sort_values('datetime',inplace=True)

match_df['odd_list'] = bet_list
# to UTC
match_df['startTime'] = pd.to_datetime(match_df['startTime'],yearfirst=True)
match_df['startTime'] = match_df['startTime'] - datetime.timedelta(hours=8)

odd_cmb_df = odd_df.append(odd_live_df, ignore_index=True)
# to UTC
odd_cmb_df['startTime'] = pd.to_datetime(odd_cmb_df['startTime'],yearfirst=True)
odd_cmb_df['startTime'] = odd_cmb_df['startTime'] - datetime.timedelta(hours=8)

odd_cmb_df['datetime'] = pd.to_datetime(odd_cmb_df['datetime'],yearfirst=True)
odd_cmb_df['datetime'] = odd_cmb_df['datetime'] - datetime.timedelta(hours=8)
odd_cmb_df.sort_values('datetime',inplace=True)






from app.models import Match, Odd_1x2, Odd_Over_Under, Odd_AH, Odd_Goal
from app import app, db

for idx,row in match_df.iterrows():
    match = Match(start_time=row['startTime'],game=row['Match'], home_team=row['Home'], away_team=row['Away'],
          match_id=row['id'], type=row['type'], live_match=(row['LiveMatch']==1), odd_list=row['odd_list'])
    if (row.loc['externalStatisticsUrl'] is not None)and (row.loc['externalStatisticsUrl']!=''):
        match.external_stat_url=row['externalStatisticsUrl']
    if (row.loc['event_id'] is not None)and (row.loc['event_id']!=''):
        match.match_event_id=row['event_id']
    if (row.loc['url'] is not None)and (row.loc['url']!=''):
        match.match_url=row['url']
    if (row.loc['HT Result'] is not None)and (row.loc['HT Result']!=''):
        match.ht_result=row['HT Result']
    if (row.loc['FT Result'] is not None)and (row.loc['FT Result']!=''):
        match.ft_result=row['FT Result']
    if (row.loc['id_live'] is not None)and (row.loc['id_live']!=''):
        match.match_live_id=row['id_live']
    if (row.loc['url_live'] is not None)and (row.loc['url_live']!=''):
        match.match_live_url=row['url_live']
    db.session.add(match)
db.session.commit()

result_match_id = db.session.query(Match.match_id).all()
result_match_live_id = db.session.query(Match.match_live_id).all()

def find_id(id,isLive=0): # in db
    if isLive==1:
        return result_match_live_id.index((id,)) + 1 # need + 1 because db start from 1
    else:
        return result_match_id.index((id,)) + 1 # need + 1 because db start from 1

def is_valid(val):
    result = False
    try:
        if (val is not None):
            if type(val)==str:
                val = float(val)
            if (not math.isnan(val)):
                if (float(row[c])>0):
                    result = True
    except:
        result = False
    return result

odd_cmb_df = odd_cmb_df.fillna(float('nan'))
odd_cmb_df.replace('',0,inplace=True)
for idx,row in odd_cmb_df.iterrows():
    db_id = find_id(row['id'],int(row['isLive']))
    # 1x2
    d_1x2 = dict()
    for c in ['Home (1)','Draw (x)','Away (2)']:
        if (row[c] is not None):
            if not math.isnan(row[c]):
                d_1x2[c] = float(row[c])
    if len(d_1x2.keys())==3:
        odd = Odd_1x2(timestamp=row['datetime'],match_id=db_id, isLive=(row['isLive']==1), home=row['Home (1)'],draw=row['Draw (x)'],away=row['Away (2)'])
        db.session.add(odd)
        db.session.commit()
    d_ou = dict()
    d_ah = dict()
    d_goal = dict()
    for c in row.index:
        if 'Over' in c:
            if is_valid(row[c]):
                d_ou['val_o'] = float(c.split()[1])
                d_ou['over'] = float(row[c])             
        if 'Under' in c:
            if is_valid(row[c]):
                d_ou['val_u'] = float(c.split()[1])
                d_ou['under'] = float(row[c])
        if 'AH' in c:
            if is_valid(row[c]):
                if 'Home' == c.split()[1]:
                    d_ah['val_p'] = 0
                    d_ah['pos'] = float(row[c])
                elif 'Away' == c.split()[1]:
                    d_ah['val_n'] = 0
                    d_ah['neg'] = float(row[c])
                elif float(c.split()[1])>0:
                    d_ah['val_p'] = abs(float(c.split()[1]))
                    d_ah['pos'] = float(row[c])
                else:
                    d_ah['val_n'] = abs(float(c.split()[1]))
                    d_ah['neg'] = float(row[c])
        if '1/2' in c:
            if is_valid(row[c]):
                if float(c.split()[1])>0:
                    d_goal['val_p'] = abs(float(c.split()[1]))
                    d_goal['pos'] = float(row[c])
                else:
                    d_goal['val_n'] = abs(float(c.split()[1]))
                    d_goal['neg'] = float(row[c])
    # Over/Under
    if d_ou!={}:
        if d_ou['val_o']== d_ou['val_u']:
            odd = Odd_Over_Under(timestamp=row['datetime'],match_id=db_id, isLive=(row['isLive']==1), val = d_ou['val_o'], over=d_ou['over'], under=d_ou['under'])
            db.session.add(odd)
            db.session.commit()
    # AH
    if d_ah!={}:
        if d_ah['val_p']== d_ah['val_n']:
            odd = Odd_AH(timestamp=row['datetime'],match_id=db_id, isLive=(row['isLive']==1), val = d_ah['val_p'], pos=d_ah['pos'], neg=d_ah['neg'])
            db.session.add(odd)        
            db.session.commit()
    # Goal
    if d_goal!={}:
        if d_goal['val_p']== d_goal['val_n']:
            odd = Odd_Goal(timestamp=row['datetime'],match_id=db_id, isLive=(row['isLive']==1), val = d_goal['val_p'], pos=d_goal['pos'], neg=d_goal['neg'])
            db.session.add(odd)        
            db.session.commit()
