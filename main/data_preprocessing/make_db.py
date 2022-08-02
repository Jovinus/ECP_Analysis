# %%
import os
import pandas as pd
import numpy as np

from glob import glob

pd.set_option("display.max_columns", None)


def split_data(input_x, option=0):
    
    if option != 0:
        option = 1
        
    splitted = input_x.split('/')
    
    try:
        return float(splitted[option])
    
    except (ValueError, IndexError):
        return np.nan
# %%
DATAPATH = "../../../dataset/raw_data"
DATAPATH2 = "../../../dataset/request"

df_dataset = pd.DataFrame()

for file_nm in glob(DATAPATH + '/DATA*.csv'):
    df_tmp = pd.read_csv(file_nm, encoding='cp949')
    df_dataset = pd.concat((df_dataset, df_tmp), axis=0)
    
df_cdw_id = pd.read_excel(os.path.join(DATAPATH, 'VO2peak_HPCID.xlsx'))
df_add_lab = pd.read_csv(os.path.join(DATAPATH, 'VO2max_chole_data.csv')).groupby(['환자번호#1', 'SM_DATE#2']).head(1)
df_add_crp = pd.read_csv(os.path.join(DATAPATH, 'VO2max_CRP_data.csv')).groupby(['환자번호#1', 'SM_DATE#2']).head(1)
df_add_death = pd.read_csv(os.path.join(DATAPATH, 'VO2max_Death.csv'))

df_add_cac = pd.read_csv(os.path.join(DATAPATH2, 'vo2max_cac.csv')).groupby(['환자번호#1', 'SM_DATE#2']).head(1)
df_add_carotid = pd.read_csv(os.path.join(DATAPATH2, 'vo2max_carotid.csv')).groupby(['환자번호#1', '건진일자#2']).head(1)
df_add_pwv_abi = pd.read_csv(os.path.join(DATAPATH2, 'vo2max_pwv_abi.csv')).groupby(['환자번호#1', '처방일자#4']).head(1)

# %%
df_add_carotid = df_add_carotid.assign(carotid = lambda x: (x['Carotid US CCA : IMT(Rt)#5'] + x['Carotid US CCA : IMT(Lt)#6']) / 2)


df_add_pwv_abi = df_add_pwv_abi.assign(
    left_value = lambda x: x['검사결과수치값#7'].apply(lambda y: split_data(y, option=0)),
    right_value = lambda x: x['검사결과수치값#7'].apply(lambda y: split_data(y, option=1)),
    mean_value = lambda x: (x['left_value'] + x['right_value'] )/ 2
)

df_add_pwv_abi = pd.pivot_table(values='mean_value', columns='검사명#6', index=['환자번호#1', '처방일자#4'], data=df_add_pwv_abi).reset_index()
df_add_pwv_abi.columns.name = None

# %%

df_dataset = pd.merge(df_dataset, df_cdw_id, how='left', on='HPCID')


df_dataset = pd.merge(
    df_dataset, df_add_lab, how='left', 
    left_on=['CDW_NO', 'SM_DATE'], right_on=["환자번호#1", "SM_DATE#2"]
).drop(columns=['환자번호#1', "SM_DATE#2", "EXEC_TIME#3"])

df_dataset = pd.merge(
    df_dataset, df_add_crp, how='left', 
    left_on=['CDW_NO', 'SM_DATE'], right_on=["환자번호#1", "SM_DATE#2"]
).drop(columns=['환자번호#1', "SM_DATE#2", "EXEC_TIME#3"])

df_dataset = pd.merge(
    df_dataset, df_add_cac, how='left', 
    left_on=['CDW_NO', 'SM_DATE'], right_on=["환자번호#1", "SM_DATE#2"]
).drop(columns=['환자번호#1', "SM_DATE#2", "VOLUME_SCORE#4"])

df_dataset = pd.merge(
    df_dataset, df_add_carotid[["환자번호#1", "건진일자#2", 'carotid']], how='left', 
    left_on=['CDW_NO', 'SM_DATE'], right_on=["환자번호#1", "건진일자#2"]
).drop(columns=['환자번호#1', "건진일자#2"])

df_dataset['SM_DATE'] = df_dataset['SM_DATE'].astype('datetime64')
df_add_pwv_abi['처방일자#4'] = df_add_pwv_abi['처방일자#4'].astype('datetime64')

df_dataset = pd.merge(
    df_dataset, df_add_pwv_abi, how='left', 
    left_on=['CDW_NO', 'SM_DATE'], right_on=["환자번호#1", "처방일자#4"]
).drop(columns=['환자번호#1', "처방일자#4"])

df_dataset = pd.merge(
    df_dataset, df_add_death, how='left', 
    left_on=['CDW_NO'], right_on=["환자번호#1"]
).drop(columns=['환자번호#1'])

# %%
df_dataset = df_dataset.rename(
    columns = {
        "CHOLESTEROL#4":"cholesterol", 
        'TG#5':"TG", 
        "CRP#4":"CRP", 
        "AJ_130_SCORE#3":"cac_score", 
        "ABI(Rt/Lt)":"abi", 
        "baPWV(Rt/Lt)":"baPWV", 
        "사망일#2":"death_date"
    }
)
# %%
df_dataset.to_csv("../../data/fitness_data.csv", index=False, encoding="utf-8")