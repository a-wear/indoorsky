import numpy as np
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.metrics import confusion_matrix


class Position_KNN():
    def __init__(self, k=1, metric='euclidean', weight='distance'):
        self.classifier_building = None
        self.classifier_floor = None
        self.regressor = None
        self.y_train = None
        self.k = k
        self.metric = metric
        self.weight = weight

    def fit(self, X_train=None, y_train=None):
        self.y_train = y_train
        self.regressor = KNeighborsRegressor(n_neighbors=self.k, metric=self.metric, weights=self.weight)
        self.classifier_building = KNeighborsClassifier(n_neighbors=self.k, metric=self.metric, weights=self.weight)
        self.classifier_floor = KNeighborsClassifier(n_neighbors=self.k, metric=self.metric, weights=self.weight)
        self.regressor.fit(X_train, y_train[:, 0:3])
        self.classifier_floor .fit(X_train, y_train[:, 3])
        self.classifier_building.fit(X_train, y_train[:, 4])

    def predict_position_2D(self, X_test=None, y_test=None, **kwargs):
        for key, value in kwargs.items():
            if key == 'true_floors':
                consider_true_floor = True
                true_false_values = value
            else:
                consider_true_floor = False
                
        prediction_2D = self.regressor.predict(X_test)
        euclidean_distance = np.linalg.norm(prediction_2D[:, 0:2] - y_test[:, 0:2], axis=1)
        
        if consider_true_floor == True:
            mask = (true_false_values[:, 0] == 0)
            selected_errors = euclidean_distance[mask]
            mean_error = np.mean(selected_errors)
        else:
            mean_error = np.mean(euclidean_distance)
            
        return mean_error, selected_errors

    def predict_position_3D(self, X_test=None, y_test=None):
        prediction_3D = self.regressor.predict(X_test)
        error = np.linalg.norm(prediction_3D[:, 0:3] - y_test[:, 0:3], axis=1)
        mean_error = np.mean(error)
        return mean_error, error

    def floor_hit_rate(self, X_test=None, y_test=None):
        prediction_floor = self.classifier_floor.predict(X_test)
        cm_floor = confusion_matrix(y_true=y_test[:, 3], y_pred=prediction_floor)
        accuracy = (np.trace(cm_floor) / float(np.sum(cm_floor))) * 100
        subs = np.abs(np.array(prediction_floor, ndmin=2).T - np.array(y_test[:, 3], ndmin=2).T)
        true_false_values = np.array(subs, ndmin=2)
        return accuracy, true_false_values, prediction_floor

    def building_hit_rate(self, X_test=None, y_test=None):
        prediction_building = self.classifier_building.predict(X_test)
        cm_building = confusion_matrix(y_true=y_test[:, 4], y_pred=prediction_building)
        accuracy = (np.trace(cm_building) / float(np.sum(cm_building))) * 100
        return accuracy, prediction_building
