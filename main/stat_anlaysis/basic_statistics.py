# %%
import pandas as pd
import numpy as np
import statsmodels.api as sm

from patsy import dmatrices

pd.set_option("display.max_columns", None)
# %%
study_set = pd.read_csv("../../data/study_set.csv")

# %% Table 1
study_set.query("baPWV.notnull()").groupby(["ecp_quantile"])["baPWV_cut"].value_counts()
# %%
study_set.query("baPWV.notnull()").groupby(["ecp_quantile"])["baPWV_cut"].value_counts(normalize=True)
# %%
study_set.query("carotid.notnull()")["ecp_quantile"].value_counts(dropna=False)
# %%
study_set.query("carotid.notnull()")
# %%
