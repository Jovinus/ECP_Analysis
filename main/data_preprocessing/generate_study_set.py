# %%
import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)

# %%
df_orig = pd.read_csv("../../data/fitness_data.csv")

# %%
FEATURES = [
    'HPCID', 'SM_DATE', 'AGE', 'sex',  
    'SM0104', 'SM0101', 'SM0102', 'SM316001',
    'MVPA', 'SM3631', 'SM0111','CRP', 'cholesterol', 
    'TG', 'BL3118', 'max_hr', 'death_date', 'Diabetes', 
    'Hypertension', 'HTN_med', 'Hyperlipidemia', 
    'MED_HYPERLIPIDEMIA', 'ALC_YS', "SMK_YS", 
    'BL3142', 'BL314201', 'SM0600SBP', 'SM0600DBP', 
    "cac_score", "carotid", "abi", "baPWV", "max_sbp", "ecp", "crf", "vo2max"
]

columns_to_rename = {
    'SM0104':'percentage_fat', 
    'SM0101':'height', 
    'SM0102':'weight', 
    'SM316001':'bmi', 
    'SM3631':'rest_hr', 
    'SM0111':'muscle_mass', 
    'SM3140':'체지방량', 
    'SM3150':'체수분량', 
    'SM3170':'제지방량', 
    'BL3142':"hdl_c", 
    'BL314201':'ldl_c', 
    "SM0600SBP":"sbp", 
    "SM0600DBP":"dbp", 
    "BL3118":'glucose',
    "ALC_YS":"alcohol", 
    "SMK_YS":"smoke",
    "MED_HYPERLIPIDEMIA":"Hyperlipid_med",
    "AGE":"age",
}

# %%
df_study_set = df_orig.query(
    "(rer >= 1.1) & (crf.notnull()) & (Stroke != 1) & (Angina !=1) & (MI !=1) & (Cancer != 1) & (Hepatatis != 1) & (cac_score.notnull() | carotid.notnull() | baPWV.notnull())", 
    engine='python'
)[FEATURES].rename(columns=columns_to_rename).groupby(["HPCID"]).head(1).reset_index(drop=True)

df_study_set = df_study_set.assign(
    age = lambda x: x['age'].astype(int),
    carotid = lambda x: x['carotid'].astype(float),
    cac_score = lambda x: np.where(x['cac_score'] <= 0, 0, x['cac_score']).astype(float),
    baPWV = lambda x: x['baPWV'].astype(float),
)

# df_study_set.to_csv("../../data/study_set.csv", index=False)
# %%
def _make_age_adjusted_value(dataframe):
    
    dataframe = dataframe.assign(
        ecp_quantile = pd.qcut(dataframe['ecp'], q=4, labels=[0, 1, 2, 3]),
        max_sbp_binary = np.where(dataframe['max_sbp'] >= 210, 1, 0),
        crf_quantile = pd.qcut(dataframe['crf'], q=4, labels=[0, 1, 2, 3]),
        carotid_cut = np.where(dataframe['carotid'] > dataframe['carotid'].quantile(0.75), 1, 0),
        baPWV_cut = np.where(dataframe['baPWV'] > dataframe['baPWV'].quantile(0.75), 1, 0),
        cac_score_cut_0 = np.where(dataframe['cac_score'] > 0, 1, 0),
        cac_score_cut_10 = np.where(dataframe['cac_score'] > 10, 1, 0),
        cac_score_cut_100 = np.where(dataframe['cac_score'] > 100, 1, 0),
    )
    
    return dataframe

def get_age_adjusted_quantile(dataframe):
    
    df_age_under_30_male = _make_age_adjusted_value(dataframe.query("age < 30 & sex == 1"))
    # df_age_under_30_female = _make_age_adjusted_value(dataframe.query("age < 30 & sex == 0"))
    df_age_30_40_male = _make_age_adjusted_value(dataframe.query("age >= 30 & age < 40 & sex == 1"))
    df_age_30_40_female = _make_age_adjusted_value(dataframe.query("age >= 30 & age < 40 & sex == 0"))
    df_age_40_50_male = _make_age_adjusted_value(dataframe.query("age >= 40 & age < 50 & sex == 1"))
    df_age_40_50_female = _make_age_adjusted_value(dataframe.query("age >= 40 & age < 50 & sex == 0"))
    df_age_50_60_male = _make_age_adjusted_value(dataframe.query("age >= 50 & age < 60 & sex == 1"))
    df_age_50_60_female = _make_age_adjusted_value(dataframe.query("age >= 50 & age < 60 & sex == 0"))
    df_age_60_70_male = _make_age_adjusted_value(dataframe.query("age >= 60 & age < 70 & sex == 1"))
    df_age_60_70_female = _make_age_adjusted_value(dataframe.query("age >= 60 & age < 70 & sex == 0"))
    df_age_over_70_male = _make_age_adjusted_value(dataframe.query("age >= 70 & sex == 1"))
    df_age_over_70_female = _make_age_adjusted_value(dataframe.query("age >= 70 & sex == 0"))
    
    processed_dataframe = pd.concat(
        (
            df_age_under_30_male, df_age_30_40_male, df_age_40_50_male, 
            df_age_50_60_male, df_age_60_70_male, df_age_over_70_male, 
            # df_age_under_30_female, 
            df_age_30_40_female, df_age_40_50_female, 
            df_age_50_60_female, df_age_60_70_female, df_age_over_70_female,
        ), axis=0
    ).reset_index(drop=True)
    
    return processed_dataframe
# %%
df_study_set = get_age_adjusted_quantile(df_study_set)

df_study_set = df_study_set.query("(baPWV != 6344.500000) & ~(rest_hr > 600) & ~(max_hr > 600) & ~(max_sbp > 300) & ~(crf > 30) & ~(carotid > 30)")
# %%
df_study_set.to_csv("../../data/study_set.csv", index=False)
# %%
