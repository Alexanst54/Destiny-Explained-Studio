"""Explicit local model modules. Foreign IDs cannot rename another boss's geometry."""
import importlib,re
from .registry import implementations

def load(entity_id):
    entry=implementations().get(entity_id)
    if not entry or entry['provider']!='universal':raise ValueError('No dedicated universal provider for '+entity_id)
    name=entry.get('module','')
    if not re.fullmatch(r'universal\.[a-z][a-z0-9_]*',name):raise ValueError('Invalid local provider module')
    module=importlib.import_module(name)
    if entity_id not in module.SUPPORTED_ENTITIES:raise ValueError('Provider does not author this Atlas identity')
    if not all(callable(getattr(module,k,None)) for k in ['setup','generate','arena','pose','camera']):raise ValueError('Incomplete provider protocol')
    return module
