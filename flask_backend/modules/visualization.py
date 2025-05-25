import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

# Font setup removed - using default matplotlib fonts
# Plotly imports removed - using only Matplotlib
import base64
import io
import json
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib backend to non-interactive
plt.switch_backend('Agg')

class VisualizationService:
    def __init__(self):
        # Set style for matplotlib
        plt.style.use('default')
        sns.set_palette("husl")
        
    def generate_data_visualization(self, data, params):
        """Generate data visualization"""
        try:
            viz_type = params.get('type', 'distribution')
            columns = params.get('columns', data.columns.tolist())
            chart_type = params.get('chart_type', 'matplotlib')  # Only matplotlib supported
            
            if viz_type == 'correlation':
                return self._generate_correlation_matrix(data, columns, chart_type)
            elif viz_type == 'scatter':
                return self._generate_scatter_plots(data, params, chart_type)
            elif viz_type == 'histogram':
                return self._generate_histograms(data, columns, chart_type)
            else:
                return {'success': False, 'message': f'Unsupported visualization type: {viz_type}'}
                
        except Exception as e:
                            return {'success': False, 'message': f'Failed to generate data visualization: {str(e)}'}
    
    def generate_model_visualization(self, model_info, train_data, params):
        """Generate model visualization"""
        try:
            viz_type = params.get('type', 'prediction')
            chart_type = params.get('chart_type', 'matplotlib')  # Only matplotlib supported
            
            if viz_type == 'prediction':
                return self._generate_prediction_plots(model_info, train_data, chart_type)
            elif viz_type == 'residuals':
                return self._generate_residual_plots(model_info, train_data, chart_type)
            elif viz_type == 'feature_importance':
                return self._generate_feature_importance(model_info, chart_type)
            elif viz_type == 'learning_curve':
                return self._generate_learning_curve(model_info, train_data, chart_type)
            else:
                return {'success': False, 'message': f'Unsupported model visualization type: {viz_type}'}
                
        except Exception as e:
            return {'success': False, 'message': f'Failed to generate model visualization: {str(e)}'}
    

    
    def _generate_correlation_matrix(self, data, columns, chart_type):
        """Generate correlation matrix"""
        numeric_data = data.select_dtypes(include=[np.number])
        
        if numeric_data.empty:
            return {'success': False, 'message': 'No numeric columns available for correlation matrix'}
        
        # 如果用户选择了特定列，只使用这些列
        if columns and len(columns) > 0:
            # 确保选择的列都是数值列
            selected_columns = [col for col in columns if col in numeric_data.columns]
            if len(selected_columns) == 0:
                return {'success': False, 'message': 'No valid numeric columns selected'}
            numeric_data = numeric_data[selected_columns]
        
        # 计算相关性矩阵
        corr_matrix = numeric_data.corr()
        
        # 检查是否有有效的相关性数据
        if corr_matrix.empty or corr_matrix.isna().all().all():
            return {'success': False, 'message': 'Cannot calculate correlation matrix, data may contain too many missing values'}
        
        # Matplotlib version
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": .5})
        plt.title('Feature Correlation Matrix')
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return {
            'success': True,
            'chart_data': img_base64,
            'chart_type': 'matplotlib'
        }
    
    def _generate_scatter_plots(self, data, params, chart_type):
        """Generate scatter plots"""
        x_col = params.get('x_column')
        y_col = params.get('y_column')
        
        if not x_col or not y_col:
            # Use first two numeric columns
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) < 2:
                return {'success': False, 'message': 'Need at least two numeric columns to generate scatter plot'}
            x_col, y_col = numeric_cols[0], numeric_cols[1]
        
        # 检查列是否存在
        if x_col not in data.columns or y_col not in data.columns:
            return {'success': False, 'message': f'Specified columns do not exist: {x_col} or {y_col}'}
        
        # 清理数据，移除NaN值
        clean_data = data[[x_col, y_col]].dropna()
        if len(clean_data) == 0:
            return {'success': False, 'message': 'No valid data points available for scatter plot'}
        
        # Matplotlib version
        plt.figure(figsize=(10, 6))
        plt.scatter(clean_data[x_col], clean_data[y_col], alpha=0.7, edgecolors='black', linewidth=0.5)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f'{x_col} vs {y_col}')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return {
            'success': True,
            'chart_data': img_base64,
            'chart_type': 'matplotlib'
        }
    

    
    def _generate_histograms(self, data, columns, chart_type):
        """Generate histograms for data distribution"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        selected_columns = [col for col in columns if col in numeric_columns][:6]  # Limit to 6 columns
        
        if len(selected_columns) == 0:
            return {'success': False, 'message': 'No numeric columns available for histogram visualization'}
        
        # Calculate subplot layout
        n_cols = min(3, len(selected_columns))
        n_rows = (len(selected_columns) + n_cols - 1) // n_cols
        
        # Matplotlib version
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 5))
        fig.suptitle('Data Distribution Histograms', fontsize=16)
        
        # Ensure axes is always 2D array
        if n_rows == 1 and n_cols == 1:
            axes = np.array([[axes]])
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        elif n_cols == 1:
            axes = axes.reshape(-1, 1)
        
        for i, col in enumerate(selected_columns):
            row = i // n_cols
            col_num = i % n_cols
            col_data = data[col].dropna()
            
            if len(col_data) > 0:
                axes[row, col_num].hist(col_data, bins=30, alpha=0.7, edgecolor='black', color='skyblue')
                axes[row, col_num].set_title(f'{col} Distribution')
                axes[row, col_num].set_xlabel('Value')
                axes[row, col_num].set_ylabel('Frequency')
                axes[row, col_num].grid(True, alpha=0.3)
                
                # Add statistics text
                mean_val = col_data.mean()
                std_val = col_data.std()
                axes[row, col_num].axvline(mean_val, color='red', linestyle='--', alpha=0.7, label=f'Mean: {mean_val:.2f}')
                axes[row, col_num].legend()
        
        # Hide empty subplots
        for i in range(len(selected_columns), n_rows * n_cols):
            row = i // n_cols
            col_num = i % n_cols
            axes[row, col_num].set_visible(False)
        
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return {
            'success': True,
            'chart_data': img_base64,
            'chart_type': 'matplotlib'
        }
    
    def _generate_prediction_plots(self, model_info, train_data, chart_type):
        """Generate prediction vs actual plots"""
        try:
            model = model_info['model']
            feature_columns = model_info['feature_columns']
            target_columns = model_info['target_columns']
            
            X = train_data[feature_columns]
            y_actual = train_data[target_columns]
            
            results = {}
            
            for target_col in target_columns:
                if len(target_columns) == 1:
                    y_pred = model.predict(X)
                    y_true = y_actual.iloc[:, 0]
                else:
                    y_pred = model[target_col].predict(X)
                    y_true = y_actual[target_col]
                
                # Matplotlib version
                plt.figure(figsize=(8, 6))
                plt.scatter(y_true, y_pred, alpha=0.7, edgecolors='black', linewidth=0.5)
                
                # Perfect prediction line
                min_val = min(y_true.min(), y_pred.min())
                max_val = max(y_true.max(), y_pred.max())
                plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Prediction')
                
                plt.xlabel('Actual Values')
                plt.ylabel('Predicted Values')
                plt.title(f'Predicted vs Actual - {target_col}')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                
                # Convert to base64
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                img_buffer.seek(0)
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                plt.close()
                
                results[target_col] = {
                    'chart_data': img_base64,
                    'chart_type': 'matplotlib'
                }
            
            return {
                'success': True,
                'results': results,
                'message': 'Prediction plots generated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to generate prediction plots: {str(e)}'}
    
    def _generate_residual_plots(self, model_info, train_data, chart_type):
        """Generate residual plots"""
        try:
            model = model_info['model']
            feature_columns = model_info['feature_columns']
            target_columns = model_info['target_columns']
            
            X = train_data[feature_columns]
            y_actual = train_data[target_columns]
            
            results = {}
            
            for target_col in target_columns:
                if len(target_columns) == 1:
                    y_pred = model.predict(X)
                    y_true = y_actual.iloc[:, 0]
                else:
                    y_pred = model[target_col].predict(X)
                    y_true = y_actual[target_col]
                
                residuals = y_true - y_pred
                
                # Matplotlib version
                plt.figure(figsize=(8, 6))
                plt.scatter(y_pred, residuals, alpha=0.7, edgecolors='black', linewidth=0.5)
                plt.axhline(y=0, color='r', linestyle='--', label='Zero Line')
                plt.xlabel('Predicted Values')
                plt.ylabel('Residuals')
                plt.title(f'Residual Plot - {target_col}')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                
                # Convert to base64
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                img_buffer.seek(0)
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                plt.close()
                
                results[target_col] = {
                    'chart_data': img_base64,
                    'chart_type': 'matplotlib'
                }
            
            return {
                'success': True,
                'results': results,
                'message': 'Residual plots generated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to generate residual plots: {str(e)}'}
    
    def _generate_feature_importance(self, model_info, chart_type):
        """Generate feature importance plots"""
        try:
            model = model_info['model']
            feature_columns = model_info['feature_columns']
            target_columns = model_info['target_columns']
            
            results = {}
            
            for target_col in target_columns:
                current_model = model if len(target_columns) == 1 else model[target_col]
                
                # Check if model has feature importance
                if hasattr(current_model, 'feature_importances_'):
                    importance = current_model.feature_importances_
                elif hasattr(current_model, 'coef_'):
                    importance = np.abs(current_model.coef_)
                else:
                    continue
                
                # Create importance dataframe
                importance_df = pd.DataFrame({
                    'feature': feature_columns,
                    'importance': importance
                }).sort_values('importance', ascending=False).head(20)  # Top 20 features
                
                # Matplotlib version
                plt.figure(figsize=(10, 8))
                plt.barh(range(len(importance_df)), importance_df['importance'], alpha=0.7, edgecolor='black')
                plt.yticks(range(len(importance_df)), importance_df['feature'])
                plt.xlabel('Importance')
                plt.title(f'Feature Importance - {target_col}')
                plt.gca().invert_yaxis()
                plt.grid(True, alpha=0.3, axis='x')
                plt.tight_layout()
                
                # Convert to base64
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                img_buffer.seek(0)
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                plt.close()
                
                results[target_col] = {
                    'chart_data': img_base64,
                    'chart_type': 'matplotlib',
                    'importance_data': importance_df.to_dict('records')
                }
            
            if not results:
                return {'success': False, 'message': 'Model does not support feature importance analysis'}
            
            return {
                'success': True,
                'results': results,
                'message': 'Feature importance plots generated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to generate feature importance plot: {str(e)}'}
    
    def _generate_learning_curve(self, model_info, train_data, chart_type):
        """Generate learning curve (simplified version)"""
        # This is a placeholder for learning curve implementation
        # In a full implementation, you would track training history
        return {
            'success': False,
            'message': 'Learning curve feature not yet implemented, requires recording learning history during training'
        } 