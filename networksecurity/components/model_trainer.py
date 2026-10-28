from networksecurity.utils.main_utils.utils import (
    evalute_model,
    evaluate_models,
    load_numpy_array,
    load_object,
    save_object,
    save_numpy_array,
)
import os, sys
from networksecurity.constant import training_pipeline
from networksecurity.entity.artifact_entity import (
    ModelTrainerArtifact,
    ClassificationMetricArtifact,
    DataTransformationArtifact,
)
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.constant.training_pipeline import TARGET_COLUMN
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecurity.logging.logger import logger
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
import numpy as np
import pandas as pd 
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
import mlflow

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_mlflow(
        self,
        best_model,
        classificationmetric=None,
        best_model_name: str = None,
        best_model_score: float = None,
        train_metric=None,
        test_metric=None,
        model_report: dict = None,
    ):
        try:
            # Set tracking URI and experiment name so MLflow UI connects to the same database
            mlflow.set_tracking_uri("sqlite:///mlflow.db")
            mlflow.set_experiment("NetworkSecurity")

            with mlflow.start_run():
                # 1. Log best model name
                if best_model_name:
                    mlflow.set_tag("best_model_name", best_model_name)
                    mlflow.log_param("best_model_name", best_model_name)

                # 2. Log model hyperparameters
                try:
                    for param_name, param_val in best_model.get_params().items():
                        if isinstance(param_val, (int, float, str, bool)) or param_val is None:
                            mlflow.log_param(param_name, param_val)
                except Exception:
                    pass

                # 3. Log model score
                if best_model_score is not None:
                    mlflow.log_metric("best_model_score", float(best_model_score))

                # 4. Log comparison scores for all tested models
                if model_report:
                    for m_name, m_score in model_report.items():
                        clean_name = m_name.replace(" ", "_").lower()
                        mlflow.log_metric(f"model_score_{clean_name}", float(m_score))

                # 5. Log Train Metrics
                if train_metric is not None:
                    mlflow.log_metric("train_f1_score", float(train_metric.f1_score))
                    mlflow.log_metric("train_precision_score", float(train_metric.precision_score))
                    mlflow.log_metric("train_recall_score", float(train_metric.recall_score))

                # 6. Log Test Metrics (or single metric if passed as classificationmetric)
                target_metric = test_metric if test_metric is not None else classificationmetric
                if target_metric is not None:
                    mlflow.log_metric("test_f1_score", float(target_metric.f1_score))
                    mlflow.log_metric("test_precision_score", float(target_metric.precision_score))
                    mlflow.log_metric("test_recall_score", float(target_metric.recall_score))

                    # Standard metric names for quick view
                    mlflow.log_metric("f1_score", float(target_metric.f1_score))
                    mlflow.log_metric("precision", float(target_metric.precision_score))
                    mlflow.log_metric("recall", float(target_metric.recall_score))

                # 7. Log model artifact
                mlflow.sklearn.log_model(best_model, "model")

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

    def train_model(self, x_train, y_train, x_test, y_test):
        try:
            models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
            }

            params = {
                "Decision Tree": {
                    'criterion': ['gini', 'entropy', 'log_loss'],
                },
                "Random Forest": {
                    'n_estimators': [8, 16, 32, 128, 256]
                },
                "Gradient Boosting": {
                    'learning_rate': [.1, .01, .05, .001],
                    'subsample': [0.6, 0.7, 0.75, 0.85, 0.9],
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                },
                "Logistic Regression": {},
                "AdaBoost": {
                    'learning_rate': [.1, .01, .001],
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                }
            }

            model_report: dict = evaluate_models(
                x_train=x_train,
                y_train=y_train,
                x_test=x_test,
                y_test=y_test,
                models=models,
                param=params,
            )
            
            best_model_score = max(sorted(model_report.values()))
            best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]
            logger.info(f"Best model name is : {best_model_name} with score: {best_model_score}")

            best_model = models[best_model_name]

            y_train_pred = best_model.predict(x_train)
            classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)

            y_test_pred = best_model.predict(x_test)
            classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)

            # Track all model parameters, comparison scores, train & test metrics in MLflow
            self.track_mlflow(
                best_model=best_model,
                best_model_name=best_model_name,
                best_model_score=best_model_score,
                train_metric=classification_train_metric,
                test_metric=classification_test_metric,
                model_report=model_report,
            )

            
            preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)
            network_model = NetworkModel(preprocessor=preprocessor, model=best_model)
            save_object(self.model_trainer_config.trained_model_file_path, obj=network_model)

            # Also save final model
            os.makedirs("final_model", exist_ok=True)
            save_object("final_model/model.pkl", best_model)

            # Model trained Artifact
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric,
            )
            logger.info(f"Model trained successfully. Artifact: {model_trainer_artifact}")
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_model_training(self) -> ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            # loading training array and testing array
            train_arr = load_numpy_array(train_file_path)
            test_arr = load_numpy_array(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )
            logger.info("separated x_train,y_train,x_test,y_test")

            model_train_artifact = self.train_model(x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test)
            return model_train_artifact           
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # Alias for method name consistency
    initiate_model_trainer = initiate_model_training

            
        