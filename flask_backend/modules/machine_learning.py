import pandas as pd
import numpy as np
import joblib
import uuid
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

class MachineLearningService:
    def __init__(self):
        self.models = {
            'LinearRegression': {
                'name': '线性回归(LR)',
                'class': LinearRegression,
                'params': {
                    'fit_intercept': [True, False],
                    'normalize': [True, False]
                }
            },
            'RandomForest': {
                'name': '随机森林(RF)',
                'class': RandomForestRegressor,
                'params': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 10, 20, 30],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
            },
            'GradientBoosting': {
                'name': 'GBR模型',
                'class': GradientBoostingRegressor,
                'params': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9, 1.0]
                }
            },
            'XGBoost': {
                'name': 'XGBR模型',
                'class': xgb.XGBRegressor,
                'params': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9, 1.0]
                }
            },
            'SVR': {
                'name': '支持向量机(SVR)',
                'class': SVR,
                'params': {
                    'C': [0.1, 1, 10, 100],
                    'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
                    'kernel': ['rbf', 'linear', 'poly']
                }
            },
            'MLP': {
                'name': '人工神经网络(ANN)',
                'class': MLPRegressor,
                'params': {
                    'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)],
                    'activation': ['relu', 'tanh', 'logistic'],
                    'alpha': [0.0001, 0.001, 0.01],
                    'learning_rate': ['constant', 'adaptive']
                }
            }
        }
    
    def get_available_models(self):
        """Get list of available ML models"""
        return {
            'success': True,
            'models': [
                {
                    'key': key,
                    'name': info['name'],
                    'params': list(info['params'].keys())
                }
                for key, info in self.models.items()
            ]
        }
    
    def train_model(self, train_data, params):
        """Train a machine learning model"""
        try:
            model_type = params.get('model_type')
            if model_type not in self.models:
                return {'success': False, 'message': f'不支持的模型类型: {model_type}'}
            
            # Prepare data
            target_columns = params.get('target_columns', train_data.columns[-3:].tolist())
            feature_columns = [col for col in train_data.columns if col not in target_columns]
            
            X = train_data[feature_columns]
            y = train_data[target_columns]
            
            # Split data for validation
            test_size = params.get('test_size', 0.2)
            random_state = params.get('random_state', 42)
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # Initialize model
            model_info = self.models[model_type]
            model_params = params.get('model_params', {})
            
            # Handle different target scenarios
            if len(target_columns) == 1:
                # Single target
                y_train_single = y_train.iloc[:, 0]
                y_val_single = y_val.iloc[:, 0]
                
                if params.get('use_grid_search', False):
                    # Grid search for hyperparameter tuning
                    grid_params = self._get_grid_search_params(model_type, model_params)
                    model = GridSearchCV(
                        model_info['class'](),
                        grid_params,
                        cv=5,
                        scoring='neg_mean_squared_error',
                        n_jobs=-1
                    )
                    model.fit(X_train, y_train_single)
                    best_model = model.best_estimator_
                    best_params = model.best_params_
                else:
                    # Direct training with provided params
                    model = model_info['class'](**model_params)
                    model.fit(X_train, y_train_single)
                    best_model = model
                    best_params = model_params
                
                # Predictions
                y_train_pred = best_model.predict(X_train)
                y_val_pred = best_model.predict(X_val)
                
                # Metrics
                train_metrics = self._calculate_metrics(y_train_single, y_train_pred)
                val_metrics = self._calculate_metrics(y_val_single, y_val_pred)
                
            else:
                # Multiple targets - train separate models for each target
                models = {}
                train_metrics = {}
                val_metrics = {}
                
                for i, target_col in enumerate(target_columns):
                    y_train_single = y_train.iloc[:, i]
                    y_val_single = y_val.iloc[:, i]
                    
                    if params.get('use_grid_search', False):
                        grid_params = self._get_grid_search_params(model_type, model_params)
                        model = GridSearchCV(
                            model_info['class'](),
                            grid_params,
                            cv=5,
                            scoring='neg_mean_squared_error',
                            n_jobs=-1
                        )
                        model.fit(X_train, y_train_single)
                        models[target_col] = model.best_estimator_
                    else:
                        model = model_info['class'](**model_params)
                        model.fit(X_train, y_train_single)
                        models[target_col] = model
                    
                    # Predictions for this target
                    y_train_pred = models[target_col].predict(X_train)
                    y_val_pred = models[target_col].predict(X_val)
                    
                    # Metrics for this target
                    train_metrics[target_col] = self._calculate_metrics(y_train_single, y_train_pred)
                    val_metrics[target_col] = self._calculate_metrics(y_val_single, y_val_pred)
                
                best_model = models
                best_params = model_params
            
            # Cross-validation score
            cv_scores = []
            for target_col in target_columns:
                if len(target_columns) == 1:
                    cv_score = cross_val_score(
                        best_model, X, y.iloc[:, 0], cv=5, scoring='neg_mean_squared_error'
                    )
                else:
                    cv_score = cross_val_score(
                        best_model[target_col], X, y[target_col], cv=5, scoring='neg_mean_squared_error'
                    )
                cv_scores.append(-cv_score.mean())
            
            # Generate unique model ID
            model_id = str(uuid.uuid4())
            
            # Prepare model info for storage
            model_info_storage = {
                'model': best_model,
                'model_type': model_type,
                'model_name': model_info['name'],
                'feature_columns': feature_columns,
                'target_columns': target_columns,
                'params': best_params,
                'training_time': datetime.now().isoformat(),
                'data_shape': train_data.shape
            }
            
            result = {
                'success': True,
                'message': f'{model_info["name"]} 训练完成',
                'model_id': model_id,
                'model': model_info_storage,
                'metrics': {
                    'train': train_metrics,
                    'validation': val_metrics,
                    'cross_validation': {
                        target_columns[i]: cv_scores[i] for i in range(len(target_columns))
                    }
                },
                'feature_columns': feature_columns,
                'target_columns': target_columns,
                'best_params': best_params
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'message': f'模型训练失败: {str(e)}'}
    
    def predict(self, model_info, test_data, params):
        """Make predictions with trained model"""
        try:
            model = model_info['model']
            feature_columns = model_info['feature_columns']
            target_columns = model_info['target_columns']
            
            # Prepare test data
            X_test = test_data[feature_columns]
            
            # Make predictions
            if len(target_columns) == 1:
                # Single target
                predictions = model.predict(X_test)
                predictions_df = pd.DataFrame(
                    predictions,
                    columns=[f'{target_columns[0]}_predicted']
                )
            else:
                # Multiple targets
                predictions_dict = {}
                for target_col in target_columns:
                    pred = model[target_col].predict(X_test)
                    predictions_dict[f'{target_col}_predicted'] = pred
                
                predictions_df = pd.DataFrame(predictions_dict)
            
            # Combine with original test data if requested
            if params.get('include_features', False):
                result_df = pd.concat([test_data.reset_index(drop=True), predictions_df], axis=1)
            else:
                result_df = predictions_df
            
            return {
                'success': True,
                'message': '预测完成',
                'predictions': result_df.to_dict('records'),
                'predictions_df': predictions_df,
                'shape': predictions_df.shape
            }
            
        except Exception as e:
            return {'success': False, 'message': f'预测失败: {str(e)}'}
    
    def evaluate_model(self, model_info, test_data, params):
        """Evaluate model performance"""
        try:
            model = model_info['model']
            feature_columns = model_info['feature_columns']
            target_columns = model_info['target_columns']
            
            # Prepare test data
            X_test = test_data[feature_columns]
            y_test = test_data[target_columns]
            
            # Make predictions
            if len(target_columns) == 1:
                # Single target
                y_pred = model.predict(X_test)
                metrics = self._calculate_metrics(y_test.iloc[:, 0], y_pred)
                
                evaluation_result = {
                    target_columns[0]: metrics
                }
            else:
                # Multiple targets
                evaluation_result = {}
                for target_col in target_columns:
                    y_pred = model[target_col].predict(X_test)
                    metrics = self._calculate_metrics(y_test[target_col], y_pred)
                    evaluation_result[target_col] = metrics
            
            return {
                'success': True,
                'message': '模型评估完成',
                'evaluation': evaluation_result,
                'model_info': {
                    'model_type': model_info['model_type'],
                    'model_name': model_info['model_name'],
                    'training_time': model_info['training_time'],
                    'feature_count': len(feature_columns),
                    'target_count': len(target_columns)
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'模型评估失败: {str(e)}'}
    
    def save_model(self, model_info, file_path):
        """Save trained model to file"""
        try:
            joblib.dump(model_info, file_path)
            return {'success': True, 'message': f'模型已保存到 {file_path}'}
        except Exception as e:
            return {'success': False, 'message': f'保存模型失败: {str(e)}'}
    
    def load_model(self, file_path):
        """Load trained model from file"""
        try:
            model_info = joblib.load(file_path)
            return {'success': True, 'model': model_info, 'message': f'模型已从 {file_path} 加载'}
        except Exception as e:
            return {'success': False, 'message': f'加载模型失败: {str(e)}'}
    
    def _calculate_metrics(self, y_true, y_pred):
        """Calculate regression metrics"""
        return {
            'mse': float(mean_squared_error(y_true, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_true, y_pred))),
            'mae': float(mean_absolute_error(y_true, y_pred)),
            'r2': float(r2_score(y_true, y_pred))
        }
    
    def _get_grid_search_params(self, model_type, user_params):
        """Get parameters for grid search"""
        default_params = self.models[model_type]['params'].copy()
        
        # Override with user-provided params
        for key, value in user_params.items():
            if key in default_params:
                if isinstance(value, list):
                    default_params[key] = value
                else:
                    default_params[key] = [value]
        
        return default_params 