import ast
import pandas as pd

def safe_eval_pandas(query: str, df):
    """Safe evaluation of pandas queries with proper validation"""
    try:
        # Parse the query
        tree = ast.parse(query, mode="eval")
        
        # Check for dangerous operations but allow standard pandas operations
        for node in ast.walk(tree):
            # Block imports and dangerous function calls
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise ValueError("Import statements are not allowed")
            
            # Block dangerous function calls but allow pandas methods
            if isinstance(node, ast.Call):
                # Allow pandas DataFrame methods
                if isinstance(node.func, ast.Attribute):
                    continue  # Allow method calls on objects
                # Block standalone function calls like __import__, eval, exec
                elif isinstance(node.func, ast.Name):
                    dangerous_funcs = {'__import__', 'eval', 'exec', 'open', 'input'}
                    if node.func.id in dangerous_funcs:
                        raise ValueError(f"Dangerous function call: {node.func.id}")
            
            # Block access to dangerous attributes
            if isinstance(node, ast.Attribute):
                dangerous_attrs = {'__class__', '__bases__', '__subclasses__', '__globals__'}
                if node.attr in dangerous_attrs:
                    raise ValueError(f"Dangerous attribute access: {node.attr}")
        
        # Execute with restricted globals - only provide df and pandas
        safe_globals = {"df": df, "pd": pd, "__builtins__": {}}
        return eval(compile(tree, "<string>", "eval"), safe_globals, {})
        
    except SyntaxError as e:
        raise ValueError(f"Invalid syntax in pandas query: {str(e)}")
    except Exception as e:
        raise ValueError(f"Query execution failed: {str(e)}")
