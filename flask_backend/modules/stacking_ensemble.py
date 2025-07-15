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
            print("开始Stacking集成训练...")
            
            # Prepare data
            target_columns = params.get('target_columns', train_data.columns[-3:].tolist())
            feature_columns = [col for col in train_data.columns if col not in target_columns]
            
            X = train_data[feature_columns]
            y = train_data[target_columns]
            
            # 对大数据集进行优化
            data_size = len(train_data)
            print(f"数据集大小: {data_size}")
            
            # Configuration parameters
            cv_folds = params.get('cv_folds', 5)
            meta_model_type = params.get('meta_model', 'LinearRegression')
            selected_base_models = params.get('base_models', ['LinearRegression'])
            
            # 对大数据集优化参数
            if data_size > 15000:
                cv_folds = min(cv_folds, 3)  # 减少交叉验证折数
                print(f"大数据集检测，调整CV折数为: {cv_folds}")
                
                # 优化基学习器参数
                optimized_base_models = self._get_optimized_base_models(selected_base_models, data_size)
                optimized_meta_model = self._get_optimized_meta_model(meta_model_type, data_size)
            else:
                optimized_base_models = self._get_default_base_models(selected_base_models)
                optimized_meta_model = self._get_default_meta_model(meta_model_type)
            
            print(f"选择的基学习器: {selected_base_models}")
            print(f"元学习器: {meta_model_type}")
            print(f"交叉验证折数: {cv_folds}")
            
            # Select base models
            base_estimators = [
                (name, optimized_base_models[name]) for name in selected_base_models 
                if name in optimized_base_models
            ]
            
            print(f"构建了 {len(base_estimators)} 个基学习器")
            
            results = {}
            models = {}
            
            # Train stacking model for each target
            for i, target_col in enumerate(target_columns):
                print(f"训练目标 {i+1}/{len(target_columns)}: {target_col}")
                
                y_target = y[target_col] if len(target_columns) > 1 else y.iloc[:, 0]
                
                # Create stacking regressor with optimized parameters
                stacking_model = StackingRegressor(
                    estimators=base_estimators,
                    final_estimator=optimized_meta_model,
                    cv=cv_folds,
                    n_jobs=-1,  # 使用所有CPU核心
                    passthrough=False  # 不传递原始特征，减少计算量
                )
                
                print(f"开始训练{target_col}的Stacking模型...")
                # Train the model
                stacking_model.fit(X, y_target)
                models[target_col] = stacking_model
                print(f"{target_col}模型训练完成")
                
                print(f"开始{target_col}的交叉验证评估...")
                # Cross-validation evaluation - 对大数据集进行优化
                try:
                    if data_size > 20000:
                        # 对超大数据集进行采样评估
                        sample_size = min(10000, data_size // 2)
                        sample_indices = np.random.choice(len(X), sample_size, replace=False)
                        X_sample = X.iloc[sample_indices]
                        y_sample = y_target.iloc[sample_indices]
                        print(f"大数据集采样评估: 使用{sample_size}样本")
                        
                        cv_scores = cross_val_score(
                            stacking_model, X_sample, y_sample, 
                            cv=cv_folds, scoring='neg_mean_squared_error',
                            n_jobs=-1
                        )
                    else:
                        cv_scores = cross_val_score(
                            stacking_model, X, y_target, 
                            cv=cv_folds, scoring='neg_mean_squared_error',
                            n_jobs=-1
                        )
                    
                    cv_score_mean = float(-cv_scores.mean())
                    cv_score_std = float(cv_scores.std())
                    print(f"{target_col}交叉验证完成，CV分数: {cv_score_mean:.4f}")
                    
                except Exception as cv_error:
                    print(f"{target_col}交叉验证失败: {cv_error}")
                    cv_score_mean = 0.0
                    cv_score_std = 0.0
                
                print(f"计算{target_col}的训练指标...")
                # Get predictions for training data - 对大数据集优化
                if data_size > 30000:
                    # 对超大数据集使用采样预测
                    sample_size = min(5000, data_size // 4)
                    sample_indices = np.random.choice(len(X), sample_size, replace=False)
                    X_pred = X.iloc[sample_indices]
                    y_true = y_target.iloc[sample_indices]
                    y_pred = stacking_model.predict(X_pred)
                    print(f"使用{sample_size}样本计算训练指标")
                else:
                    y_pred = stacking_model.predict(X)
                    y_true = y_target
                
                # Calculate metrics
                metrics = {
                    'mse': float(mean_squared_error(y_true, y_pred)),
                    'rmse': float(np.sqrt(mean_squared_error(y_true, y_pred))),
                    'mae': float(mean_absolute_error(y_true, y_pred)),
                    'r2': float(r2_score(y_true, y_pred)),
                    'cv_score': cv_score_mean,
                    'cv_std': cv_score_std
                }
                
                results[target_col] = metrics
                print(f"{target_col}指标计算完成: R²={metrics['r2']:.4f}")
            
            print("生成模型结果...")
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
            result = {
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
            
            print(f"Stacking模型{model_id}训练完成")
            return result
            
        except Exception as e:
            import traceback
            error_msg = f'Stacking模型训练失败: {str(e)}'
            print(f"Stacking训练异常: {error_msg}")
            print(f"详细错误: {traceback.format_exc()}")
            return {'success': False, 'message': error_msg}
    
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
    
    def _get_optimized_base_models(self, selected_models, data_size):
        """为大数据集优化基学习器参数"""
        optimized_models = {}
        
        for model_name in selected_models:
            if model_name == 'LinearRegression':
                optimized_models[model_name] = LinearRegression(n_jobs=-1)
                
            elif model_name == 'RandomForest':
                # 减少估计器数量和深度
                n_estimators = 30 if data_size > 20000 else 50
                max_depth = 10 if data_size > 20000 else 15
                optimized_models[model_name] = RandomForestRegressor(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    random_state=42,
                    n_jobs=-1
                )
                
            elif model_name == 'GradientBoosting':
                # 减少估计器数量，增加学习率
                n_estimators = 30 if data_size > 20000 else 50
                learning_rate = 0.15 if data_size > 20000 else 0.1
                optimized_models[model_name] = GradientBoostingRegressor(
                    n_estimators=n_estimators,
                    learning_rate=learning_rate,
                    max_depth=5,
                    random_state=42
                )
                
            elif model_name == 'XGBoost':
                # XGBoost优化
                n_estimators = 30 if data_size > 20000 else 50
                learning_rate = 0.15 if data_size > 20000 else 0.1
                optimized_models[model_name] = xgb.XGBRegressor(
                    n_estimators=n_estimators,
                    learning_rate=learning_rate,
                    max_depth=5,
                    random_state=42,
                    n_jobs=-1,
                    tree_method='hist'  # 更快的训练方法
                )
                
            elif model_name == 'SVR':
                # SVR优化
                optimized_models[model_name] = SVR(
                    C=1.0, 
                    kernel='rbf',
                    cache_size=2000  # 限制缓存大小
                )
                
            elif model_name == 'MLP':
                # MLP优化
                hidden_layer_sizes = (50,) if data_size > 20000 else (100,)
                max_iter = 200 if data_size > 20000 else 300
                optimized_models[model_name] = MLPRegressor(
                    hidden_layer_sizes=hidden_layer_sizes,
                    random_state=42,
                    max_iter=max_iter,
                    early_stopping=True,
                    validation_fraction=0.1,
                    n_iter_no_change=10
                )
        
        return optimized_models
    
    def _get_default_base_models(self, selected_models):
        """获取默认的基学习器"""
        return {name: self.base_models[name]['model'] for name in selected_models if name in self.base_models}
    
    def _get_optimized_meta_model(self, meta_model_type, data_size):
        """为大数据集优化元学习器参数"""
        if meta_model_type == 'LinearRegression':
            return LinearRegression(n_jobs=-1)
            
        elif meta_model_type == 'RandomForest':
            n_estimators = 20 if data_size > 20000 else 30
            return RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=8,
                random_state=42,
                n_jobs=-1
            )
            
        elif meta_model_type == 'GradientBoosting':
            n_estimators = 20 if data_size > 20000 else 30
            return GradientBoostingRegressor(
                n_estimators=n_estimators,
                learning_rate=0.15,
                max_depth=3,
                random_state=42
            )
            
        elif meta_model_type == 'XGBoost':
            n_estimators = 20 if data_size > 20000 else 30
            return xgb.XGBRegressor(
                n_estimators=n_estimators,
                learning_rate=0.15,
                max_depth=3,
                random_state=42,
                n_jobs=-1,
                tree_method='hist'
            )
            
        elif meta_model_type == 'SVR':
            return SVR(C=1.0, kernel='rbf', cache_size=1000)
            
        elif meta_model_type == 'MLP':
            return MLPRegressor(
                hidden_layer_sizes=(30,),
                random_state=42,
                max_iter=150,
                early_stopping=True,
                validation_fraction=0.1
            )
        
        # 默认返回线性回归
        return LinearRegression(n_jobs=-1)
    
    def _get_default_meta_model(self, meta_model_type):
        """获取默认的元学习器"""
        if meta_model_type in self.meta_models:
            return self.meta_models[meta_model_type]['model']
        else:
            return self.meta_models['LinearRegression']['model'] 