import pandas as pd
import numpy as np
from IPython.display import display

#### Extract feature from self-reported physical exercise queation -> MVPA(yes/no)
def is_MVPA(df):
    ## epidemiology version
    df['OVERALL_PHYSICAL_ACTIVITY'] = np.where(df['OVERALL_PHYSICAL_ACTIVITY'].isnull()|df['OVERALL_PHYSICAL_ACTIVITY'].isin([9999]), 0, df['OVERALL_PHYSICAL_ACTIVITY'])
    df['PHY_DURATION'] = np.where(df['PHY_DURATION'].isnull()|df['PHY_DURATION'].isin([9999]), 0 ,df['PHY_DURATION'])
    df['PHY_FREQ'] = np.where(df['PHY_FREQ'].isnull()|df['PHY_FREQ'].isin([9999]), 0, df['PHY_FREQ'])

    dur_mapper = {0:0, 1:10, 2:30, 3:50, 4:60}
    df['tmp_phy_duration'] = df['PHY_DURATION'].map(dur_mapper)

    freq_mapper = {0:0, 1:1.5, 2:3.5, 3:6}
    df['tmp_phy_freq'] = df['PHY_FREQ'].map(freq_mapper)

    df['tmp_phy_act'] = df['tmp_phy_freq'] * df['tmp_phy_duration']
    
    df['tmp_act_mets'] = df['OVERALL_PHYSICAL_ACTIVITY'].map({0:0, 1:3.3, 1:4, 2:8})
    df['METs_week'] =  df['tmp_act_mets'] * df['tmp_phy_act']
    df['METs_week'] = np.where(df['METs_week'].isnull(), 0, df['METs_week'])
    

    #### Define MVPA(yes = 1/no = 0)
    df['MVPA'] = np.where(df['OVERALL_PHYSICAL_ACTIVITY'].isin([1, 2]) & (df['tmp_phy_act'] >= 150), 1, 0)

    display(df['MVPA'].value_counts(dropna=False))
    
    return df.drop(columns=['tmp_phy_duration', 'tmp_phy_freq', 'tmp_phy_act', 'tmp_act_mets'])

#### Define disease to exclude
def have_disease(df):

    print("\nInitial n: ", len(set(df["HPCID"])))

    #### Diabetes
    df['Diabetes'] = np.where((df['BL3118'] >= 126) | (df['BL3164'] >= 6.5) | (df['MED_DIABETES'] == 1) | (df['TRT_DIABETES'] == 0) | (df['TRT_MED_DIABETES'] == 1), 1, 0)
    print("\nDiabetes: n = ", len(set(df[df["Diabetes"] == 1]["HPCID"])))
    
    #### Hypertension
    df['Hypertension'] = np.where((df['SM0600SBP'] >= 140) | (df['SM0600DBP'] >= 90) | (df['HISTORY_HYPERTENSION'] == 1) | (df['TRT_HYPERTENSION'].isin([0, 1])) , 1, 0)
    df['HTN_med'] = np.where((df['Hypertension'] == 1) & (df['MED_HYPERTENSION'] == 1), 1, 0)
    print("\nHypertension: n = ", len(set(df[df["Hypertension"] == 1]["HPCID"])))
    
    #### Hyperlipidemia
    df['Hyperlipidemia'] = np.where((df['BL314201'] > 130) | (df['BL3142'] < 40) | (df['MED_HYPERLIPIDEMIA'] == 1) | (df['TRT_MED_HYPERLIPIDEMIA'].isin([0, 1])), 1, 0)
    print("\nHyperlipidemia: n = ", len(set(df[df["Hyperlipidemia"] == 1]["HPCID"])))
    
    #### Hepatatis
    df['Hepatatis'] = np.where((df['BL5111'] > 0.5) | (df['BL5115'] >= 0.5), 1, 0)
    print("\nHepatatis: n = ", len(set(df[df["Hepatatis"] == 1]["HPCID"])))

    #####################################Roughly Defined Chronic Disease#################################
    
    #### Stroke
    df['Stroke'] = df[['HISTORY_STROKE', 'TRT_STROKE', 'STATUS_STROKE', 'TRT_STROKE_OP']].any(axis=1, skipna=True) * 1
    display(df['Stroke'].value_counts())
    print("\nStroke: n = ",len(set(df[df['Stroke'] == 1]["HPCID"])))
    
    #### Angina
    df['Angina'] = df[['HISTORY_ANGINA', 'TRT_ANGINA', 'STATUS_ANGINA', 'TRT_ANGINA_OP']].any(axis=1, skipna=True) * 1
    display(df['Angina'].value_counts())
    print("\nAngina: n = ",len(set(df[df["Angina"] == 1]["HPCID"])))
    
    #### MI
    df['MI'] = df[['HISTORY_MI', 'TRT_MI', 'STATUS_MI', 'TRT_MI_OP']].any(axis=1, skipna=True) * 1
    display(df["MI"].value_counts())
    print("\nMyocardiac Infraction: n = ", len(set(df[df['MI'] == 1]["HPCID"])))
    
    #### Asthma
    df['Asthma'] = df[['HISTORY_ASTHMA']].any(axis=1, skipna=True) * 1
    print("\nAsthma: n = ",len(set(df[df["Asthma"] == 1]["HPCID"])))
    
    #### Cancer
    df['Cancer'] = df.loc[:, "HISTORY_CANCER": "TRT_CANCER_OTHER_OT"].any(axis=1, skipna=True)*1
    print("\nExclude_cancer n: ", len(set(df[df["Cancer"] == 1]["HPCID"])))
    
    return df