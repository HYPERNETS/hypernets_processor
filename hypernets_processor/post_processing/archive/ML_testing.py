from random import Random

import xarray as xr
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    classification_report,
    recall_score,
    make_scorer,
)
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.feature_selection import SelectFromModel

import seaborn as sns
import matplotlib.pyplot as plt


windows_results_path = r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe"

linux_data_path = r"/mnt/t/data/insitu/hypernets/post_processing_qc"
windows_data_path = r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc"

outliers = pd.read_csv(
    r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\GHNA_2024_outliers.csv"
)
good_data = pd.read_csv(
    r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\GHNA_2024_good.csv"
)

outliers["is_outlier"] = "outlier"
good_data["is_outlier"] = "good"

data = pd.concat(([outliers, good_data]))
IDs = data["# id"]

data.drop(columns=data.columns[:6], axis=1, inplace=True)
data.drop(columns=["date", "time", " refl_550nm"], axis=1, inplace=True)

# X = data.drop('is_outlier', axis = 1)
X = data[[" sza", " vza", " saa", " vaa", "raa"]]
y = data["is_outlier"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=0.8, test_size=0.2, random_state=1
)
"""
def select_features(X_train, y_train, X_test, fs_model):
    fs = SelectFromModel(fs_model, max_features = 7)
    fs.fit(X_train, y_train)
    fs_model.fit(X_train, y_train)
    X_train_fs = fs.transform(X_train)
    X_test_fs = fs.transform(X_test)
    importances = fs_model.feature_importances_
    return X_train_fs, X_test_fs, fs, importances

fs_model = RandomForestClassifier(n_estimators = 100, max_depth = 10, random_state = 1)
X_train_fs, X_test_fs, fs, importances = select_features(X_train, y_train, X_test, fs_model)
"""

tree = DecisionTreeClassifier(max_depth=5, random_state=1, class_weight="balanced")
tree.fit(X_train, y_train)
y_pred = tree.predict(X_test)

##printing
# print paths
tree_rules = export_text(tree, feature_names=X.keys())
print(tree_rules)
print(classification_report(y_test, y_pred))

recall = make_scorer(recall_score, pos_label="outlier")
print(recall_score(y_test, y_pred, pos_label="outlier"))
print(cross_val_score(tree, X, y, scoring=recall))
##plotting
# use if using feature selection model for selected keys
# fs_features = [i for (i, v) in zip(X.keys(), np.array(fs.get_support())) if v]
"""
#plot tree
plt.figure(figsize = (100,10))
plot_tree(tree, filled = True, fontsize = 10, class_names = ['good', 'outlier'], feature_names = X.keys())
plt.show()

#plot confusion matrix
ax = plt.subplot()
conf = confusion_matrix(y_test, y_pred, labels = ['good', 'outlier'])
sns.heatmap(conf, annot = True, fmt = 'g', ax = ax)
ax.set_xlabel('Predicted Labels')
ax.set_ylabel('True Labels')
ax.set_title('Confusion Matrix')
ax.xaxis.set_ticklabels(['Good', 'Outlier'])
ax.yaxis.set_ticklabels(['Good', 'Outlier'])
plt.show()

#plot feature importance
plt.bar(X.keys(), tree.feature_importances_)
plt.xticks(rotation = 30, ha = 'right')
plt.tight_layout()
plt.show()
"""
