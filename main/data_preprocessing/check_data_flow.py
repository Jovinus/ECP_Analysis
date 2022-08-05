# %%
import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)

# %%
df_orig = pd.read_csv("../../data/fitness_data.csv")
# %%
print(len(df_orig['HPCID'].drop_duplicates()))

# %%
df_study_set = df_orig.query(
    "(rer >= 1.1) & (sex==1)", 
    engine='python')

print(len(df_study_set))


# %%
df_study_set = df_orig.query(
    "(rer >= 1.1) & (sex == 1) & (crf.notnull()) & (Stroke != 1) & (Angina !=1) & (MI !=1) & (Cancer != 1) & (Hepatatis != 1) & (cac_score.notnull() | carotid.notnull() | baPWV.notnull())", 
    engine='python'
)
print(len(df_study_set))

# %%
df_study_set = df_study_set.query("(baPWV != 6344.500000) & ~(SM3631 > 600) & ~(max_hr > 600) & ~(max_sbp > 300) & ~(crf > 30) & ~(carotid > 30)")
print(len(df_study_set))
# %%
