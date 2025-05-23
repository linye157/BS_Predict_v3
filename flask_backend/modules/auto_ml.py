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
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 10, 20],
                    'min_samples_split': [2, 5, 10]
                }
            },
            'GradientBoosting': {
                'model': GradientBoostingRegressor,
                'params': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                }
            },
            'XGBoost': {
                'model': xgb.XGBRegressor,
                'params': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                }
            },
            'SVR': {
                'model': SVR,
                'params': {
                    'C': [0.1, 1, 10],
                    'gamma': ['scale', 'auto'],
                    'kernel': ['rbf', 'linear']
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
            models_to_try = params.get('models', list(self.models_config.keys()))
            max_iter = params.get('max_iter', 50)  # for RandomizedSearchCV
            
            results = {}
            best_models = {}
            
            for target_col in target_columns:
                y_target = y_train[target_col] if len(target_columns) > 1 else y_train.iloc[:, 0]
                target_results = {}
                best_score = float('-inf')
                best_model_info = None
                
                print(f"正在为目标 {target_col} 运行AutoML...")
                
                for model_name in models_to_try:
                    if model_name not in self.models_config:
                        continue
                    
                    try:
                        model_config = self.models_config[model_name]
                        base_model = model_config['model']()
                        param_grid = model_config['params']
                        
                        # Choose search method
                        if search_method == 'random':
                            search = RandomizedSearchCV(
                                base_model,
                                param_grid,
                                n_iter=max_iter,
                                cv=cv_folds,
                                scoring=scoring,
                                n_jobs=-1,
                                random_state=42
                            )
                        else:
                            search = GridSearchCV(
                                base_model,
                                param_grid,
                                cv=cv_folds,
                                scoring=scoring,
                                n_jobs=-1
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
            
            # Prepare final model info
            final_model_info = {
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
                'data_shape': train_data.shape
            }
            
            return {
                'success': True,
                'message': 'AutoML完成',
                'model_id': model_id,
                'model': final_model_info,
                'results': results,
                'best_models': best_models,
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