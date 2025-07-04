# prompts package: Contains all MCP Prompt templates
# Using lazy imports to avoid circular dependency issues

__all__ = ['pr_prompts', 'ci_prompts', 'review_prompts']

def _import_all():
    """Lazy import all modules when needed."""
    import pkgutil
    import importlib
    
    for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
        if module_name in __all__:
            module = importlib.import_module(f"{__name__}.{module_name}")
            globals()[module_name] = module

# Only import when the package is actually used
import sys
if not hasattr(sys, '_prompts_imported'):
    _import_all()
    sys._prompts_imported = True 