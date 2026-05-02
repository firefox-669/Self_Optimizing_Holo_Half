"""
SOHH 安全评估 API 服务器

提供REST API接口用于Agent安全评估
基于 FastAPI 构建
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# 添加插件路径
sys.path.insert(0, str(Path(__file__).parent / "plugins"))

from security_assessor import (
    calculate_security_score,
    get_security_assessment_report,
    verify_skill,
    evaluate_workflow_live,
    check_exploration_hacking,
    get_skill_reputation,
    run_red_team_test
)

app = FastAPI(
    title="SOHH Security Assessment API",
    description="Self-Optimizing Holo Half - Agent安全评估服务",
    version="2.2.0"
)


# ============================================================================
# 数据模型
# ============================================================================

class StepModel(BaseModel):
    content: Optional[str] = None
    command: Optional[str] = None
    output: Optional[str] = None
    result: Optional[str] = None
    timestamp: Optional[str] = None


class SkillVerificationRequest(BaseModel):
    skill_code: str
    skill_name: str = "unknown_skill"


class WorkflowEvaluationRequest(BaseModel):
    workflow_steps: List[Dict[str, Any]]
    expected_outcomes: Optional[List[Dict[str, Any]]] = None


class ExplorationHackingRequest(BaseModel):
    training_logs: List[Dict[str, Any]]


class SkillReputationRequest(BaseModel):
    skill_name: str
    verification_history: Optional[List[Dict[str, Any]]] = None


class RedTeamTestRequest(BaseModel):
    agent_config: Dict[str, Any]
    test_scenarios: Optional[List[Dict[str, Any]]] = None


# ============================================================================
# API 端点
# ============================================================================

@app.get("/")
def read_root():
    """API根路径"""
    return {
        "service": "SOHH Security Assessment API",
        "version": "2.2.0",
        "status": "running",
        "endpoints": [
            "/assess/session",
            "/assess/skill",
            "/assess/workflow",
            "/detect/exploration-hacking",
            "/reputation/skill",
            "/test/red-team",
            "/health"
        ]
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/assess/session")
def assess_session_security(steps: List[StepModel]):
    """
    评估会话安全性
    
    Args:
        steps: 执行步骤列表
        
    Returns:
        安全评估报告
    """
    try:
        # 转换为字典格式
        steps_dict = [step.dict(exclude_none=True) for step in steps]
        
        report = get_security_assessment_report(steps_dict)
        
        return {
            "success": True,
            "data": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assess/skill")
def assess_skill_safety(request: SkillVerificationRequest):
    """
    验证Skill代码安全性
    
    Args:
        request: Skill验证请求
        
    Returns:
        Skill安全验证报告
    """
    try:
        result = verify_skill(request.skill_code, request.skill_name)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assess/workflow")
def assess_workflow_live(request: WorkflowEvaluationRequest):
    """
    实时工作流评估（Claw-Eval-Live）
    
    Args:
        request: 工作流评估请求
        
    Returns:
        实时评估报告
    """
    try:
        result = evaluate_workflow_live(
            request.workflow_steps,
            request.expected_outcomes
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect/exploration-hacking")
def detect_exploration_hacking_api(request: ExplorationHackingRequest):
    """
    检测探索黑客行为
    
    Args:
        request: 训练日志
        
    Returns:
        检测报告
    """
    try:
        result = check_exploration_hacking(request.training_logs)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reputation/skill")
def get_skill_reputation_api(request: SkillReputationRequest):
    """
    获取Skills信誉评分
    
    Args:
        request: Skills信誉查询请求
        
    Returns:
        信誉报告
    """
    try:
        result = get_skill_reputation(
            request.skill_name,
            request.verification_history
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test/red-team")
def run_red_team_test_api(request: RedTeamTestRequest):
    """
    运行红队测试
    
    Args:
        request: 红队测试请求
        
    Returns:
        红队测试报告
    """
    try:
        result = run_red_team_test(
            request.agent_config,
            request.test_scenarios
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 启动服务器
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("="*70)
    print("🚀 SOHH Security Assessment API Server")
    print("="*70)
    print("\n📡 服务器启动中...")
    print("   API文档: http://localhost:8000/docs")
    print("   ReDoc: http://localhost:8000/redoc")
    print("\n💡 使用示例:")
    print("   curl -X POST http://localhost:8000/assess/session \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '[{\"content\": \"ls -la\"}]'")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
