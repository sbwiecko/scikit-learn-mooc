# %% [markdown]
# # Hyperparameter tuning by grid-search
#
# In the previous notebook, we saw that hyperparameters can affect the
# statistical performance of a model. In this notebook, we will show how to
# optimize hyperparameters using a grid-search approach.

# %% [markdown]
# ## Our predictive model
#
# Let us reload the dataset as we did previously:

# %%
from sklearn import set_config

set_config(display="diagram")

# %%
import pandas as pd

adult_census = pd.read_csv("../datasets/adult-census.csv")

# %% [markdown]
# We extract the column containing the target.

# %%
target_name = "class"
target = adult_census[target_name]
target

# %% [markdown]
# We drop from our data the target and the `"education-num"` column which
# duplicates the information from the `"education"` column.

# %%
data = adult_census.drop(columns=[target_name, "education-num"])
data.head()

# %% [markdown]
# Once the dataset is loaded, we split it into a training and testing sets.

# %%
from sklearn.model_selection import train_test_split

data_train, data_test, target_train, target_test = train_test_split(
    data, target, random_state=42)

# %% [markdown]
# We will define a pipeline as seen in the first module. It will handle both
# numerical and categorical features.
#
# As we will use a tree-based model as a predictor, here we apply an ordinal
# encoder on the categorical features: it encodes every category with an
# arbitrary integer. For simple models such as linear models, a one-hot encoder
# should be preferred. But for complex models, in particular tree-based models,
# the ordinal encoder is useful as it avoids having high-dimensional
# representations.
#
# First we select all the categorical columns.

# %%
from sklearn.compose import make_column_selector as selector

categorical_columns_selector = selector(dtype_include=object)
categorical_columns = categorical_columns_selector(data)

# %% [markdown]
# Then we build our ordinal encoder, giving it the known categories.

# %%
from sklearn.preprocessing import OrdinalEncoder

categorical_preprocessor = OrdinalEncoder(handle_unknown="use_encoded_value",
                                          unknown_value=-1)

# %% [markdown]
# We now use a column transformer with code to select the categorical columns
# and apply to them the ordinal encoder.

# %%
from sklearn.compose import ColumnTransformer

preprocessor = ColumnTransformer([
    ('cat-preprocessor', categorical_preprocessor, categorical_columns)],
    remainder='passthrough', sparse_threshold=0)

# %% [markdown]
# Finally, we use a tree-based classifier (i.e. histogram gradient-boosting) to
# predict whether or not a person earns more than 50 k$ a year.

# %%
# for the moment this line is required to import HistGradientBoostingClassifier
from sklearn.experimental import enable_hist_gradient_boosting
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier",
     HistGradientBoostingClassifier(random_state=42, max_leaf_nodes=4))])
model

# %% [markdown]
# ## Tuning using a grid-search
#
# Instead of manually writing the two `for` loops, scikit-learn provides a
# class called `GridSearchCV` which implement the exhaustive search implemented
# during the exercise.
#
# Let see how to use the `GridSearchCV` estimator for doing such search.
# Since the grid-search will be costly, we will only explore the combination
# learning-rate and the maximum number of nodes.

# %%
# %%time
from sklearn.model_selection import GridSearchCV

param_grid = {
    'classifier__learning_rate': (0.05, 0.1, 0.5, 1, 5),
    'classifier__max_leaf_nodes': (3, 10, 30, 100)}
model_grid_search = GridSearchCV(model, param_grid=param_grid,
                                 n_jobs=2, cv=2)
model_grid_search.fit(data_train, target_train)

# %% [markdown]
# Finally, we will check the accuracy of our model using the test set.

# %%
accuracy = model_grid_search.score(data_test, target_test)
print(
    f"The test accuracy score of the grid-searched pipeline is: "
    f"{accuracy:.2f}"
)

# %% [markdown]
# ```{warning}
# Be aware that the evaluation should normally be performed in a
# cross-validation framework by providing `model_grid_search` as a model to
# the `cross_validate` function.
#
# Here, we are using a single train-test split to highlight the specificities
# of the `model_grid_search` instance. We will show such examples in the last
# section of this notebook.
# ```

# %% [markdown]
# The `GridSearchCV` estimator takes a `param_grid` parameter which defines
# all hyperparameters and their associated values. The grid-search will be in
# charge of creating all possible combinations and test them.
#
# The number of combinations will be equal to the product of the
# number of values to explore for each parameter (e.g. in our example 4 x 4
# combinations). Thus, adding new parameters with their associated values to be
# explored become rapidly computationally expensive.
#
# Once the grid-search is fitted, it can be used as any other predictor by
# calling `predict` and `predict_proba`. Internally, it will use the model with
# the best parameters found during `fit`.
#
# Get predictions for the 5 first samples using the estimator with the best
# parameters.

# %%
model_grid_search.predict(data_test.iloc[0:5])

# %% [markdown]
# You can know about these parameters by looking at the `best_params_`
# attribute.

# %%
print(f"The best set of parameters is: "
      f"{model_grid_search.best_params_}")

# %% [markdown]
# The accuracy and the best parameters of the grid-searched pipeline are
# similar to the ones we found in the previous exercise, where we searched the
# best parameters "by hand" through a double for loop.
#
# In addition, we can inspect all results which are stored in the attribute
# `cv_results_` of the grid-search. We will filter some specific columns
# from these results.

# %%
cv_results = pd.DataFrame(model_grid_search.cv_results_).sort_values(
    "mean_test_score", ascending=False)
cv_results.head()

# %% [markdown]
# Let us focus on the most interesting columns and shorten the parameter
# names to remove the `"param_classifier__"` prefix for readability:

# %%
# get the parameter names
column_results = [f"param_{name}" for name in param_grid.keys()]
column_results += [
    "mean_test_score", "std_test_score", "rank_test_score"]
cv_results = cv_results[column_results]


# %%
def shorten_param(param_name):
    if "__" in param_name:
        return param_name.rsplit("__", 1)[1]
    return param_name


cv_results = cv_results.rename(shorten_param, axis=1)
cv_results

# %% [markdown]
# With only 2 parameters, we might want to visualize the grid-search as a
# heatmap. We need to transform our `cv_results` into a dataframe where:
#
# - the rows will correspond to the learning-rate values;
# - the columns will correspond to the maximum number of leaf;
# - the content of the dataframe will be the mean test scores.

# %%
pivoted_cv_results = cv_results.pivot_table(
    values="mean_test_score", index=["learning_rate"],
    columns=["max_leaf_nodes"])

pivoted_cv_results

# %% [markdown]
# We can use a heatmap representation to show the above dataframe visually.

# %%
import seaborn as sns

ax = sns.heatmap(pivoted_cv_results, annot=True, cmap="YlGnBu", vmin=0.7,
                 vmax=0.9)
ax.invert_yaxis()

# %% [markdown]
# The above tables highlights the following things:
#
# * for too high values of `learning_rate`, the statistical performance of the
#   model is degraded and adjusting the value of `max_leaf_nodes` cannot fix
#   that problem;
# * outside of this pathological region, we observe that the optimal choice
#   of `max_leaf_nodes` depends on the value of `learning_rate`;
# * in particular, we observe a "diagonal" of good models with an accuracy
#   close to the maximal of 0.87: when the value of `max_leaf_nodes` is
#   increased, one should increase the value of `learning_rate` accordingly
#   to preserve a good accuracy.
#
# The precise meaning of those two parameters will be explained in a latter
# notebook.
#
# For now we will note that, in general, **there is no unique optimal parameter
# setting**: 6 models out of the 16 parameter configuration reach the maximal
# accuracy (up to small random fluctuations caused by the sampling of the
# training set).

# %% [markdown]
# In this notebook we have seen:
#
# * how to optimize the hyperparameters of a predictive model via a
#   grid-search;
# * that searching for more than two hyperparamters is too costly;
# * that a grid-search does not necessarily find an optimal solution.
