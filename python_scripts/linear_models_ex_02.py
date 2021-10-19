# coding: utf-8
# %% [markdown]
# # 📝 Exercise M4.02
#
# The goal of this exercise is to build an intuition on what will be the
# parameters' values of a linear model when the link between the data and the
# target is non-linear.
#
# First, we will generate such non-linear data.
#
# ```{tip}
# `np.random.RandomState` allows to create a random number generator which can
# be later used to get deterministic results.
# ```

# %%
import numpy as np
# Set the seed for reproduction
rng = np.random.RandomState(0)

# Generate data
n_sample = 100
data_max, data_min = 1.4, -1.4
len_data = (data_max - data_min)
data = rng.rand(n_sample) * len_data - len_data / 2
noise = rng.randn(n_sample) * .3
target = data ** 3 - 0.5 * data ** 2 + noise

# %% [markdown]
# ```{note}
# To ease the plotting, we will create a Pandas dataframe containing the data
# and target
# ```

# %%
import pandas as pd
full_data = pd.DataFrame({"data": data, "target": target})

# %%
import seaborn as sns

_ = sns.scatterplot(data=full_data, x="data", y="target", color="black",
                    alpha=0.5)

# %% [markdown]
# We observe that the link between the data `data` and vector `target` is
# non-linear. For instance, `data` could represent to be the years of
# experience (normalized) and `target` the salary (normalized). Therefore, the
# problem here would be to infer the salary given the years of experience.
#
# Using the function `f` defined below, find both the `weight` and the
# `intercept` that you think will lead to a good linear model. Plot both the
# data and the predictions of this model.

# %%
def f(data, weight=0, intercept=0):
    target_predict = weight * data + intercept
    return target_predict

# %%
# Write your code here.

# %% [markdown]
# Compute the mean squared error for this model

# %%
# Write your code here.

# %% [markdown]
# Train a linear regression model on this dataset.
#
# ```{warning}
# In scikit-learn, by convention `data` (also called `X` in the scikit-learn
# documentation) should be a 2D matrix of shape `(n_samples, n_features)`.
# If `data` is a 1D vector, you need to reshape it into a matrix with a
# single column if the vector represents a feature or a single row if the
# vector represents a sample.
# ```

# %%
from sklearn.linear_model import LinearRegression

# Write your code here.

# %% [markdown]
# Compute predictions from the linear regression model and plot both the data
# and the predictions.

# %%
# Write your code here.

# %% [markdown]
# Compute the mean squared error

# %%
# Write your code here.
