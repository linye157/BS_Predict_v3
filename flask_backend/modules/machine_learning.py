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
                    'copy_X': [True, False],
                    'n_jobs': [None, -1],
                    'positive': [False, True]
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
            
            print(f"开始训练模型: {model_type}")
            
            # Prepare data
            target_columns = params.get('target_columns', train_data.columns[-3:].tolist())
            feature_columns = [col for col in train_data.columns if col not in target_columns]
            
            X = train_data[feature_columns]
            y = train_data[target_columns]
            
            # 对于大数据集，减少验证集比例以提高训练效率
            data_size = len(train_data)
            if data_size > 10000:
                test_size = min(0.15, params.get('test_size', 0.2))  # 大数据集使用更小的验证集
                print(f"大数据集检测到({data_size}条)，调整验证集比例为{test_size}")
            else:
                test_size = params.get('test_size', 0.2)
            
            # Split data for validation
            random_state = params.get('random_state', 42)
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            print(f"训练集大小: {X_train.shape}, 验证集大小: {X_val.shape}")
            
            # Initialize model
            model_info = self.models[model_type]
            model_params = params.get('model_params', {})
            
            # 验证并清理模型参数
            validated_params = self._validate_model_params(model_type, model_params)
            
            # 对大数据集优化参数
            if data_size > 15000:
                validated_params = self._optimize_params_for_large_data(model_type, validated_params, data_size)
                print(f"大数据集优化后参数: {validated_params}")
            else:
                print(f"验证后的模型参数: {validated_params}")
            
            # Handle different target scenarios
            if len(target_columns) == 1:
                # Single target
                y_train_single = y_train.iloc[:, 0]
                y_val_single = y_val.iloc[:, 0]
                
                print(f"开始训练单目标模型...")
                
                if params.get('use_grid_search', False):
                    # Grid search for hyperparameter tuning
                    print("使用网格搜索优化参数...")
                    grid_params = self._get_grid_search_params(model_type, validated_params)
                    
                    # 对大数据集减少CV折数
                    cv_folds = 3 if data_size > 15000 else 5
                    print(f"使用{cv_folds}折交叉验证")
                    
                    model = GridSearchCV(
                        model_info['class'](),
                        grid_params,
                        cv=cv_folds,
                        scoring='neg_mean_squared_error',
                        n_jobs=-1,
                        verbose=1  # 显示进度
                    )
                    model.fit(X_train, y_train_single)
                    best_model = model.best_estimator_
                    best_params = model.best_params_
                    print("网格搜索完成")
                else:
                    # Direct training with provided params
                    print("直接训练模型...")
                    model = model_info['class'](**validated_params)
                    model.fit(X_train, y_train_single)
                    best_model = model
                    best_params = validated_params
                    print("模型训练完成")
                
                print("开始预测和计算指标...")
                # Predictions
                y_train_pred = best_model.predict(X_train)
                y_val_pred = best_model.predict(X_val)
                
                # Metrics - 确保格式一致
                train_metrics = {target_columns[0]: self._calculate_metrics(y_train_single, y_train_pred)}
                val_metrics = {target_columns[0]: self._calculate_metrics(y_val_single, y_val_pred)}
                
            else:
                # Multiple targets - train separate models for each target
                print(f"开始训练多目标模型 ({len(target_columns)}个目标)...")
                models = {}
                train_metrics = {}
                val_metrics = {}
                
                for i, target_col in enumerate(target_columns):
                    print(f"训练目标 {i+1}/{len(target_columns)}: {target_col}")
                    y_train_single = y_train.iloc[:, i]
                    y_val_single = y_val.iloc[:, i]
                    
                    if params.get('use_grid_search', False):
                        print(f"为目标{target_col}使用网格搜索...")
                        grid_params = self._get_grid_search_params(model_type, validated_params)
                        cv_folds = 3 if data_size > 15000 else 5
                        model = GridSearchCV(
                            model_info['class'](),
                            grid_params,
                            cv=cv_folds,
                            scoring='neg_mean_squared_error',
                            n_jobs=-1,
                            verbose=1
                        )
                        model.fit(X_train, y_train_single)
                        models[target_col] = model.best_estimator_
                    else:
                        model = model_info['class'](**validated_params)
                        model.fit(X_train, y_train_single)
                        models[target_col] = model
                    
                    print(f"目标{target_col}训练完成，计算指标...")
                    # Predictions for this target
                    y_train_pred = models[target_col].predict(X_train)
                    y_val_pred = models[target_col].predict(X_val)
                    
                    # Metrics for this target
                    train_metrics[target_col] = self._calculate_metrics(y_train_single, y_train_pred)
                    val_metrics[target_col] = self._calculate_metrics(y_val_single, y_val_pred)
                
                best_model = models
                best_params = validated_params
            
            print("开始交叉验证评分...")
            # Cross-validation score - 对大数据集进行优化
            cv_scores = {}
            try:
                # 对大数据集使用更少的CV折数和采样
                if data_size > 15000:
                    cv_folds = 3
                    # 对超大数据集进行采样以加速CV
                    if data_size > 50000:
                        sample_size = min(10000, data_size // 2)
                        sample_indices = np.random.choice(len(X), sample_size, replace=False)
                        X_cv = X.iloc[sample_indices]
                        y_cv = y.iloc[sample_indices]
                        print(f"超大数据集采样CV: 使用{sample_size}样本进行{cv_folds}折交叉验证")
                    else:
                        X_cv = X
                        y_cv = y
                        print(f"大数据集CV: 使用{cv_folds}折交叉验证")
                else:
                    cv_folds = 5
                    X_cv = X
                    y_cv = y
                    print(f"标准CV: 使用{cv_folds}折交叉验证")
                
                for i, target_col in enumerate(target_columns):
                    try:
                        if len(target_columns) == 1:
                            cv_score = cross_val_score(
                                best_model, X_cv, y_cv.iloc[:, 0], 
                                cv=cv_folds, scoring='neg_mean_squared_error',
                                n_jobs=-1
                            )
                        else:
                            cv_score = cross_val_score(
                                best_model[target_col], X_cv, y_cv[target_col], 
                                cv=cv_folds, scoring='neg_mean_squared_error',
                                n_jobs=-1
                            )
                        cv_scores[target_col] = float(-cv_score.mean())
                        print(f"目标{target_col}的CV分数: {cv_scores[target_col]:.4f}")
                    except Exception as cv_error:
                        print(f"目标{target_col}的CV计算失败: {cv_error}")
                        cv_scores[target_col] = 0.0
            except Exception as e:
                print(f"交叉验证过程出错: {e}")
                # 如果CV失败，使用验证集的MSE作为替代
                for target_col in target_columns:
                    cv_scores[target_col] = val_metrics[target_col]['mse']
            
            print("训练完成，生成结果...")
            # Generate unique model ID
            model_id = str(uuid.uuid4())
            
            # Prepare model info for storage (不包含在JSON响应中)
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
            
            # 准备JSON可序列化的响应结果
            result = {
                'success': True,
                'message': f'{model_info["name"]} 训练完成',
                'model_id': model_id,
                'model': model_info_storage,  # 这个会在app.py中被移除
                'model_info': {
                    'model_type': model_type,
                    'model_name': model_info['name'],
                    'feature_columns': feature_columns,
                    'target_columns': target_columns,
                    'params': best_params,
                    'training_time': datetime.now().isoformat(),
                    'data_shape': list(train_data.shape)
                },
                'metrics': {
                    'train': train_metrics,
                    'validation': val_metrics,
                    'cross_validation': cv_scores
                },
                'feature_columns': feature_columns,
                'target_columns': target_columns,
                'best_params': best_params
            }
            
            print(f"模型{model_id}训练完成，返回结果")
            return result
            
        except Exception as e:
            import traceback
            error_msg = f'模型训练失败: {str(e)}'
            print(f"训练异常: {error_msg}")
            print(f"详细错误: {traceback.format_exc()}")
            return {'success': False, 'message': error_msg}
    
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
            
            # 确保返回可序列化的数据
            return {
                'success': True,
                'message': '预测完成',
                'predictions': result_df.to_dict('records'),  # 转换为可序列化的字典列表
                'shape': list(result_df.shape),  # 转换为列表
                'columns': list(result_df.columns),  # 添加列名信息
                'prediction_count': len(result_df)
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
    
    def _validate_model_params(self, model_type, params):
        """验证模型参数的有效性，移除无效参数"""
        if model_type not in self.models:
            return params
            
        model_class = self.models[model_type]['class']
        
        # 获取模型类的有效参数
        try:
            # 创建一个临时实例来获取有效参数
            temp_instance = model_class()
            valid_params = temp_instance.get_params().keys()
            
            # 过滤掉无效参数
            validated_params = {}
            for key, value in params.items():
                if key in valid_params:
                    validated_params[key] = value
                else:
                    print(f"警告: 参数 '{key}' 对于模型 {model_type} 无效，已忽略")
            
            return validated_params
        except Exception as e:
            print(f"参数验证失败: {e}")
            return params
    
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
    
    def _optimize_params_for_large_data(self, model_type, params, data_size):
        """优化大数据集的模型参数以提高训练效率"""
        optimized_params = params.copy()
        
        if model_type == 'RandomForest':
            # 随机森林：减少估计器数量，限制深度
            if data_size > 20000:
                if 'n_estimators' not in optimized_params or optimized_params['n_estimators'] > 50:
                    optimized_params['n_estimators'] = 50
                if 'max_depth' not in optimized_params:
                    optimized_params['max_depth'] = 15
                optimized_params['n_jobs'] = -1  # 使用所有CPU核心
            
        elif model_type == 'GradientBoosting':
            # 梯度提升：减少估计器数量，增加学习率
            if data_size > 20000:
                if 'n_estimators' not in optimized_params or optimized_params['n_estimators'] > 50:
                    optimized_params['n_estimators'] = 50
                if 'learning_rate' not in optimized_params:
                    optimized_params['learning_rate'] = 0.15  # 稍微增加学习率
                if 'max_depth' not in optimized_params:
                    optimized_params['max_depth'] = 5
                    
        elif model_type == 'XGBoost':
            # XGBoost：优化参数
            if data_size > 20000:
                if 'n_estimators' not in optimized_params or optimized_params['n_estimators'] > 50:
                    optimized_params['n_estimators'] = 50
                if 'learning_rate' not in optimized_params:
                    optimized_params['learning_rate'] = 0.15
                if 'max_depth' not in optimized_params:
                    optimized_params['max_depth'] = 5
                optimized_params['n_jobs'] = -1
                optimized_params['tree_method'] = 'hist'  # 使用更快的直方图方法
                
        elif model_type == 'SVR':
            # SVR：对大数据集添加缓存限制
            if data_size > 20000:
                optimized_params['cache_size'] = 2000  # 限制缓存大小
                if 'C' not in optimized_params:
                    optimized_params['C'] = 1.0  # 使用默认C值
                if 'gamma' not in optimized_params:
                    optimized_params['gamma'] = 'scale'
                    
        elif model_type == 'MLP':
            # MLP：减少最大迭代次数，早停
            if data_size > 20000:
                optimized_params['max_iter'] = 200  # 减少最大迭代次数
                optimized_params['early_stopping'] = True
                optimized_params['validation_fraction'] = 0.1
                optimized_params['n_iter_no_change'] = 10
                if 'hidden_layer_sizes' not in optimized_params:
                    optimized_params['hidden_layer_sizes'] = (100,)  # 简化网络结构
        
        return optimized_params 