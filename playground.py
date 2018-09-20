# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 21:49:34 2018

@author: vietpham

"""
import pandas as pd
import sqlite3
import os


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
		print(c,v)
		for t in typ:
			if t in c:
				print('hi')
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
match_df = pd.read_sql_query("SELECT * FROM Match_info",con=conn,index_col='index')
match_id = match_df['id'].values.tolist()
df = match_df['id_live'].fillna(0)
match_id_live = df.unique().tolist()
match_id_live.remove(0)

odd_live_df = pd.DataFrame()
for tID in match_id_live:
    df = pd.read_sql_query("SELECT * FROM Odd_{}".format(tID),con=conn)

    odd_live_df = odd_live_df.append(df, ignore_index=True)

odd_live_df.sort_values('datetime',inplace=True)

odd_df = pd.DataFrame()
for tID in match_id:
    df = pd.read_sql_query("SELECT * FROM Odd_{}".format(tID),con=conn)
    odd_df = odd_df.append(df, ignore_index=True)

odd_df.sort_values('datetime',inplace=True)