from typing import List, Dict, Any
from agno.workflow import Step


def extract_step_info(obj: Any) -> List[Dict[str, Any]]:
    """
    递归提取所有 Step 类型实例的信息
    """
    results = {}

    # 判断是否为 Step 类型
    if isinstance(obj, Step):
        name = getattr(obj, 'name', None)
        agent = getattr(obj, 'agent', None) and 'agent'
        team = getattr(obj, 'team', None) and 'team'
        executor = getattr(obj, 'executor', None) and 'executor'
        results[name] = agent or team or executor

    # 如果有 steps 属性，递归处理
    if hasattr(obj, 'steps'):
        steps = obj.steps
        if isinstance(steps, (list, tuple)):
            for step in steps:
                results = {**results, **extract_step_info(step)}

    return results
