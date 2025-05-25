import pandas as pd
import numpy as np
import uuid
from datetime import datetime
from sklearn.ensemble import StackingRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

class StackingEnsembleService:
    def __init__(self):
        # 与机器学习服务保持一致的模型配置
        self.base_models = {
            'LinearRegression': {
                'name': '线性回归(LR)',
                'model': LinearRegression()
            },
            'RandomForest': {
                'name': '随机森林(RF)',
                'model': RandomForestRegressor(n_estimators=100, random_state=42)
            },
            'GradientBoosting': {
                'name': 'GBR模型',
                'model': GradientBoostingRegressor(n_estimators=100, random_state=42)
            },
            'XGBoost': {
                'name': 'XGBR模型',
                'model': xgb.XGBRegressor(n_estimators=100, random_state=42)
            },
            'SVR': {
                'name': '支持向量机(SVR)',
                'model': SVR(C=1.0, kernel='rbf')
            },
            'MLP': {
                'name': '人工神经网络(ANN)',
                'model': MLPRegressor(hidden_layer_sizes=(100,), random_state=42, max_iter=500)
            }
        }
        
        # 元学习器选项
        self.meta_models = {
            'LinearRegression': {
                'name': '线性回归',
                'model': LinearRegression()
            },
            'RandomForest': {
                'name': '随机森林',
                'model': RandomForestRegressor(n_estimators=50, random_state=42)
            },
            'GradientBoosting': {
                'name': 'GBR模型',
                'model': GradientBoostingRegressor(n_estimators=50, random_state=42)
            },
            'XGBoost': {
                'name': 'XGBR模型',
                'model': xgb.XGBRegressor(n_estimators=50, random_state=42)
            },
            'SVR': {
                'name': '支持向量机',
                'model': SVR(C=1.0, kernel='rbf')
            },
            'MLP': {
                'name': '人工神经网络',
                'model': MLPRegressor(hidden_layer_sizes=(50,), random_state=42, max_iter=300)
            }
        }
    
    def get_available_models(self):
        """获取可用的基学习器和元学习器"""
        return {
            'success': True,
            'base_models': [
                {
                    'key': key,
                    'name': info['name']
                }
                for key, info in self.base_models.items()
            ],
            'meta_models': [
                {
                    'key': key,
                    'name': info['name']
                }
                for key, info in self.meta_models.items()
            ]
        }
    
    def train_stacking_ensemble(self, train_data, params):
        """Train stacking ensemble model"""
        try:
            # Prepare data
            target_columns = params.get('target_columns', train_data.columns[-3:].tolist())
            feature_columns = [col for col in train_data.columns if col not in target_columns]
            
            X = train_data[feature_columns]
            y = train_data[target_columns]
            
            # Configuration parameters
            cv_folds = params.get('cv_folds', 5)
            meta_model_type = params.get('meta_model', 'LinearRegression')
            selected_base_models = params.get('base_models', ['rf', 'gbr', 'lr'])
            
            # Select base models
            base_estimators = [
                (name, self.base_models[name]['model']) for name in selected_base_models 
                if name in self.base_models
            ]
            
            # Meta model
            if meta_model_type in self.meta_models:
                meta_model = self.meta_models[meta_model_type]['model']
            else:
                meta_model = self.meta_models['LinearRegression']['model']
            
            results = {}
            models = {}
            
            # Train stacking model for each target
            for target_col in target_columns:
                y_target = y[target_col] if len(target_columns) > 1 else y.iloc[:, 0]
                
                # Create stacking regressor
                stacking_model = StackingRegressor(
                    estimators=base_estimators,
                    final_estimator=meta_model,
                    cv=cv_folds,
                    n_jobs=-1
                )
                
                # Train the model
                stacking_model.fit(X, y_target)
                models[target_col] = stacking_model
                
                # Cross-validation evaluation
                cv_scores = cross_val_score(
                    stacking_model, X, y_target, 
                    cv=cv_folds, scoring='neg_mean_squared_error'
                )
                
                # Get predictions for training data
                y_pred = stacking_model.predict(X)
                
                # Calculate metrics
                metrics = {
                    'mse': float(mean_squared_error(y_target, y_pred)),
                    'rmse': float(np.sqrt(mean_squared_error(y_target, y_pred))),
                    'mae': float(mean_absolute_error(y_target, y_pred)),
                    'r2': float(r2_score(y_target, y_pred)),
                    'cv_score': float(-cv_scores.mean()),
                    'cv_std': float(cv_scores.std())
                }
                
                results[target_col] = metrics
            
            # Generate unique model ID
            model_id = str(uuid.uuid4())
            
            # Prepare model info for storage (包含模型对象，用于app_state存储)
            model_info_storage = {
                'model': models if len(target_columns) > 1 else models[target_columns[0]],
                'model_type': 'StackingEnsemble',
                'model_name': 'Stacking集成模型',
                'feature_columns': feature_columns,
                'target_columns': target_columns,
                'base_models': selected_base_models,
                'meta_model': meta_model_type,
                'cv_folds': cv_folds,
                'training_time': datetime.now().isoformat(),
                'data_shape': list(train_data.shape)
            }
            
            # 准备JSON可序列化的响应结果
            return {
                'success': True,
                'message': 'Stacking集成模型训练完成',
                'model_id': model_id,
                'model': model_info_storage,  # 这个会在app.py中被移除
                'model_info': {
                    'model_type': 'StackingEnsemble',
                    'model_name': 'Stacking集成模型',
                    'feature_columns': feature_columns,
                    'target_columns': target_columns,
                    'base_models': selected_base_models,
                    'meta_model': meta_model_type,
                    'cv_folds': cv_folds,
                    'training_time': datetime.now().isoformat(),
                    'data_shape': list(train_data.shape)
                },
                'metrics': results,
                'feature_columns': feature_columns,
                'target_columns': target_columns
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Stacking模型训练失败: {str(e)}'}
    
    def get_base_model_predictions(self, train_data, params):
        """Get individual base model predictions for analysis"""
        try:
            target_columns = params.get('target_columns', train_data.columns[-3:].tolist())
            feature_columns = [col for col in train_data.columns if col not in target_columns]
            
            X = train_data[feature_columns]
            y = train_data[target_columns]
            
            cv_folds = params.get('cv_folds', 5)
            kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
            
            results = {}
            
            for target_col in target_columns:
                y_target = y[target_col] if len(target_columns) > 1 else y.iloc[:, 0]
                target_results = {}
                
                for model_name, model_info in self.base_models.items():
                    cv_predictions = np.zeros(len(X))
                    cv_scores = []
                    
                    for train_idx, val_idx in kf.split(X):
                        X_train_cv, X_val_cv = X.iloc[train_idx], X.iloc[val_idx]
                        y_train_cv, y_val_cv = y_target.iloc[train_idx], y_target.iloc[val_idx]
                        
                        # Train model on CV fold
                        model = model_info['model']
                        model_copy = type(model)(**model.get_params())
                        model_copy.fit(X_train_cv, y_train_cv)
                        
                        # Predict on validation set
                        val_pred = model_copy.predict(X_val_cv)
                        cv_predictions[val_idx] = val_pred
                        
                        # Calculate fold score
                        fold_score = r2_score(y_val_cv, val_pred)
                        cv_scores.append(fold_score)
                    
                    # Calculate overall metrics
                    metrics = {
                        'r2': float(r2_score(y_target, cv_predictions)),
                        'mse': float(mean_squared_error(y_target, cv_predictions)),
                        'rmse': float(np.sqrt(mean_squared_error(y_target, cv_predictions))),
                        'mae': float(mean_absolute_error(y_target, cv_predictions)),
                        'cv_mean': float(np.mean(cv_scores)),
                        'cv_std': float(np.std(cv_scores))
                    }
                    
                    target_results[model_name] = {
                        'metrics': metrics,
                        'predictions': cv_predictions.tolist()
                    }
                
                results[target_col] = target_results
            
            return {
                'success': True,
                'message': '基模型预测分析完成',
                'results': results
            }
            
        except Exception as e:
            return {'success': False, 'message': f'基模型分析失败: {str(e)}'} 