"""
Data Analysis Tools for Chat Interface
Provides file reading, data analysis, and visualization capabilities
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json
import io
import base64
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import tempfile
import os


class DataAnalyzer:
    """Handles data analysis and visualization tasks"""
    
    def __init__(self):
        self.data = None
        self.data_info = {}
        self.chart_counter = 0
        
        # Set matplotlib backend for server environments
        plt.switch_backend('Agg')
        
        # Configure seaborn style
        sns.set_style("whitegrid")
        plt.style.use('default')
    
    def load_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Load data from uploaded file
        
        Args:
            file_content: Raw file bytes
            filename: Original filename with extension
            
        Returns:
            Dictionary with success status and data info
        """
        try:
            file_ext = Path(filename).suffix.lower()
            
            if file_ext == '.csv':
                self.data = pd.read_csv(io.BytesIO(file_content))
            elif file_ext == '.json':
                json_data = json.loads(file_content.decode('utf-8'))
                if isinstance(json_data, list):
                    self.data = pd.DataFrame(json_data)
                elif isinstance(json_data, dict):
                    # Handle nested JSON structures
                    self.data = pd.json_normalize(json_data)
                else:
                    raise ValueError("JSON must contain array of objects or nested object")
            elif file_ext in ['.xlsx', '.xls']:
                # Read Excel file and handle potential issues
                self.data = pd.read_excel(io.BytesIO(file_content))
                
                # Remove completely empty rows and columns
                self.data = self.data.dropna(how='all')  # Remove rows where all values are NaN
                self.data = self.data.dropna(axis=1, how='all')  # Remove columns where all values are NaN
                
                # Find the actual data boundaries (ignore trailing empty cells common in Excel)
                if not self.data.empty:
                    # Find last row with actual data
                    last_data_row = self.data.last_valid_index()
                    if last_data_row is not None:
                        self.data = self.data.loc[:last_data_row]
                    
                    # Clean column names (remove unnamed columns that are empty)
                    unnamed_cols = [col for col in self.data.columns if 'Unnamed:' in str(col)]
                    for col in unnamed_cols:
                        if self.data[col].isna().all():
                            self.data = self.data.drop(columns=[col])
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Clean the data for JSON serialization
            self._clean_data_for_json()
            
            # Generate data summary
            self.data_info = self._analyze_data()
            
            return {
                "success": True,
                "filename": filename,
                "shape": self.data.shape,
                "columns": list(self.data.columns),
                "dtypes": self._safe_dtypes_dict(),
                "summary": self.data_info,
                "message": f"Successfully loaded {filename} with {self.data.shape[0]} rows and {self.data.shape[1]} columns."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to load {filename}: {str(e)}"
            }
    
    def _clean_data_for_json(self):
        """Clean data to ensure JSON serialization compatibility"""
        if self.data is None:
            return
        
        # Replace infinite values with NaN, then handle NaN values
        self.data = self.data.replace([np.inf, -np.inf], np.nan)
        
        # For numeric columns, we can optionally fill NaN with 0 or keep them as None
        # For now, we'll keep NaN as None for JSON serialization
        # The describe() and other methods will handle NaN appropriately
        
        # Clean column names - remove any characters that might cause issues
        new_columns = []
        for col in self.data.columns:
            # Convert to string and clean
            clean_col = str(col).strip()
            # Remove or replace problematic characters
            clean_col = clean_col.replace('\n', ' ').replace('\r', ' ')
            new_columns.append(clean_col)
        
        self.data.columns = new_columns
    
    def _safe_dtypes_dict(self) -> Dict[str, str]:
        """Create a JSON-safe dictionary of data types"""
        try:
            return {col: str(dtype) for col, dtype in self.data.dtypes.items()}
        except Exception:
            # Fallback to basic type information
            return {col: "unknown" for col in self.data.columns}
    
    def _safe_to_dict(self, series_or_df) -> Dict[str, Any]:
        """Safely convert pandas Series or DataFrame to dict for JSON serialization"""
        try:
            if hasattr(series_or_df, 'to_dict'):
                result = series_or_df.to_dict()
                
                # Clean the result dictionary
                cleaned_result = {}
                for key, value in result.items():
                    # Handle different types of values
                    if pd.isna(value) or value in [np.inf, -np.inf]:
                        cleaned_result[str(key)] = None
                    elif isinstance(value, (np.integer, np.floating)):
                        if np.isfinite(value):
                            cleaned_result[str(key)] = float(value) if isinstance(value, np.floating) else int(value)
                        else:
                            cleaned_result[str(key)] = None
                    elif isinstance(value, dict):
                        # For nested dictionaries (like from describe())
                        cleaned_result[str(key)] = self._safe_to_dict(pd.Series(value))
                    else:
                        cleaned_result[str(key)] = value
                
                return cleaned_result
            else:
                return {}
        except Exception:
            return {}
    
    def _analyze_data(self) -> Dict[str, Any]:
        """Generate comprehensive data analysis"""
        if self.data is None:
            return {}
        
        try:
            analysis = {
                "basic_info": {
                    "rows": int(len(self.data)),
                    "columns": int(len(self.data.columns)),
                    "memory_usage": f"{self.data.memory_usage(deep=True).sum() / 1024:.1f} KB"
                },
                "column_types": {
                    "numeric": list(self.data.select_dtypes(include=[np.number]).columns),
                    "categorical": list(self.data.select_dtypes(include=['object', 'category']).columns),
                    "datetime": list(self.data.select_dtypes(include=['datetime64']).columns)
                },
                "missing_values": self._safe_to_dict(self.data.isnull().sum()),
                "numeric_summary": {}
            }
            
            # Add numeric summary for numeric columns
            numeric_cols = analysis["column_types"]["numeric"]
            if numeric_cols:
                try:
                    describe_result = self.data[numeric_cols].describe()
                    analysis["numeric_summary"] = self._safe_to_dict(describe_result)
                except Exception:
                    analysis["numeric_summary"] = {"error": "Could not generate numeric summary"}
            
            return analysis
            
        except Exception as e:
            return {"error": f"Error analyzing data: {str(e)}"}
    
    def query_data(self, query: str) -> Dict[str, Any]:
        """
        Answer questions about the data
        
        Args:
            query: Natural language question about the data
            
        Returns:
            Dictionary with analysis results
        """
        if self.data is None:
            return {"error": "No data loaded. Please upload a file first."}
        
        try:
            query_lower = query.lower()
            results = {"query": query, "results": []}
            
            # Basic data info queries
            if any(phrase in query_lower for phrase in ['how many rows', 'number of rows', 'row count']):
                results["results"].append(f"The dataset has {len(self.data)} rows.")
            
            if any(phrase in query_lower for phrase in ['how many columns', 'number of columns', 'column count']):
                results["results"].append(f"The dataset has {len(self.data.columns)} columns.")
            
            if any(phrase in query_lower for phrase in ['column names', 'what columns', 'list columns']):
                results["results"].append(f"Columns: {', '.join(self.data.columns)}")
            
            if any(phrase in query_lower for phrase in ['data types', 'column types', 'dtypes']):
                type_info = []
                for col, dtype in self.data.dtypes.items():
                    type_info.append(f"{col}: {dtype}")
                results["results"].append("Data types:\n" + "\n".join(type_info))
            
            # Missing values
            if any(phrase in query_lower for phrase in ['missing values', 'null values', 'missing data']):
                missing = self.data.isnull().sum()
                missing_info = missing[missing > 0]
                if len(missing_info) > 0:
                    missing_dict = self._safe_to_dict(missing_info)
                    missing_str = "\n".join([f"{k}: {v}" for k, v in missing_dict.items()])
                    results["results"].append(f"Missing values:\n{missing_str}")
                else:
                    results["results"].append("No missing values found in the dataset.")
            
            # Summary statistics
            if any(phrase in query_lower for phrase in ['summary', 'describe', 'statistics', 'stats']):
                numeric_cols = self.data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    try:
                        summary = self.data[numeric_cols].describe()
                        # Convert to string representation safely
                        results["results"].append(f"Summary statistics:\n{summary.to_string()}")
                    except Exception:
                        results["results"].append("Could not generate summary statistics.")
                else:
                    results["results"].append("No numeric columns found for summary statistics.")
            
            # Unique values
            if any(phrase in query_lower for phrase in ['unique values', 'unique count', 'distinct']):
                unique_counts = []
                for col in self.data.columns:
                    try:
                        unique_count = self.data[col].nunique()
                        unique_counts.append(f"{col}: {unique_count} unique values")
                    except Exception:
                        unique_counts.append(f"{col}: Could not count unique values")
                results["results"].append("Unique value counts:\n" + "\n".join(unique_counts))
            
            # Data head/sample
            if any(phrase in query_lower for phrase in ['show data', 'first few rows', 'sample', 'head']):
                try:
                    sample_data = self.data.head().to_string()
                    results["results"].append(f"First 5 rows:\n{sample_data}")
                except Exception:
                    results["results"].append("Could not display sample data due to formatting issues.")
            
            if not results["results"]:
                results["results"].append("I understand you want to know about the data. Could you be more specific? You can ask about:\n- Row/column counts\n- Data types\n- Missing values\n- Summary statistics\n- Sample data\n- Unique values")
            
            return results
            
        except Exception as e:
            return {"error": f"Error analyzing data: {str(e)}"}
    
    def create_visualization(self, chart_type: str, **kwargs) -> Dict[str, Any]:
        """
        Create data visualizations
        
        Args:
            chart_type: Type of chart to create
            **kwargs: Chart-specific parameters
            
        Returns:
            Dictionary with chart data and metadata
        """
        if self.data is None:
            return {"error": "No data loaded. Please upload a file first."}
        
        try:
            self.chart_counter += 1
            chart_id = f"chart_{self.chart_counter}"
            
            if chart_type == "histogram":
                return self._create_histogram(chart_id, **kwargs)
            elif chart_type == "scatter":
                return self._create_scatter(chart_id, **kwargs)
            elif chart_type == "bar":
                return self._create_bar_chart(chart_id, **kwargs)
            elif chart_type == "line":
                return self._create_line_chart(chart_id, **kwargs)
            elif chart_type == "correlation":
                return self._create_correlation_heatmap(chart_id, **kwargs)
            elif chart_type == "box":
                return self._create_box_plot(chart_id, **kwargs)
            else:
                return {"error": f"Unsupported chart type: {chart_type}"}
                
        except Exception as e:
            return {"error": f"Error creating visualization: {str(e)}"}
    
    def _create_histogram(self, chart_id: str, column: str = None, bins: int = 30) -> Dict[str, Any]:
        """Create histogram using Plotly"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if not column:
            if len(numeric_cols) == 0:
                return {"error": "No numeric columns available for histogram"}
            column = numeric_cols[0]
        
        if column not in self.data.columns:
            return {"error": f"Column '{column}' not found"}
        
        fig = px.histogram(self.data, x=column, nbins=bins, 
                          title=f"Distribution of {column}")
        fig.update_layout(showlegend=False)
        
        return {
            "chart_id": chart_id,
            "chart_type": "histogram",
            "plotly_json": fig.to_json(),
            "title": f"Distribution of {column}",
            "description": f"Histogram showing the distribution of values in column '{column}'"
        }
    
    def _create_scatter(self, chart_id: str, x_col: str = None, y_col: str = None, 
                       color_col: str = None) -> Dict[str, Any]:
        """Create scatter plot using Plotly"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {"error": "Need at least 2 numeric columns for scatter plot"}
        
        if not x_col:
            x_col = numeric_cols[0]
        if not y_col:
            y_col = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
        
        kwargs = {"x": x_col, "y": y_col, "title": f"{x_col} vs {y_col}"}
        if color_col and color_col in self.data.columns:
            kwargs["color"] = color_col
        
        fig = px.scatter(self.data, **kwargs)
        
        return {
            "chart_id": chart_id,
            "chart_type": "scatter",
            "plotly_json": fig.to_json(),
            "title": f"{x_col} vs {y_col}",
            "description": f"Scatter plot showing relationship between {x_col} and {y_col}"
        }
    
    def _create_bar_chart(self, chart_id: str, x_col: str = None, y_col: str = None) -> Dict[str, Any]:
        """Create bar chart using Plotly"""
        categorical_cols = self.data.select_dtypes(include=['object', 'category']).columns
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if not x_col:
            if len(categorical_cols) > 0:
                x_col = categorical_cols[0]
            else:
                return {"error": "No categorical columns available for bar chart"}
        
        if not y_col:
            if len(numeric_cols) > 0:
                # Aggregate data by x_col
                agg_data = self.data.groupby(x_col)[numeric_cols[0]].mean().reset_index()
                fig = px.bar(agg_data, x=x_col, y=numeric_cols[0], 
                           title=f"Average {numeric_cols[0]} by {x_col}")
            else:
                # Count values in categorical column
                value_counts = self.data[x_col].value_counts().reset_index()
                value_counts.columns = [x_col, 'count']
                fig = px.bar(value_counts, x=x_col, y='count', 
                           title=f"Count of {x_col}")
        else:
            fig = px.bar(self.data, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
        
        return {
            "chart_id": chart_id,
            "chart_type": "bar",
            "plotly_json": fig.to_json(),
            "title": fig.layout.title.text,
            "description": f"Bar chart showing {x_col} data"
        }
    
    def _create_line_chart(self, chart_id: str, x_col: str = None, y_col: str = None) -> Dict[str, Any]:
        """Create line chart using Plotly"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 1:
            return {"error": "Need at least 1 numeric column for line chart"}
        
        if not x_col:
            x_col = self.data.columns[0]  # Use first column as x-axis
        if not y_col:
            y_col = numeric_cols[0]
        
        fig = px.line(self.data, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
        
        return {
            "chart_id": chart_id,
            "chart_type": "line",
            "plotly_json": fig.to_json(),
            "title": f"{y_col} over {x_col}",
            "description": f"Line chart showing {y_col} trends over {x_col}"
        }
    
    def _create_correlation_heatmap(self, chart_id: str) -> Dict[str, Any]:
        """Create correlation heatmap using Plotly"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {"error": "Need at least 2 numeric columns for correlation matrix"}
        
        corr_matrix = self.data[numeric_cols].corr()
        
        fig = px.imshow(corr_matrix, 
                       x=corr_matrix.columns, 
                       y=corr_matrix.columns,
                       color_continuous_scale='RdBu_r',
                       title="Correlation Matrix")
        
        return {
            "chart_id": chart_id,
            "chart_type": "correlation",
            "plotly_json": fig.to_json(),
            "title": "Correlation Matrix",
            "description": "Heatmap showing correlations between numeric variables"
        }
    
    def _create_box_plot(self, chart_id: str, column: str = None, group_by: str = None) -> Dict[str, Any]:
        """Create box plot using Plotly"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if not column:
            if len(numeric_cols) == 0:
                return {"error": "No numeric columns available for box plot"}
            column = numeric_cols[0]
        
        kwargs = {"y": column, "title": f"Box Plot of {column}"}
        if group_by and group_by in self.data.columns:
            kwargs["x"] = group_by
            kwargs["title"] = f"Box Plot of {column} by {group_by}"
        
        fig = px.box(self.data, **kwargs)
        
        return {
            "chart_id": chart_id,
            "chart_type": "box",
            "plotly_json": fig.to_json(),
            "title": fig.layout.title.text,
            "description": f"Box plot showing distribution of {column}"
        }
    
    def get_chart_suggestions(self) -> List[Dict[str, Any]]:
        """Get suggested charts based on data types"""
        if self.data is None:
            return []
        
        suggestions = []
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        categorical_cols = self.data.select_dtypes(include=['object', 'category']).columns
        
        # Histogram for numeric columns
        if len(numeric_cols) > 0:
            suggestions.append({
                "type": "histogram",
                "title": f"Distribution of {numeric_cols[0]}",
                "description": "Show the distribution of values",
                "params": {"column": numeric_cols[0]}
            })
        
        # Scatter plot for numeric columns
        if len(numeric_cols) >= 2:
            suggestions.append({
                "type": "scatter",
                "title": f"{numeric_cols[0]} vs {numeric_cols[1]}",
                "description": "Show relationship between variables",
                "params": {"x_col": numeric_cols[0], "y_col": numeric_cols[1]}
            })
        
        # Bar chart for categorical data
        if len(categorical_cols) > 0:
            suggestions.append({
                "type": "bar",
                "title": f"Count by {categorical_cols[0]}",
                "description": "Show distribution of categories",
                "params": {"x_col": categorical_cols[0]}
            })
        
        # Correlation matrix for multiple numeric columns
        if len(numeric_cols) >= 3:
            suggestions.append({
                "type": "correlation",
                "title": "Correlation Matrix",
                "description": "Show correlations between variables",
                "params": {}
            })
        
        return suggestions


# Global analyzer instance
data_analyzer = DataAnalyzer()
