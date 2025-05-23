import pandas as pd
import numpy as np
import io
import os
from pathlib import Path
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

class DataProcessingService:
    def __init__(self):
        self.train_data_path = Path("data/train_data.xlsx")
        self.test_data_path = Path("data/test_data.xlsx")
    
    def load_default_data(self):
        """Load the default training and testing data"""
        try:
            result = {'success': True, 'message': ''}
            
            if self.train_data_path.exists():
                train_data = pd.read_excel(self.train_data_path)
                result['train_data'] = train_data
                result['message'] += f"训练数据加载成功: {train_data.shape[0]} 行, {train_data.shape[1]} 列. "
            else:
                result['message'] += f"未找到默认训练数据文件: {self.train_data_path}. "
                
            if self.test_data_path.exists():
                test_data = pd.read_excel(self.test_data_path)
                result['test_data'] = test_data
                result['message'] += f"测试数据加载成功: {test_data.shape[0]} 行, {test_data.shape[1]} 列. "
            else:
                result['message'] += f"未找到默认测试数据文件: {self.test_data_path}. "
                
            return result
        except Exception as e:
            return {'success': False, 'message': f'加载数据时出错: {str(e)}'}
    
    def upload_data(self, files):
        """Upload custom dataset"""
        result = {'success': True, 'message': ''}
        
        try:
            if 'train_file' in files:
                train_file = files['train_file']
                if train_file.filename.endswith('.csv'):
                    train_data = pd.read_csv(train_file)
                else:
                    train_data = pd.read_excel(train_file)
                
                result['train_data'] = train_data
                result['message'] += f"训练数据上传成功: {train_data.shape[0]} 行, {train_data.shape[1]} 列. "
            
            if 'test_file' in files:
                test_file = files['test_file']
                if test_file.filename.endswith('.csv'):
                    test_data = pd.read_csv(test_file)
                else:
                    test_data = pd.read_excel(test_file)
                
                result['test_data'] = test_data
                result['message'] += f"测试数据上传成功: {test_data.shape[0]} 行, {test_data.shape[1]} 列. "
                
            return result
        except Exception as e:
            return {'success': False, 'message': f'上传数据时出错: {str(e)}'}
    
    def get_data_preview(self, train_data, test_data):
        """Get data preview and statistics"""
        result = {'success': True}
        
        try:
            if train_data is not None:
                result['train_preview'] = {
                    'shape': train_data.shape,
                    'head': train_data.head(10).to_dict('records'),
                    'columns': train_data.columns.tolist(),
                    'dtypes': train_data.dtypes.to_dict(),
                    'description': train_data.describe().to_dict(),
                    'missing_values': train_data.isnull().sum().to_dict(),
                    'missing_percentage': (train_data.isnull().sum() / len(train_data) * 100).to_dict()
                }
            
            if test_data is not None:
                result['test_preview'] = {
                    'shape': test_data.shape,
                    'head': test_data.head(10).to_dict('records'),
                    'columns': test_data.columns.tolist(),
                    'dtypes': test_data.dtypes.to_dict(),
                    'description': test_data.describe().to_dict(),
                    'missing_values': test_data.isnull().sum().to_dict(),
                    'missing_percentage': (test_data.isnull().sum() / len(test_data) * 100).to_dict()
                }
            
            return result
        except Exception as e:
            return {'success': False, 'message': f'获取数据预览时出错: {str(e)}'}
    
    def preprocess_data(self, train_data, test_data, params):
        """Apply data preprocessing"""
        try:
            result = {'success': True, 'message': '数据预处理完成'}
            
            # Copy data to avoid modifying original
            if train_data is not None:
                processed_train = train_data.copy()
            else:
                processed_train = None
                
            if test_data is not None:
                processed_test = test_data.copy()
            else:
                processed_test = None
            
            preprocess_methods = params.get('methods', [])
            
            # Handle missing values
            if '填充缺失值' in preprocess_methods:
                fill_method = params.get('fill_method', '均值填充')
                fixed_value = params.get('fixed_value', 0.0)
                
                if processed_train is not None:
                    processed_train = self._fill_missing_values(processed_train, fill_method, fixed_value)
                if processed_test is not None:
                    processed_test = self._fill_missing_values(processed_test, fill_method, fixed_value)
            
            # Feature standardization
            if '特征标准化' in preprocess_methods:
                if processed_train is not None and processed_test is not None:
                    processed_train, processed_test = self._standardize_features(processed_train, processed_test)
                elif processed_train is not None:
                    processed_train = self._standardize_features(processed_train)
            
            # Feature normalization
            if '特征归一化' in preprocess_methods:
                if processed_train is not None and processed_test is not None:
                    processed_train, processed_test = self._normalize_features(processed_train, processed_test)
                elif processed_train is not None:
                    processed_train = self._normalize_features(processed_train)
            
            # Outlier handling
            if '异常值处理' in preprocess_methods:
                outlier_method = params.get('outlier_method', 'IQR')
                if processed_train is not None:
                    processed_train = self._handle_outliers(processed_train, outlier_method)
                if processed_test is not None:
                    processed_test = self._handle_outliers(processed_test, outlier_method)
            
            result['train_data'] = processed_train
            result['test_data'] = processed_test
            
            return result
        except Exception as e:
            return {'success': False, 'message': f'数据预处理时出错: {str(e)}'}
    
    def convert_data_for_download(self, data, file_format):
        """Convert data for download"""
        try:
            if file_format == 'csv':
                output = io.StringIO()
                data.to_csv(output, index=False, encoding='utf-8-sig')
                return {
                    'success': True,
                    'data': output.getvalue().encode('utf-8-sig'),
                    'mimetype': 'text/csv'
                }
            elif file_format == 'xlsx':
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    data.to_excel(writer, index=False)
                return {
                    'success': True,
                    'data': output.getvalue(),
                    'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                }
            else:
                return {'success': False, 'message': '不支持的文件格式'}
        except Exception as e:
            return {'success': False, 'message': f'转换数据时出错: {str(e)}'}
    
    def _fill_missing_values(self, df, method, fixed_value=None):
        """Fill missing values in dataframe"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if method == '均值填充':
            df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
        elif method == '中位数填充':
            df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
        elif method == '众数填充':
            for col in numeric_columns:
                mode_value = df[col].mode()
                if not mode_value.empty:
                    df[col] = df[col].fillna(mode_value[0])
        elif method == '固定值填充':
            df[numeric_columns] = df[numeric_columns].fillna(fixed_value)
        
        # Fill non-numeric columns with mode
        non_numeric_columns = df.select_dtypes(exclude=[np.number]).columns
        for col in non_numeric_columns:
            mode_value = df[col].mode()
            if not mode_value.empty:
                df[col] = df[col].fillna(mode_value[0])
        
        return df
    
    def _standardize_features(self, train_df, test_df=None):
        """Standardize features using StandardScaler"""
        # Only standardize numeric columns
        numeric_columns = train_df.select_dtypes(include=[np.number]).columns
        
        scaler = StandardScaler()
        train_scaled = train_df.copy()
        train_scaled[numeric_columns] = scaler.fit_transform(train_df[numeric_columns])
        
        if test_df is not None:
            test_scaled = test_df.copy()
            test_scaled[numeric_columns] = scaler.transform(test_df[numeric_columns])
            return train_scaled, test_scaled
        else:
            return train_scaled
    
    def _normalize_features(self, train_df, test_df=None):
        """Normalize features using MinMaxScaler"""
        # Only normalize numeric columns
        numeric_columns = train_df.select_dtypes(include=[np.number]).columns
        
        scaler = MinMaxScaler()
        train_normalized = train_df.copy()
        train_normalized[numeric_columns] = scaler.fit_transform(train_df[numeric_columns])
        
        if test_df is not None:
            test_normalized = test_df.copy()
            test_normalized[numeric_columns] = scaler.transform(test_df[numeric_columns])
            return train_normalized, test_normalized
        else:
            return train_normalized
    
    def _handle_outliers(self, df, method):
        """Handle outliers in dataframe"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df_cleaned = df.copy()
        
        if method == 'IQR':
            for col in numeric_columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Cap outliers
                df_cleaned[col] = df_cleaned[col].clip(lower=lower_bound, upper=upper_bound)
        
        elif method == 'Z-Score':
            for col in numeric_columns:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                df_cleaned = df_cleaned[z_scores < 3]
        
        elif method == 'Percentile':
            for col in numeric_columns:
                lower_bound = df[col].quantile(0.05)
                upper_bound = df[col].quantile(0.95)
                df_cleaned[col] = df_cleaned[col].clip(lower=lower_bound, upper=upper_bound)
        
        return df_cleaned 