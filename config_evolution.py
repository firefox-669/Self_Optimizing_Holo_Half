# Self_Optimizing_Holo_Half 进化配置
# 默认配置 - 低风险设置

# ============ 安全级别 (选择一个) ============
# DISABLED = 完全禁用
# READ_ONLY = 仅分析, 不修改
# DRY_RUN = 测试运行, 不保存
# SAFE_ONLY = 仅安全的修改
# FULL = 完全自动 (风险最高)

SAFETY_LEVEL = "SAFE_ONLY"  # 默认使用安全模式

# ============ 最低优先级阈值 ============
# 只有优先级 >= 此值的建议才会被自动应用
MIN_PRIORITY_THRESHOLD = 0.7

# ============ 高风险操作黑名单 ============
# 以下类型的建议不会自动应用，需要手动确认

UNSAFE_TYPES = [
    "connection",      # 连接新服务
    "new_feature",   # 新功能
]

# ============ 备份设置 ============
# 自动创建备份快照
AUTO_BACKUP = True
MAX_SNAPSHOTS = 10  # 最多保留的快照数

# ============ 验证设置 ============
# 自动验证修改后的项目是否正常工作
AUTO_VERIFY = True
VERIFY_TIMEOUT = 30  # 验证超时秒数

# ============ 网络设置 ============
# 资讯收集间隔 (秒)
FETCH_INTERVAL = 3600  # 1小时

# ============ 自动进化设置 ============
# 是否启用每日自动进化
AUTO_DAILY = False
DAILY_HOUR = 3  # 每天几点运行 (0-23)