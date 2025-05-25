import pandas as pd
import numpy as np
import uuid
from datetime import datetime
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

class AutoMLService:
    def __init__(self):
        # 快速模式配置（参数较少）
        self.fast_models_config = {
            'LinearRegression': {
                'model': LinearRegression,
                'params': {
                    'fit_intercept': [True]
                }
            },
            'RandomForest': {
                'model': RandomForestRegressor,
                'params': {
                    'n_estimators': [50],
                    'max_depth': [10]
                }
            },
            'GradientBoosting': {
                'model': GradientBoostingRegressor,
                'params': {
                    'n_estimators': [50],
                    'learning_rate': [0.1]
                }
            },
            'XGBoost': {
                'model': xgb.XGBRegressor,
                'params': {
                    'n_estimators': [50],
                    'learning_rate': [0.1],
                    'max_depth': [3],
                    'n_jobs': [1]
                }
            },
            'SVR': {
                'model': SVR,
                'params': {
                    'C': [1],
                    'gamma': ['scale'],
                    'kernel': ['rbf']
                }
            },
            'MLP': {
                'model': MLPRegressor,
                'params': {
                    'hidden_layer_sizes': [(50,)],
                    'activation': ['relu'],
                    'alpha': [0.001],
                    'max_iter': [300]
                }
            }
        }
        
        # 完整模式配置（参数较多）
        self.models_config = {
            'LinearRegression': {
                'model': LinearRegression,
                'params': {
                    'fit_intercept': [True, False]
                }
            },
            'RandomForest': {
                'model': RandomForestRegressor,
                'params': {
                    'n_estimators': [50, 100],
                    'max_depth': [None, 10],
                    'min_samples_split': [2, 5]
                }
            },
            'GradientBoosting': {
                'model': GradientBoostingRegressor,
                'params': {
                    'n_estimators': [50, 100],
                    'learning_rate': [0.1, 0.2],
                    'max_depth': [3, 5]
                }
            },
            'XGBoost': {
                'model': xgb.XGBRegressor,
                'params': {
                    'n_estimators': [50, 100],
                    'learning_rate': [0.1, 0.2],
                    'max_depth': [3, 5],
                    'n_jobs': [1]  # 限制并行度
                }
            },
            'SVR': {
                'model': SVR,
                'params': {
                    'C': [1, 10],
                    'gamma': ['scale'],
                    'kernel': ['rbf']
                }
            },
            'MLP': {
                'model': MLPRegressor,
                'params': {
                    'hidden_layer_sizes': [(50,), (100,)],
                    'activation': ['relu'],
                    'alpha': [0.001],
                    'max_iter': [300]
                }
            }
        }
    
    def run_automl(self, train_data, test_data, params):
        """Run automated machine learning"""
        try:
            # Prepare data
            target_columns = params.get('target_columns', train_data.columns[-3:].tolist())
            feature_columns = [col for col in train_data.columns if col not in target_columns]
            
            X_train = train_data[feature_columns]
            y_train = train_data[target_columns]
            
            # AutoML configuration
            search_method = params.get('search_method', 'grid')  # 'grid' or 'random'
            cv_folds = params.get('cv_folds', 5)
            scoring = params.get('scoring', 'neg_mean_squared_error')
            training_mode = params.get('training_mode', 'fast')  # 'fast' or 'thorough'
            max_iter = params.get('max_iter', 50)  # for RandomizedSearchCV
            
            # 选择模型配置
            if training_mode == 'fast':
                models_config = self.fast_models_config
                print(f"使用快速模式训练")
            else:
                models_config = self.models_config
                print(f"使用完整模式训练")
                
            models_to_try = params.get('models', list(models_config.keys()))
            
            results = {}
            best_models = {}
            
            for target_col in target_columns:
                y_target = y_train[target_col] if len(target_columns) > 1 else y_train.iloc[:, 0]
                target_results = {}
                best_score = float('-inf')
                best_model_info = None
                
                print(f"正在为目标 {target_col} 运行AutoML...")
                
                for model_name in models_to_try:
                    if model_name not in models_config:
                        continue
                    
                    try:
                        model_config = models_config[model_name]
                        base_model = model_config['model']()
                        param_grid = model_config['params']
                        
                        # Choose search method
                        if search_method == 'random':
                            search = RandomizedSearchCV(
                                base_model,
                                param_grid,
                                n_iter=min(max_iter, 20),  # 限制最大迭代次数
                                cv=cv_folds,
                                scoring=scoring,
                                n_jobs=1,  # 限制并行度避免资源竞争
                                random_state=42,
                                verbose=0
                            )
                        else:
                            search = GridSearchCV(
                                base_model,
                                param_grid,
                                cv=cv_folds,
                                scoring=scoring,
                                n_jobs=1,  # 限制并行度
                                verbose=0
                            )
                        
                        # Fit the search
                        search.fit(X_train, y_target)
                        
                        # Get best results
                        best_estimator = search.best_estimator_
                        best_params = search.best_params_
                        best_cv_score = search.best_score_
                        
                        # Make predictions for evaluation
                        y_train_pred = best_estimator.predict(X_train)
                        train_r2 = r2_score(y_target, y_train_pred)
                        train_mse = mean_squared_error(y_target, y_train_pred)
                        
                        model_result = {
                            'model_name': model_name,
                            'best_params': best_params,
                            'cv_score': float(-best_cv_score),  # Convert back to positive
                            'train_r2': float(train_r2),
                            'train_mse': float(train_mse),
                            'train_rmse': float(np.sqrt(train_mse)),
                            'model': best_estimator
                        }
                        
                        # Test evaluation if test data is available
                        if test_data is not None:
                            X_test = test_data[feature_columns]
                            if target_col in test_data.columns:
                                y_test_target = test_data[target_col]
                                y_test_pred = best_estimator.predict(X_test)
                                test_r2 = r2_score(y_test_target, y_test_pred)
                                test_mse = mean_squared_error(y_test_target, y_test_pred)
                                
                                model_result.update({
                                    'test_r2': float(test_r2),
                                    'test_mse': float(test_mse),
                                    'test_rmse': float(np.sqrt(test_mse))
                                })
                        
                        target_results[model_name] = model_result
                        
                        # Track best model
                        if best_cv_score > best_score:
                            best_score = best_cv_score
                            best_model_info = {
                                'model_name': model_name,
                                'model': best_estimator,
                                'params': best_params,
                                'score': best_cv_score
                            }
                        
                        print(f"  {model_name}: CV Score = {-best_cv_score:.4f}")
                        
                    except Exception as e:
                        print(f"  {model_name}: 训练失败 - {str(e)}")
                        target_results[model_name] = {
                            'error': str(e),
                            'status': 'failed'
                        }
                
                results[target_col] = {
                    'models': target_results,
                    'best_model': best_model_info
                }
                
                if best_model_info:
                    best_models[target_col] = best_model_info
            
            # Generate model ID
            model_id = str(uuid.uuid4())
            
            # Prepare final model info (包含模型对象，用于app_state存储)
            final_model_info_storage = {
                'model': best_models if len(target_columns) > 1 else best_models.get(target_columns[0], {}).get('model'),
                'model_type': 'AutoML',
                'model_name': 'AutoML最优模型',
                'feature_columns': feature_columns,
                'target_columns': target_columns,
                'automl_config': {
                    'search_method': search_method,
                    'cv_folds': cv_folds,
                    'models_tried': models_to_try,
                    'scoring': scoring
                },
                'best_models_per_target': best_models,
                'training_time': datetime.now().isoformat(),
                'data_shape': list(train_data.shape)
            }
            
            # 准备JSON可序列化的模型信息
            final_model_info_json = {
                'model_type': 'AutoML',
                'model_name': 'AutoML最优模型',
                'feature_columns': feature_columns,
                'target_columns': target_columns,
                'automl_config': {
                    'search_method': search_method,
                    'cv_folds': cv_folds,
                    'models_tried': models_to_try,
                    'scoring': scoring
                },
                'training_time': datetime.now().isoformat(),
                'data_shape': list(train_data.shape)
            }
            
            # 清理results中的模型对象，只保留可序列化的数据
            clean_results = {}
            clean_best_models = {}
            
            for target_col, target_data in results.items():
                clean_target_results = {'models': {}}
                
                for model_name, model_result in target_data['models'].items():
                    if 'model' in model_result:
                        # 移除模型对象，保留其他信息
                        clean_model_result = {k: v for k, v in model_result.items() if k != 'model'}
                        clean_target_results['models'][model_name] = clean_model_result
                    else:
                        clean_target_results['models'][model_name] = model_result
                
                # 处理best_model信息
                if 'best_model' in target_data and target_data['best_model']:
                    best_model_info = target_data['best_model'].copy()
                    if 'model' in best_model_info:
                        del best_model_info['model']
                    clean_target_results['best_model'] = best_model_info
                
                clean_results[target_col] = clean_target_results
                
                # 清理best_models
                if target_col in best_models:
                    clean_best_model = best_models[target_col].copy()
                    if 'model' in clean_best_model:
                        del clean_best_model['model']
                    clean_best_models[target_col] = clean_best_model
            
            return {
                'success': True,
                'message': 'AutoML完成',
                'model_id': model_id,
                'model': final_model_info_storage,  # 这个会在app.py中被移除
                'model_info': final_model_info_json,
                'results': clean_results,
                'best_models': clean_best_models,
                'feature_columns': feature_columns,
                'target_columns': target_columns
            }
            
        except Exception as e:
            return {'success': False, 'message': f'AutoML运行失败: {str(e)}'}
    
    def model_comparison_report(self, results):
        """Generate model comparison report"""
        try:
            comparison_data = []
            
            for target_col, target_results in results.items():
                models = target_results.get('models', {})
                
                for model_name, model_result in models.items():
                    if 'error' not in model_result:
                        comparison_data.append({
                            'target': target_col,
                            'model': model_name,
                            'cv_score': model_result.get('cv_score', 0),
                            'train_r2': model_result.get('train_r2', 0),
                            'train_rmse': model_result.get('train_rmse', 0),
                            'test_r2': model_result.get('test_r2', 'N/A'),
                            'test_rmse': model_result.get('test_rmse', 'N/A')
                        })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            return {
                'success': True,
                'comparison_table': comparison_df.to_dict('records'),
                'summary': {
                    'total_models_trained': len(comparison_data),
                    'targets_processed': len(results),
                    'best_overall_model': self._find_best_overall_model(results)
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'生成比较报告失败: {str(e)}'}
    
    def _find_best_overall_model(self, results):
        """Find the best overall performing model across all targets"""
        best_model = None
        best_avg_score = float('-inf')
        
        model_scores = {}
        
        for target_col, target_results in results.items():
            models = target_results.get('models', {})
            
            for model_name, model_result in models.items():
                if 'error' not in model_result:
                    cv_score = model_result.get('cv_score', 0)
                    
                    if model_name not in model_scores:
                        model_scores[model_name] = []
                    model_scores[model_name].append(cv_score)
        
        # Calculate average scores
        for model_name, scores in model_scores.items():
            avg_score = np.mean(scores)
            if avg_score > best_avg_score:
                best_avg_score = avg_score
                best_model = {
                    'model_name': model_name,
                    'average_cv_score': float(avg_score),
                    'score_std': float(np.std(scores)),
                    'targets_count': len(scores)
                }
        
        return best_model 