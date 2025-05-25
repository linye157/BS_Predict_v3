from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import io
import joblib
from pathlib import Path
from datetime import datetime
import json

# Import modules
from modules.data_processing import DataProcessingService
from modules.machine_learning import MachineLearningService
from modules.stacking_ensemble import StackingEnsembleService
from modules.auto_ml import AutoMLService
from modules.visualization import VisualizationService
from modules.report import ReportService

app = Flask(__name__)
# 增强CORS配置，允许所有头信息和方法
CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": "*", "methods": "*", "expose_headers": "*", "supports_credentials": True}})

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'data'
app.config['MODELS_FOLDER'] = 'models'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['DATA_FOLDER'], 
               app.config['MODELS_FOLDER'], app.config['REPORTS_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Initialize services
data_service = DataProcessingService()
ml_service = MachineLearningService()
stacking_service = StackingEnsembleService()
automl_service = AutoMLService()
viz_service = VisualizationService()
report_service = ReportService()

# Global state storage (in production, use Redis or database)
app_state = {
    'train_data': None,
    'test_data': None,
    'models': {},
    'current_model': None,
    'preprocessing_params': {},
    'training_history': []
}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Data Processing endpoints
@app.route('/api/data/load-default', methods=['POST'])
def load_default_data():
    """Load default training and testing data"""
    try:
        result = data_service.load_default_data()
        if result['success']:
            # 存储DataFrame到app_state
            if 'train_data' in result:
                app_state['train_data'] = result['train_data']
            if 'test_data' in result:
                app_state['test_data'] = result['test_data']
            
            # 从result中移除DataFrame对象，只返回消息
            response = {
                'success': result['success'],
                'message': result['message']
            }
        else:
            response = result
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/data/upload', methods=['POST'])
def upload_data():
    """Upload custom dataset"""
    try:
        files = request.files
        result = data_service.upload_data(files)
        if result['success']:
            # 存储DataFrame到app_state
            if 'train_data' in result:
                app_state['train_data'] = result['train_data']
            if 'test_data' in result:
                app_state['test_data'] = result['test_data']
            
            # 从result中移除DataFrame对象，只返回消息
            response = {
                'success': result['success'],
                'message': result['message']
            }
        else:
            response = result
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/data/preview', methods=['GET'])
def preview_data():
    """Get data preview and statistics"""
    try:
        result = data_service.get_data_preview(
            app_state['train_data'], 
            app_state['test_data']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/data/preprocess', methods=['POST'])
def preprocess_data():
    """Apply data preprocessing"""
    try:
        # 支持两种请求格式：JSON和表单
        if request.is_json:
            params = request.get_json()
        else:
            # 尝试从表单数据中获取参数
            form_data = request.form.get('data')
            if form_data:
                params = json.loads(form_data)
            else:
                return jsonify({'success': False, 'message': '无效的请求格式'}), 400
        
        print(f"接收到预处理参数: {params}")
        
        result = data_service.preprocess_data(
            app_state['train_data'], 
            app_state['test_data'], 
            params
        )
        if result['success']:
            # 存储DataFrame到app_state
            if 'train_data' in result:
                app_state['train_data'] = result['train_data']
            if 'test_data' in result:
                app_state['test_data'] = result['test_data']
            app_state['preprocessing_params'] = params
            
            # 从result中移除DataFrame对象，只返回消息
            response = {
                'success': result['success'],
                'message': result['message']
            }
        else:
            response = result
        
        return jsonify(response)
    except Exception as e:
        print(f"预处理错误: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/data/download/<data_type>/<file_format>', methods=['GET'])
def download_data(data_type, file_format):
    """Download data in specified format"""
    try:
        data = app_state.get(f'{data_type}_data')
        if data is None:
            return jsonify({'error': f'No {data_type} data available'}), 404
            
        result = data_service.convert_data_for_download(data, file_format)
        if result['success']:
            return send_file(
                io.BytesIO(result['data']),
                as_attachment=True,
                download_name=f'{data_type}_data.{file_format}',
                mimetype=result['mimetype']
            )
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Machine Learning endpoints
@app.route('/api/ml/models', methods=['GET'])
def get_available_models():
    """Get list of available ML models"""
    return jsonify(ml_service.get_available_models())

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle large payload errors"""
    print("请求数据过大")
    return jsonify({
        'success': False,
        'message': 'Request entity too large, max allowed size is 100MB'
    }), 413

@app.route('/api/ml/train', methods=['POST'])
def train_model():
    """Train a machine learning model"""
    print("======= 收到训练请求 =======")
    try:
        params = request.get_json()
        if params is None:
            print("无法解析JSON数据")
            return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400
            
        print(f"收到训练请求参数: {params}")
        
        if app_state['train_data'] is None:
            print("训练失败: 没有训练数据")
            return jsonify({'success': False, 'message': 'No training data available'}), 400
            
        if 'model_type' not in params:
            print("训练失败: 未指定模型类型")
            return jsonify({'success': False, 'message': 'Model type not specified'}), 400
            
        if 'target_columns' not in params or not params['target_columns']:
            print("训练失败: 未指定目标列")
            return jsonify({'success': False, 'message': 'Target columns not specified'}), 400
        
        print(f"训练数据形状: {app_state['train_data'].shape}")
        print(f"选择的模型: {params.get('model_type')}")
        print(f"目标列: {params.get('target_columns')}")
        
        result = ml_service.train_model(
            app_state['train_data'],
            params
        )
        
        if result['success']:
            model_id = result['model_id']
            # 存储完整的模型信息到app_state（包含模型对象）
            app_state['models'][model_id] = result['model']
            app_state['current_model'] = model_id
            app_state['training_history'].append({
                'timestamp': datetime.now().isoformat(),
                'model_type': params.get('model_type'),
                'model_id': model_id,
                'metrics': result.get('metrics', {})
            })
            print(f"模型训练成功: {model_id}")
            
            # 创建JSON可序列化的响应（移除模型对象）
            json_result = result.copy()
            if 'model' in json_result:
                del json_result['model']  # 移除不可序列化的模型对象
        else:
            print(f"模型训练失败: {result.get('message', '未知错误')}")
            json_result = result
        
        return jsonify(json_result)
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"模型训练异常: {error_msg}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': error_msg}), 500

@app.route('/api/ml/predict', methods=['POST'])
def predict():
    """Make predictions with trained model"""
    try:
        params = request.get_json()
        model_id = params.get('model_id') or app_state.get('current_model')
        
        if not model_id or model_id not in app_state['models']:
            return jsonify({'success': False, 'message': 'No trained model available'}), 400
            
        test_data = app_state.get('test_data')
        if test_data is None:
            return jsonify({'success': False, 'message': 'No test data available'}), 400
            
        result = ml_service.predict(
            app_state['models'][model_id],
            test_data,
            params
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ml/evaluate', methods=['POST'])
def evaluate_model():
    """Evaluate model performance"""
    try:
        params = request.get_json()
        model_id = params.get('model_id') or app_state.get('current_model')
        
        if not model_id or model_id not in app_state['models']:
            return jsonify({'success': False, 'message': 'No trained model available'}), 400
            
        result = ml_service.evaluate_model(
            app_state['models'][model_id],
            app_state['test_data'],
            params
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Stacking Ensemble endpoints
@app.route('/api/stacking/train', methods=['POST'])
def train_stacking():
    """Train stacking ensemble model"""
    try:
        params = request.get_json()
        if app_state['train_data'] is None:
            return jsonify({'success': False, 'message': 'No training data available'}), 400
            
        result = stacking_service.train_stacking_ensemble(
            app_state['train_data'],
            params
        )
        
        if result['success']:
            model_id = result['model_id']
            app_state['models'][model_id] = result['model']
            app_state['current_model'] = model_id
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# AutoML endpoints
@app.route('/api/automl/run', methods=['POST'])
def run_automl():
    """Run automated machine learning"""
    try:
        params = request.get_json()
        if app_state['train_data'] is None:
            return jsonify({'success': False, 'message': 'No training data available'}), 400
            
        result = automl_service.run_automl(
            app_state['train_data'],
            app_state.get('test_data'),
            params
        )
        
        if result['success']:
            model_id = result['model_id']
            app_state['models'][model_id] = result['model']
            app_state['current_model'] = model_id
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Visualization endpoints
@app.route('/api/visualization/data', methods=['POST'])
def generate_data_visualization():
    """Generate data visualization"""
    try:
        params = request.get_json()
        data = app_state.get(f"{params.get('data_type', 'train')}_data")
        
        if data is None:
            return jsonify({'success': False, 'message': 'No data available'}), 400
            
        result = viz_service.generate_data_visualization(data, params)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/visualization/model', methods=['POST'])
def generate_model_visualization():
    """Generate model visualization"""
    try:
        params = request.get_json()
        model_id = params.get('model_id') or app_state.get('current_model')
        
        if not model_id or model_id not in app_state['models']:
            return jsonify({'success': False, 'message': 'No trained model available'}), 400
            
        result = viz_service.generate_model_visualization(
            app_state['models'][model_id],
            app_state['train_data'],
            params
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Report endpoints
@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate analysis report"""
    try:
        params = request.get_json()
        model_id = params.get('model_id') or app_state.get('current_model')
        
        result = report_service.generate_report(
            app_state['train_data'],
            app_state['test_data'],
            app_state['models'].get(model_id) if model_id else None,
            app_state['training_history'],
            params
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reports/download/<report_id>/<file_format>', methods=['GET'])
def download_report(report_id, file_format):
    """Download report in specified format"""
    try:
        result = report_service.download_report(report_id, file_format)
        if result['success']:
            return send_file(
                result['file_path'],
                as_attachment=True,
                download_name=result['filename']
            )
        else:
            return jsonify(result), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# System status endpoints
@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Get current system status"""
    status = {
        'train_data_loaded': app_state['train_data'] is not None,
        'test_data_loaded': app_state['test_data'] is not None,
        'trained_models': len(app_state['models']),
        'current_model': app_state['current_model'],
        'training_history': len(app_state['training_history'])
    }
    
    if app_state['train_data'] is not None:
        status['train_data_shape'] = app_state['train_data'].shape
    if app_state['test_data'] is not None:
        status['test_data_shape'] = app_state['test_data'].shape
        
    return jsonify(status)

# 特别处理OPTIONS请求
@app.route('/api/data/upload', methods=['OPTIONS'])
def options_upload():
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response

# 特别处理预处理OPTIONS请求
@app.route('/api/data/preprocess', methods=['OPTIONS'])
def options_preprocess():
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response

# 特别处理预览OPTIONS请求
@app.route('/api/data/preview', methods=['OPTIONS'])
def options_preview():
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

# 特别处理模型训练OPTIONS请求
@app.route('/api/ml/train', methods=['OPTIONS'])
def options_ml_train():
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

# 特别处理模型预测OPTIONS请求
@app.route('/api/ml/predict', methods=['OPTIONS'])
def options_ml_predict():
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

# 特别处理模型评估OPTIONS请求
@app.route('/api/ml/evaluate', methods=['OPTIONS'])
def options_ml_evaluate():
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

# 特别处理模型列表OPTIONS请求
@app.route('/api/ml/models', methods=['OPTIONS'])
def options_ml_models():
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

# 通用OPTIONS处理，捕获所有API路径的预检请求
@app.route('/api/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')  # 缓存预检请求结果1小时
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 