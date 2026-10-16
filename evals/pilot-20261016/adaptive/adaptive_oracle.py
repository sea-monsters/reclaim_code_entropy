"""Independent trusted-fixture probes for the two adaptive-routing tasks."""
import ast
import importlib.util
import itertools
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
kind,root=sys.argv[1],Path(sys.argv[2]).resolve()
spec=importlib.util.spec_from_file_location('adaptive_app',root/'app.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
if kind=='leaf':
    for value in (0,1,-3,'旧',None):assert m.format_id(value)=='item-'+str(value)
    defs={n.name for n in ast.walk(ast.parse((root/'app.py').read_text())) if isinstance(n,ast.FunctionDef)}
    assert '_old_label' not in defs
    result={'behavior':'passed','private_cut_completed':True}
elif kind=='boundary':
    traces=0
    for size in range(6):
        for actions in itertools.product(('begin','stop','finish'),repeat=size):
            d=m.Dispatcher();admissions_open=True;inflight=0
            assert d.released is False
            for action in actions:
                expected_error=None
                if action=='begin':
                    if not admissions_open:expected_error='closed'
                    else:inflight+=1
                elif action=='stop':admissions_open=False
                elif not inflight:expected_error='empty'
                else:inflight-=1
                try:getattr(d,action)()
                except RuntimeError as exc:assert str(exc)==expected_error,(actions,action,str(exc),expected_error)
                else:assert expected_error is None,(actions,action,'missing error')
                assert d.released is (not admissions_open and inflight==0),(actions,action)
            traces+=1
    result={'behavior':'passed','traces_checked':traces,'max_trace_length':5,'concurrency_proof':False}
else:raise ValueError(kind)
print(json.dumps(result,indent=2))
