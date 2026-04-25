"""
SOHH 标准数据采集接口规范 v1.0

这个模块定义了 AI Agent 评估系统的标准数据接口，类似于 USB 接口规范。
任何 AI Agent 系统都可以按照此规范实现数据采集，与 SOHH 兼容。

设计理念：
- 松耦合：Agent 系统只需实现标准接口，无需依赖 SOHH 内部实现
- 可扩展：支持自定义字段和扩展维度
- 向后兼容：新版本接口兼容旧版本数据

使用示例：
    from sohh_standard_interface import SOHHDataCollector
    
    # 创建采集器
    collector = SOHHDataCollector(
        agent_id="openhands-v1.0",
        project_id="my-project"
    )
    
    # 记录任务执行
    collector.record_task_execution(
        task_id="task-001",
        description="Create a Flask API",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=5),
        success=True,
        tokens_used=1500,
        cost=0.003
    )
    
    # 记录用户反馈
    collector.record_user_feedback(
        task_id="task-001",
        satisfaction_score=4.5,
        feedback="Good code quality"
    )
    
    # 提交数据到 SOHH
    collector.submit_to_sohh(db_path="data/holo_half.db")
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum
import json
import uuid


class SuggestionCategory(Enum):
    """建议类别标准化"""
    SKILL_UPDATE = "skill_update"
    PARAMETER_TUNING = "parameter_tuning"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    TOOL_INTEGRATION = "tool_integration"
    SECURITY_PATCH = "security_patch"


class PriorityLevel(Enum):
    """优先级标准化"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class StandardActionItem:
    """
    标准行动项 (The Core of Standardization)
    这是不同项目都能看懂的“最小执行单元”
    """
    action_id: str = field(default_factory=lambda: f"act_{uuid.uuid4().hex[:8]}")
    category: SuggestionCategory = SuggestionCategory.SKILL_UPDATE
    priority: PriorityLevel = PriorityLevel.MEDIUM
    title: str = ""
    description: str = ""
    
    # 标准化的负载数据 (Payload)，不同 Category 对应不同的 Key-Value 结构
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # 预期收益指标 (用于后续验证进化是否成功)
    expected_metrics: Dict[str, float] = field(default_factory=dict)
    
    # 实施难度评估 (1-10)
    complexity_score: int = 5


@dataclass
class StandardEvolutionReport:
    """
    标准进化报告
    所有接入 SOHH 的项目，拿到的都是这个统一格式的报告
    """
    report_id: str = field(default_factory=lambda: f"evo_{uuid.uuid4().hex[:8]}")
    agent_id: str = ""
    generated_at: datetime = field(default_factory=datetime.now)
    current_health_score: float = 0.0
    
    # 核心：标准化的行动建议列表
    action_items: List[StandardActionItem] = field(default_factory=list)
    
    # 关联的行业趋势参考
    trend_references: List[Dict[str, str]] = field(default_factory=list)
    
    def to_json(self) -> str:
        """序列化为 JSON 字符串，方便跨项目传输"""
        def convert_to_dict(obj):
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if isinstance(value, Enum):
                        result[key] = value.value
                    elif isinstance(value, datetime):
                        result[key] = value.isoformat()
                    elif isinstance(value, list):
                        result[key] = [convert_to_dict(item) for item in value]
                    elif hasattr(value, '__dict__'):
                        result[key] = convert_to_dict(value)
                    else:
                        result[key] = value
                return result
            return obj
            
        return json.dumps(convert_to_dict(self), indent=2, ensure_ascii=False)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class TaskExecution:
    """
    任务执行记录 - 核心数据结构
    
    这是评估系统的基础单元，每个任务执行都会生成一条记录。
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""  # Agent 标识，如 "openhands-v1.0"
    project_id: str = ""  # 项目标识
    description: str = ""  # 任务描述
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    
    # 资源使用情况
    tokens_used: int = 0
    cost: float = 0.0
    iterations: int = 0
    
    # 质量指标（可选，由 Agent 自行评估）
    code_quality_score: Optional[float] = None  # 代码质量评分 0-1
    test_pass_rate: Optional[float] = None  # 测试通过率 0-1
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'task_id': self.task_id,
            'agent_id': self.agent_id,
            'project_id': self.project_id,
            'description': self.description,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'success': self.success,
            'error_message': self.error_message,
            'tokens_used': self.tokens_used,
            'cost': self.cost,
            'iterations': self.iterations,
            'code_quality_score': self.code_quality_score,
            'test_pass_rate': self.test_pass_rate,
            'metadata': json.dumps(self.metadata),
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class UserFeedback:
    """
    用户反馈记录
    
    用户对任务执行结果的主观评价。
    """
    feedback_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    user_id: str = "anonymous"
    satisfaction_score: float = 0.0  # 满意度 0-5
    feedback_text: Optional[str] = None
    would_recommend: Optional[bool] = None  # 是否推荐
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'feedback_id': self.feedback_id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'satisfaction_score': self.satisfaction_score,
            'feedback_text': self.feedback_text,
            'would_recommend': self.would_recommend,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class SkillUsage:
    """
    技能使用记录
    
    记录 Agent 使用了哪些技能/工具。
    """
    skill_id: str = ""
    skill_name: str = ""
    task_id: str = ""
    usage_count: int = 0
    success_count: int = 0
    avg_duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'skill_id': self.skill_id,
            'skill_name': self.skill_name,
            'task_id': self.task_id,
            'usage_count': self.usage_count,
            'success_count': self.success_count,
            'avg_duration': self.avg_duration,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class CapabilitySnapshot:
    """
    能力快照 - 定期记录 Agent 的综合能力
    
    用于生成历史趋势图。
    """
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 六维能力评分 (0-100)
    success_rate: float = 0.0
    efficiency_gain: float = 0.0
    user_satisfaction: float = 0.0
    usage_activity: float = 0.0
    cost_efficiency: float = 0.0
    innovation: float = 0.0
    
    # 综合评分
    overall_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'snapshot_id': self.snapshot_id,
            'agent_id': self.agent_id,
            'timestamp': self.timestamp.isoformat(),
            'success_rate': self.success_rate,
            'efficiency_gain': self.efficiency_gain,
            'user_satisfaction': self.user_satisfaction,
            'usage_activity': self.usage_activity,
            'cost_efficiency': self.cost_efficiency,
            'innovation': self.innovation,
            'overall_score': self.overall_score
        }


class SOHHDataCollector:
    """
    SOHH 标准数据采集器
    
    这是"USB 接口"的核心实现。任何 AI Agent 系统都可以使用这个采集器
    来收集数据并提交到 SOHH 进行评估。
    
    使用示例（OpenHands 集成）:
        collector = SOHHDataCollector(agent_id="openhands-v1.0")
        
        # 在任务开始时
        collector.start_task(task_id="xxx", description="...")
        
        # 在任务结束时
        collector.end_task(task_id="xxx", success=True, ...)
        
        # 记录用户反馈
        collector.record_feedback(task_id="xxx", satisfaction=4.5)
        
        # 定期提交数据
        collector.submit_to_sohh()
    """
    
    def __init__(self, agent_id: str, project_id: str = "default"):
        """
        初始化数据采集器
        
        Args:
            agent_id: Agent 的唯一标识，如 "openhands-v1.0"
            project_id: 项目标识
        """
        self.agent_id = agent_id
        self.project_id = project_id
        self.task_executions: List[TaskExecution] = []
        self.user_feedbacks: List[UserFeedback] = []
        self.skill_usages: List[SkillUsage] = []
        self.capability_snapshots: List[CapabilitySnapshot] = []
    
    def start_task(self, task_id: str, description: str, metadata: Dict = None) -> str:
        """
        记录任务开始
        
        Args:
            task_id: 任务ID
            description: 任务描述
            metadata: 额外元数据
            
        Returns:
            task_id
        """
        execution = TaskExecution(
            task_id=task_id,
            agent_id=self.agent_id,
            project_id=self.project_id,
            description=description,
            status=TaskStatus.RUNNING,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        self.task_executions.append(execution)
        return task_id
    
    def end_task(self, task_id: str, success: bool, 
                 tokens_used: int = 0, cost: float = 0.0,
                 iterations: int = 0, error_message: str = None,
                 code_quality_score: float = None,
                 test_pass_rate: float = None,
                 metadata: Dict[str, Any] = None) -> None:
        """
        记录任务结束
        
        Args:
            task_id: 任务ID
            success: 是否成功
            tokens_used: 使用的 Token 数量
            cost: 成本（美元）
            iterations: 迭代次数
            error_message: 错误信息（如果失败）
            code_quality_score: 代码质量评分 0-1
            test_pass_rate: 测试通过率 0-1
            metadata: 额外元数据
        """
        for execution in self.task_executions:
            if execution.task_id == task_id:
                execution.end_time = datetime.now()
                execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()
                execution.status = TaskStatus.SUCCESS if success else TaskStatus.FAILED
                execution.success = success
                execution.tokens_used = tokens_used
                execution.cost = cost
                execution.iterations = iterations
                execution.error_message = error_message
                execution.code_quality_score = code_quality_score
                execution.test_pass_rate = test_pass_rate
                if metadata:
                    execution.metadata.update(metadata)
                break
    
    def record_feedback(self, task_id: str, satisfaction_score: float,
                       feedback_text: str = None, would_recommend: bool = None) -> None:
        """
        记录用户反馈
        
        Args:
            task_id: 任务ID
            satisfaction_score: 满意度评分 0-5
            feedback_text: 反馈文本
            would_recommend: 是否推荐
        """
        feedback = UserFeedback(
            task_id=task_id,
            satisfaction_score=satisfaction_score,
            feedback_text=feedback_text,
            would_recommend=would_recommend
        )
        self.user_feedbacks.append(feedback)
    
    def record_skill_usage(self, skill_id: str, skill_name: str,
                          task_id: str, success: bool,
                          duration: float) -> None:
        """
        记录技能使用
        
        Args:
            skill_id: 技能ID
            skill_name: 技能名称
            task_id: 任务ID
            success: 是否成功
            duration: 执行时长（秒）
        """
        # 查找是否已有该技能的记录
        existing = None
        for usage in self.skill_usages:
            if usage.skill_id == skill_id and usage.task_id == task_id:
                existing = usage
                break
        
        if existing:
            existing.usage_count += 1
            if success:
                existing.success_count += 1
            existing.avg_duration = (existing.avg_duration * (existing.usage_count - 1) + duration) / existing.usage_count
        else:
            usage = SkillUsage(
                skill_id=skill_id,
                skill_name=skill_name,
                task_id=task_id,
                usage_count=1,
                success_count=1 if success else 0,
                avg_duration=duration
            )
            self.skill_usages.append(usage)
    
    def take_capability_snapshot(self) -> CapabilitySnapshot:
        """
        拍摄能力快照 - 计算当前的综合能力评分
        
        Returns:
            CapabilitySnapshot
        """
        # 计算各项指标
        if not self.task_executions:
            return CapabilitySnapshot(agent_id=self.agent_id)
        
        completed_tasks = [t for t in self.task_executions if t.end_time]
        if not completed_tasks:
            return CapabilitySnapshot(agent_id=self.agent_id)
        
        # 成功率
        successful = sum(1 for t in completed_tasks if t.success)
        success_rate = (successful / len(completed_tasks)) * 100
        
        # 效率（基于平均耗时，假设基准为 300 秒）
        avg_duration = sum(t.duration_seconds for t in completed_tasks) / len(completed_tasks)
        efficiency_gain = max(0, (1 - avg_duration / 300)) * 100
        
        # 用户满意度
        if self.user_feedbacks:
            avg_satisfaction = sum(f.satisfaction_score for f in self.user_feedbacks) / len(self.user_feedbacks)
            user_satisfaction = (avg_satisfaction / 5.0) * 100
        else:
            user_satisfaction = 50.0  # 默认值
        
        # 使用活跃度（基于任务数量）
        usage_activity = min(100, len(completed_tasks) * 10)
        
        # 成本效率
        total_cost = sum(t.cost for t in completed_tasks)
        avg_cost = total_cost / len(completed_tasks) if completed_tasks else 0
        cost_efficiency = max(0, (1 - avg_cost / 0.01)) * 100  # 假设基准成本 $0.01
        
        # 创新性（基于代码质量和测试通过率）
        quality_scores = [t.code_quality_score for t in completed_tasks if t.code_quality_score]
        test_scores = [t.test_pass_rate for t in completed_tasks if t.test_pass_rate]
        innovation = ((sum(quality_scores) / len(quality_scores) if quality_scores else 0.5) * 50 +
                     (sum(test_scores) / len(test_scores) if test_scores else 0.5) * 50)
        
        # 综合评分
        overall_score = (success_rate * 0.2 + efficiency_gain * 0.15 + 
                        user_satisfaction * 0.2 + usage_activity * 0.15 +
                        cost_efficiency * 0.15 + innovation * 0.15)
        
        snapshot = CapabilitySnapshot(
            agent_id=self.agent_id,
            success_rate=round(success_rate, 2),
            efficiency_gain=round(efficiency_gain, 2),
            user_satisfaction=round(user_satisfaction, 2),
            usage_activity=round(usage_activity, 2),
            cost_efficiency=round(cost_efficiency, 2),
            innovation=round(innovation, 2),
            overall_score=round(overall_score, 2)
        )
        
        self.capability_snapshots.append(snapshot)
        return snapshot
    
    def submit_to_sohh(self, db_path: str = "data/holo_half.db", trace_source_path: str = None) -> Dict:
        """
        提交数据到 SOHH 数据库
        
        Args:
            db_path: SOHH 数据库路径
            trace_source_path: 执行链路日志的路径（如 OpenSpace 的 recordings 目录）
            
        Returns:
            提交结果统计
        """
        import sqlite3
        from pathlib import Path
        
        # 1. 尝试加载插件并采集链路数据
        execution_traces = []
        if trace_source_path and Path(trace_source_path).exists():
            try:
                from plugins.openspace_analyzer import OpenSpaceAnalyzer
                analyzer = OpenSpaceAnalyzer()
                if analyzer.is_compatible(trace_source_path):
                    print(f"🔍 检测到兼容框架，正在解析链路: {trace_source_path}")
                    steps = analyzer.collect_trace(trace_source_path)
                    metrics = analyzer.analyze_metrics(steps)
                    print(f"✅ 链路解析成功: {metrics['total_steps']} 步")
                    execution_traces = steps
            except ImportError:
                print("⚠️  插件模块未找到，跳过链路采集")
        
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        try:
            # 创建表（如果不存在）
            self._create_tables(cursor)
            
            # 插入任务执行记录
            tasks_inserted = 0
            for task in self.task_executions:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO task_executions 
                        (task_id, agent_id, project_id, description, status, 
                         start_time, end_time, duration_seconds, success, 
                         error_message, tokens_used, cost, iterations,
                         code_quality_score, test_pass_rate, metadata, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        task.task_id, task.agent_id, task.project_id, task.description,
                        task.status.value, task.start_time.isoformat() if task.start_time else None,
                        task.end_time.isoformat() if task.end_time else None,
                        task.duration_seconds, task.success, task.error_message,
                        task.tokens_used, task.cost, task.iterations,
                        task.code_quality_score, task.test_pass_rate,
                        json.dumps(task.metadata), task.timestamp.isoformat()
                    ))
                    tasks_inserted += 1
                except Exception as e:
                    print(f"⚠️  插入任务记录失败: {e}")
            
            # 插入用户反馈
            feedbacks_inserted = 0
            for feedback in self.user_feedbacks:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO user_feedbacks
                        (feedback_id, task_id, user_id, satisfaction_score, 
                         feedback_text, would_recommend, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        feedback.feedback_id, feedback.task_id, feedback.user_id,
                        feedback.satisfaction_score, feedback.feedback_text,
                        feedback.would_recommend, feedback.timestamp.isoformat()
                    ))
                    feedbacks_inserted += 1
                except Exception as e:
                    print(f"⚠️  插入反馈记录失败: {e}")
            
            # 插入能力快照
            snapshots_inserted = 0
            for snapshot in self.capability_snapshots:
                try:
                    cursor.execute("""
                        INSERT INTO capability_snapshots
                        (snapshot_id, agent_id, timestamp, success_rate, 
                         efficiency_gain, user_satisfaction, usage_activity,
                         cost_efficiency, innovation, overall_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        snapshot.snapshot_id, snapshot.agent_id, snapshot.timestamp.isoformat(),
                        snapshot.success_rate, snapshot.efficiency_gain,
                        snapshot.user_satisfaction, snapshot.usage_activity,
                        snapshot.cost_efficiency, snapshot.innovation,
                        snapshot.overall_score
                    ))
                    snapshots_inserted += 1
                except Exception as e:
                    print(f"⚠️  插入快照记录失败: {e}")
            
            # 插入任务记录 (用于报告展示)
            tasks_records_inserted = 0
            for task in self.task_executions:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO task_records 
                        (task_id, description, success, duration, iterations, error_message)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        task.task_id, task.description, task.success,
                        task.duration_seconds, task.iterations, task.error_message
                    ))
                    tasks_records_inserted += 1
                except Exception as e:
                    print(f"⚠️  插入任务记录（报告用）失败: {e}")
            
            # 插入执行轨迹 (v2.1 新增)
            traces_inserted = 0
            if execution_traces:
                # 简单起见，我们将所有步骤关联到最近的一个任务 ID
                last_task_id = self.task_executions[-1].task_id if self.task_executions else "unknown"
                for step in execution_traces:
                    try:
                        cursor.execute("""
                            INSERT INTO execution_traces 
                            (task_id, step_id, timestamp, step_type, content, metadata_json)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            last_task_id, step.step_id, step.timestamp, 
                            step.step_type, step.content[:500], json.dumps(step.metadata) # 限制内容长度
                        ))
                        traces_inserted += 1
                    except Exception as e:
                        print(f"⚠️  插入轨迹步骤失败: {e}")
            
            conn.commit()
            
            result = {
                'success': True,
                'tasks_inserted': tasks_inserted,
                'feedbacks_inserted': feedbacks_inserted,
                'snapshots_inserted': snapshots_inserted,
                'tasks_records_inserted': tasks_records_inserted,
                'traces_inserted': traces_inserted,
                'db_path': str(db_path)
            }
            
            print(f"✅ 数据提交成功!")
            print(f"   任务记录: {tasks_inserted}")
            print(f"   用户反馈: {feedbacks_inserted}")
            print(f"   能力快照: {snapshots_inserted}")
            print(f"   报告任务清单: {tasks_records_inserted}")
            print(f"   执行轨迹步骤: {traces_inserted}")
            print(f"   数据库: {db_path}")
            
            return result
            
        except Exception as e:
            conn.rollback()
            print(f"❌ 数据提交失败: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def _create_tables(self, cursor):
        """创建数据库表"""
        
        # 任务执行表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_executions (
                task_id TEXT PRIMARY KEY,
                agent_id TEXT,
                project_id TEXT,
                description TEXT,
                status TEXT,
                start_time TEXT,
                end_time TEXT,
                duration_seconds REAL,
                success BOOLEAN,
                error_message TEXT,
                tokens_used INTEGER,
                cost REAL,
                iterations INTEGER,
                code_quality_score REAL,
                test_pass_rate REAL,
                metadata TEXT,
                timestamp TEXT
            )
        """)
        
        # 用户反馈表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedbacks (
                feedback_id TEXT PRIMARY KEY,
                task_id TEXT,
                user_id TEXT,
                satisfaction_score REAL,
                feedback_text TEXT,
                would_recommend BOOLEAN,
                timestamp TEXT,
                FOREIGN KEY (task_id) REFERENCES task_executions(task_id)
            )
        """)
        
        # 能力快照表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS capability_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                agent_id TEXT,
                timestamp TEXT,
                success_rate REAL,
                efficiency_gain REAL,
                user_satisfaction REAL,
                usage_activity REAL,
                cost_efficiency REAL,
                innovation REAL,
                overall_score REAL
            )
        """)
        
        # 技能使用表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_usages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id TEXT,
                skill_name TEXT,
                task_id TEXT,
                usage_count INTEGER,
                success_count INTEGER,
                avg_duration REAL,
                timestamp TEXT
            )
        """)
        
        # 任务记录表 (用于报告展示)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                description TEXT,
                success BOOLEAN DEFAULT 0,
                duration REAL DEFAULT 0,
                iterations INTEGER DEFAULT 0,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 执行轨迹表 (v2.1 新增 - 存储标准化步骤)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                step_id INTEGER NOT NULL,
                timestamp REAL,
                step_type TEXT,
                content TEXT,
                metadata_json TEXT,
                FOREIGN KEY (task_id) REFERENCES task_records(task_id)
            )
        """)
    
    def export_to_json(self, filepath: str) -> str:
        """
        导出数据为 JSON 文件
        
        Args:
            filepath: 输出文件路径
            
        Returns:
            文件路径
        """
        data = {
            'agent_id': self.agent_id,
            'project_id': self.project_id,
            'export_time': datetime.now().isoformat(),
            'task_executions': [t.to_dict() for t in self.task_executions],
            'user_feedbacks': [f.to_dict() for f in self.user_feedbacks],
            'skill_usages': [s.to_dict() for s in self.skill_usages],
            'capability_snapshots': [c.to_dict() for c in self.capability_snapshots]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 数据已导出到: {filepath}")
        return filepath


# 便捷函数
def create_collector(agent_id: str, project_id: str = "default") -> SOHHDataCollector:
    """
    创建数据采集器的便捷函数
    
    Args:
        agent_id: Agent 标识
        project_id: 项目标识
        
    Returns:
        SOHHDataCollector 实例
    """
    return SOHHDataCollector(agent_id=agent_id, project_id=project_id)


class SuggestionProvider:
    """
    SOHH 建议提供者接口
    
    任何项目接入此接口后，都可以从 SOHH 获取最新的进化方向分析和优化意见。
    SOHH 不会直接修改代码，而是提供结构化的建议报告。
    """
    
    def get_evolution_suggestions(self, agent_id: str, context: Dict = None) -> StandardEvolutionReport:
        """
        获取进化建议
        
        Args:
            agent_id: Agent 的唯一标识
            context: 额外的上下文信息（如当前使用的模型版本、技能列表等）
            
        Returns:
            StandardEvolutionReport: 包含趋势分析、薄弱点诊断和优化建议的报告
        """
        raise NotImplementedError
