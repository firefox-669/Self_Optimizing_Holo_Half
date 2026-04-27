"""
评估信度检验工具

提供重测信度、内部一致性等统计检验功能，确保评估结果的可靠性。
"""

import numpy as np
from typing import List, Dict, Any, Callable


def test_retest_reliability(evaluation_func: Callable, 
                           task_id: str,
                           runs: int = 5,
                           **kwargs) -> Dict[str, Any]:
    """
    重测信度检验 - 同一任务多次运行，检验评分稳定性
    
    Args:
        evaluation_func: 评估函数，返回评分字典
        task_id: 任务ID
        runs: 运行次数（建议5-10次）
        **kwargs: 传递给评估函数的额外参数
    
    Returns:
        信度检验结果
    """
    print(f"🔄 开始重测信度检验 (runs={runs})...")
    
    scores = []
    for i in range(runs):
        result = evaluation_func(task_id=task_id, **kwargs)
        scores.append(result)
        print(f"   第 {i+1}/{runs} 次运行完成")
    
    # 提取各维度的分数
    dimensions = scores[0].keys()
    reliability_results = {}
    
    for dim in dimensions:
        dim_scores = [s[dim] for s in scores]
        
        # 计算统计量
        mean = np.mean(dim_scores)
        std = np.std(dim_scores)
        cv = std / mean if mean != 0 else 0  # 变异系数
        
        # 信度判断：CV < 10% 认为可靠
        is_reliable = cv < 0.1
        
        reliability_results[dim] = {
            "mean": round(mean, 2),
            "std": round(std, 2),
            "cv": round(cv, 4),
            "is_reliable": is_reliable,
            "scores": dim_scores
        }
    
    # 整体信度
    all_cvs = [r["cv"] for r in reliability_results.values()]
    overall_cv = np.mean(all_cvs)
    overall_reliable = overall_cv < 0.1
    
    return {
        "task_id": task_id,
        "runs": runs,
        "overall_cv": round(overall_cv, 4),
        "overall_reliable": overall_reliable,
        "dimensions": reliability_results
    }


def cronbach_alpha(items_scores: List[List[float]]) -> float:
    """
    计算 Cronbach's Alpha 系数 - 内部一致性检验
    
    Args:
        items_scores: 每个被试在各题目上的得分矩阵
                     shape: (n_subjects, n_items)
    
    Returns:
        Cronbach's Alpha 系数 (0-1)
        > 0.9: 优秀
        0.8-0.9: 良好
        0.7-0.8: 可接受
        < 0.7: 需要改进
    """
    items_scores = np.array(items_scores)
    n_subjects, n_items = items_scores.shape
    
    if n_items < 2:
        raise ValueError("至少需要2个题目才能计算Cronbach's Alpha")
    
    # 计算每个题目的方差
    item_variances = np.var(items_scores, axis=0, ddof=1)
    
    # 计算总分的方差
    total_scores = np.sum(items_scores, axis=1)
    total_variance = np.var(total_scores, ddof=1)
    
    # 计算Alpha
    alpha = (n_items / (n_items - 1)) * (1 - np.sum(item_variances) / total_variance)
    
    return round(alpha, 4)


def test_internal_consistency(agent_scores: List[Dict[str, float]],
                             dimensions: List[str] = None) -> Dict[str, Any]:
    """
    检验六维能力模型的内部一致性
    
    Args:
        agent_scores: 多个Agent的评分列表
        dimensions: 要检验的维度列表，默认为全部
    
    Returns:
        内部一致性检验结果
    """
    if dimensions is None:
        dimensions = ["success_rate", "efficiency_gain", "user_satisfaction",
                     "usage_activity", "cost_efficiency", "innovation"]
    
    # 构建评分矩阵
    scores_matrix = []
    for agent_score in agent_scores:
        row = [agent_score.get(dim, 0) for dim in dimensions]
        scores_matrix.append(row)
    
    # 计算Cronbach's Alpha
    alpha = cronbach_alpha(scores_matrix)
    
    # 解释Alpha值
    if alpha >= 0.9:
        interpretation = "优秀 - 维度间高度一致"
    elif alpha >= 0.8:
        interpretation = "良好 - 维度间一致性较好"
    elif alpha >= 0.7:
        interpretation = "可接受 - 维度间有一定一致性"
    else:
        interpretation = "需要改进 - 维度间一致性不足"
    
    return {
        "cronbach_alpha": alpha,
        "interpretation": interpretation,
        "n_agents": len(agent_scores),
        "dimensions_tested": dimensions,
        "reliable": alpha >= 0.7
    }


def inter_rater_agreement(ratings: List[List[float]]) -> Dict[str, Any]:
    """
    计算评分者间一致性（如果有多个评估者）
    
    Args:
        ratings: 多个评估者对同一组任务的评分
                shape: (n_raters, n_tasks)
    
    Returns:
        一致性统计结果
    """
    ratings = np.array(ratings)
    n_raters, n_tasks = ratings.shape
    
    # 计算相关系数矩阵
    corr_matrix = np.corrcoef(ratings)
    
    # 平均相关系数（排除对角线）
    mask = ~np.eye(n_raters, dtype=bool)
    avg_correlation = np.mean(corr_matrix[mask])
    
    # 标准差的一致性
    std_across_raters = np.std(ratings, axis=0)
    avg_std = np.mean(std_across_raters)
    
    return {
        "avg_correlation": round(avg_correlation, 4),
        "avg_std_across_raters": round(avg_std, 4),
        "n_raters": n_raters,
        "n_tasks": n_tasks,
        "correlation_matrix": corr_matrix.tolist(),
        "reliable": avg_correlation > 0.7
    }


def generate_reliability_report(evaluation_func: Callable,
                               test_tasks: List[str],
                               runs_per_task: int = 5) -> Dict[str, Any]:
    """
    生成完整的信度检验报告
    
    Args:
        evaluation_func: 评估函数
        test_tasks: 测试任务列表
        runs_per_task: 每个任务的运行次数
    
    Returns:
        完整的信度报告
    """
    print("="*70)
    print("📊 评估系统信度检验报告")
    print("="*70)
    
    report = {
        "test_tasks": len(test_tasks),
        "runs_per_task": runs_per_task,
        "total_evaluations": len(test_tasks) * runs_per_task,
        "task_results": {}
    }
    
    all_reliable_count = 0
    
    for task_id in test_tasks:
        print(f"\n🔍 检验任务: {task_id}")
        result = test_retest_reliability(
            evaluation_func=evaluation_func,
            task_id=task_id,
            runs=runs_per_task
        )
        
        report["task_results"][task_id] = result
        
        if result["overall_reliable"]:
            all_reliable_count += 1
            print(f"   ✅ 信度良好 (CV={result['overall_cv']:.4f})")
        else:
            print(f"   ⚠️  信度需改进 (CV={result['overall_cv']:.4f})")
    
    # 总体统计
    reliability_rate = all_reliable_count / len(test_tasks) * 100
    
    print("\n" + "="*70)
    print(f"📈 总体信度: {all_reliable_count}/{len(test_tasks)} 任务可靠 ({reliability_rate:.1f}%)")
    print("="*70)
    
    report["overall_reliability_rate"] = round(reliability_rate, 2)
    report["reliable_tasks"] = all_reliable_count
    report["total_tasks"] = len(test_tasks)
    
    return report


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    # 示例1：重测信度检验
    print("\n" + "="*70)
    print("示例1: 重测信度检验")
    print("="*70)
    
    # 模拟评估函数
    def mock_evaluation(task_id: str, **kwargs):
        import random
        # 模拟有些波动的评分
        return {
            "success_rate": 80 + random.uniform(-5, 5),
            "efficiency_gain": 20 + random.uniform(-3, 3),
            "user_satisfaction": 85 + random.uniform(-4, 4)
        }
    
    result = test_retest_reliability(
        evaluation_func=mock_evaluation,
        task_id="test-task-001",
        runs=5
    )
    
    print(f"\n整体变异系数: {result['overall_cv']:.4f}")
    print(f"是否可靠: {'✅ 是' if result['overall_reliable'] else '❌ 否'}")
    
    # 示例2：内部一致性检验
    print("\n" + "="*70)
    print("示例2: 内部一致性检验")
    print("="*70)
    
    # 模拟10个Agent的评分
    agent_scores = [
        {"success_rate": 85, "efficiency_gain": 20, "user_satisfaction": 90,
         "usage_activity": 70, "cost_efficiency": 75, "innovation": 80},
        {"success_rate": 78, "efficiency_gain": 18, "user_satisfaction": 85,
         "usage_activity": 65, "cost_efficiency": 70, "innovation": 75},
        # ... 更多Agent
    ]
    
    # 生成更多模拟数据
    import random
    for i in range(8):
        agent_scores.append({
            "success_rate": 70 + random.uniform(0, 20),
            "efficiency_gain": 15 + random.uniform(0, 15),
            "user_satisfaction": 80 + random.uniform(0, 15),
            "usage_activity": 60 + random.uniform(0, 30),
            "cost_efficiency": 65 + random.uniform(0, 20),
            "innovation": 70 + random.uniform(0, 20)
        })
    
    consistency = test_internal_consistency(agent_scores)
    
    print(f"\nCronbach's Alpha: {consistency['cronbach_alpha']:.4f}")
    print(f"解释: {consistency['interpretation']}")
    print(f"是否可靠: {'✅ 是' if consistency['reliable'] else '❌ 否'}")
    
    print("\n" + "="*70)
    print("💡 提示: 在实际使用中，用真实的评估函数替换mock_evaluation")
    print("="*70)
