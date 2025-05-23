import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
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
            chart_type = params.get('chart_type', 'plotly')  # 'plotly' or 'matplotlib'
            
            if viz_type == 'distribution':
                return self._generate_distribution_plots(data, columns, chart_type)
            elif viz_type == 'correlation':
                return self._generate_correlation_matrix(data, columns, chart_type)
            elif viz_type == 'scatter':
                return self._generate_scatter_plots(data, params, chart_type)
            elif viz_type == 'histogram':
                return self._generate_histograms(data, columns, chart_type)
            elif viz_type == 'box':
                return self._generate_box_plots(data, columns, chart_type)
            else:
                return {'success': False, 'message': f'不支持的可视化类型: {viz_type}'}
                
        except Exception as e:
            return {'success': False, 'message': f'生成数据可视化失败: {str(e)}'}
    
    def generate_model_visualization(self, model_info, train_data, params):
        """Generate model visualization"""
        try:
            viz_type = params.get('type', 'prediction')
            chart_type = params.get('chart_type', 'plotly')
            
            if viz_type == 'prediction':
                return self._generate_prediction_plots(model_info, train_data, chart_type)
            elif viz_type == 'residuals':
                return self._generate_residual_plots(model_info, train_data, chart_type)
            elif viz_type == 'feature_importance':
                return self._generate_feature_importance(model_info, chart_type)
            elif viz_type == 'learning_curve':
                return self._generate_learning_curve(model_info, train_data, chart_type)
            else:
                return {'success': False, 'message': f'不支持的模型可视化类型: {viz_type}'}
                
        except Exception as e:
            return {'success': False, 'message': f'生成模型可视化失败: {str(e)}'}
    
    def _generate_distribution_plots(self, data, columns, chart_type):
        """Generate distribution plots for numeric columns"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        selected_columns = [col for col in columns if col in numeric_columns][:6]  # Limit to 6 columns
        
        if chart_type == 'plotly':
            fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=selected_columns,
                specs=[[{"secondary_y": False} for _ in range(3)] for _ in range(2)]
            )
            
            for i, col in enumerate(selected_columns):
                row = (i // 3) + 1
                col_num = (i % 3) + 1
                
                fig.add_trace(
                    go.Histogram(x=data[col], name=col, showlegend=False),
                    row=row, col=col_num
                )
            
            fig.update_layout(
                title="数据分布图",
                height=600,
                showlegend=False
            )
            
            return {
                'success': True,
                'chart_data': fig.to_json(),
                'chart_type': 'plotly'
            }
        else:
            # Matplotlib version
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            fig.suptitle('数据分布图', fontsize=16)
            
            for i, col in enumerate(selected_columns):
                row = i // 3
                col_num = i % 3
                axes[row, col_num].hist(data[col].dropna(), bins=30, alpha=0.7)
                axes[row, col_num].set_title(col)
                axes[row, col_num].set_xlabel('Value')
                axes[row, col_num].set_ylabel('Frequency')
            
            # Hide empty subplots
            for i in range(len(selected_columns), 6):
                row = i // 3
                col_num = i % 3
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
    
    def _generate_correlation_matrix(self, data, columns, chart_type):
        """Generate correlation matrix"""
        numeric_data = data.select_dtypes(include=[np.number])
        corr_matrix = numeric_data.corr()
        
        if chart_type == 'plotly':
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title="特征相关性矩阵",
                width=800,
                height=800
            )
            
            return {
                'success': True,
                'chart_data': fig.to_json(),
                'chart_type': 'plotly'
            }
        else:
            # Matplotlib version
            plt.figure(figsize=(12, 10))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": .5})
            plt.title('特征相关性矩阵')
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
                return {'success': False, 'message': '需要至少两个数值列来生成散点图'}
            x_col, y_col = numeric_cols[0], numeric_cols[1]
        
        if chart_type == 'plotly':
            fig = px.scatter(data, x=x_col, y=y_col, title=f'{x_col} vs {y_col}')
            fig.update_traces(marker=dict(size=8, opacity=0.7))
            
            return {
                'success': True,
                'chart_data': fig.to_json(),
                'chart_type': 'plotly'
            }
        else:
            # Matplotlib version
            plt.figure(figsize=(10, 6))
            plt.scatter(data[x_col], data[y_col], alpha=0.7)
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
        """Generate histograms"""
        return self._generate_distribution_plots(data, columns, chart_type)
    
    def _generate_box_plots(self, data, columns, chart_type):
        """Generate box plots"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        selected_columns = [col for col in columns if col in numeric_columns][:6]
        
        if chart_type == 'plotly':
            fig = go.Figure()
            
            for col in selected_columns:
                fig.add_trace(go.Box(y=data[col], name=col))
            
            fig.update_layout(
                title="箱线图",
                yaxis_title="Value",
                height=600
            )
            
            return {
                'success': True,
                'chart_data': fig.to_json(),
                'chart_type': 'plotly'
            }
        else:
            # Matplotlib version
            plt.figure(figsize=(12, 6))
            data[selected_columns].boxplot()
            plt.title('箱线图')
            plt.xticks(rotation=45)
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
                
                if chart_type == 'plotly':
                    fig = go.Figure()
                    
                    # Scatter plot
                    fig.add_trace(go.Scatter(
                        x=y_true,
                        y=y_pred,
                        mode='markers',
                        name='Predictions',
                        marker=dict(size=8, opacity=0.7)
                    ))
                    
                    # Perfect prediction line
                    min_val = min(y_true.min(), y_pred.min())
                    max_val = max(y_true.max(), y_pred.max())
                    fig.add_trace(go.Scatter(
                        x=[min_val, max_val],
                        y=[min_val, max_val],
                        mode='lines',
                        name='Perfect Prediction',
                        line=dict(color='red', dash='dash')
                    ))
                    
                    fig.update_layout(
                        title=f'预测值 vs 实际值 - {target_col}',
                        xaxis_title='实际值',
                        yaxis_title='预测值',
                        width=600,
                        height=500
                    )
                    
                    results[target_col] = {
                        'chart_data': fig.to_json(),
                        'chart_type': 'plotly'
                    }
                else:
                    # Matplotlib version
                    plt.figure(figsize=(8, 6))
                    plt.scatter(y_true, y_pred, alpha=0.7)
                    
                    # Perfect prediction line
                    min_val = min(y_true.min(), y_pred.min())
                    max_val = max(y_true.max(), y_pred.max())
                    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Prediction')
                    
                    plt.xlabel('实际值')
                    plt.ylabel('预测值')
                    plt.title(f'预测值 vs 实际值 - {target_col}')
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
                'message': '预测图生成完成'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'生成预测图失败: {str(e)}'}
    
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
                
                if chart_type == 'plotly':
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=y_pred,
                        y=residuals,
                        mode='markers',
                        name='Residuals',
                        marker=dict(size=8, opacity=0.7)
                    ))
                    
                    # Zero line
                    fig.add_hline(y=0, line_dash="dash", line_color="red")
                    
                    fig.update_layout(
                        title=f'残差图 - {target_col}',
                        xaxis_title='预测值',
                        yaxis_title='残差',
                        width=600,
                        height=500
                    )
                    
                    results[target_col] = {
                        'chart_data': fig.to_json(),
                        'chart_type': 'plotly'
                    }
                else:
                    # Matplotlib version
                    plt.figure(figsize=(8, 6))
                    plt.scatter(y_pred, residuals, alpha=0.7)
                    plt.axhline(y=0, color='r', linestyle='--')
                    plt.xlabel('预测值')
                    plt.ylabel('残差')
                    plt.title(f'残差图 - {target_col}')
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
                'message': '残差图生成完成'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'生成残差图失败: {str(e)}'}
    
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
                
                if chart_type == 'plotly':
                    fig = go.Figure(data=go.Bar(
                        x=importance_df['importance'],
                        y=importance_df['feature'],
                        orientation='h'
                    ))
                    
                    fig.update_layout(
                        title=f'特征重要性 - {target_col}',
                        xaxis_title='重要性',
                        yaxis_title='特征',
                        height=600,
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    
                    results[target_col] = {
                        'chart_data': fig.to_json(),
                        'chart_type': 'plotly',
                        'importance_data': importance_df.to_dict('records')
                    }
                else:
                    # Matplotlib version
                    plt.figure(figsize=(10, 8))
                    plt.barh(range(len(importance_df)), importance_df['importance'])
                    plt.yticks(range(len(importance_df)), importance_df['feature'])
                    plt.xlabel('重要性')
                    plt.title(f'特征重要性 - {target_col}')
                    plt.gca().invert_yaxis()
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
                return {'success': False, 'message': '模型不支持特征重要性分析'}
            
            return {
                'success': True,
                'results': results,
                'message': '特征重要性图生成完成'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'生成特征重要性图失败: {str(e)}'}
    
    def _generate_learning_curve(self, model_info, train_data, chart_type):
        """Generate learning curve (simplified version)"""
        # This is a placeholder for learning curve implementation
        # In a full implementation, you would track training history
        return {
            'success': False,
            'message': '学习曲线功能暂未实现，需要在训练过程中记录学习历史'
        } 