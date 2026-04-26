"""
SOHH 核心功能验证脚本

用于快速检查 SOHH 的关键组件是否正常工作
"""

import sys
from pathlib import Path

def check_imports():
    """检查关键模块是否可以导入"""
    print("="*70)
    print("1. 检查模块导入")
    print("="*70)
    
    modules = [
        ('sohh_standard_interface', '标准接口'),
        ('user_scoring.visualization_report', '可视化报告生成器'),
        ('plugins.openspace_analyzer', 'OpenSpace日志解析器'),
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✅ {description:20} - {module_name}")
        except ImportError as e:
            print(f"❌ {description:20} - {module_name}")
            print(f"   错误: {e}")
            all_ok = False
    
    return all_ok


def check_files():
    """检查关键文件是否存在"""
    print("\n" + "="*70)
    print("2. 检查关键文件")
    print("="*70)
    
    files = [
        ('README.md', '项目文档'),
        ('OPENSPACE_INTEGRATION_GUIDE.md', '集成指南'),
        ('examples/sohh_integration_example.py', '示例代码'),
        ('examples/integration_openspace_real.py', 'OpenSpace集成示例'),
        ('requirements.txt', '依赖列表'),
    ]
    
    all_ok = True
    for file_path, description in files:
        if Path(file_path).exists():
            print(f"✅ {description:25} - {file_path}")
        else:
            print(f"❌ {description:25} - {file_path} (缺失)")
            all_ok = False
    
    return all_ok


def check_database():
    """检查数据库结构"""
    print("\n" + "="*70)
    print("3. 检查数据库")
    print("="*70)
    
    db_path = Path("data/holo_half.db")
    if not db_path.exists():
        print(f"⚠️  数据库不存在: {db_path}")
        print("   提示: 运行 benchmark 后会创建数据库")
        return True
    
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 检查关键表
    tables = ['task_records', 'capability_snapshots', 'scoring_records']
    all_ok = True
    
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ {table:30} - {count} 条记录")
        else:
            print(f"⚠️  {table:30} - 表不存在")
    
    conn.close()
    return all_ok


def check_examples():
    """检查示例代码"""
    print("\n" + "="*70)
    print("4. 检查示例代码")
    print("="*70)
    
    examples_dir = Path("examples")
    if not examples_dir.exists():
        print("❌ examples 目录不存在")
        return False
    
    example_files = list(examples_dir.glob("*.py"))
    print(f"✅ 找到 {len(example_files)} 个示例文件:")
    for f in sorted(example_files):
        print(f"   - {f.name}")
    
    return len(example_files) > 0


def main():
    """主函数"""
    print("\n" + "="*70)
    print("SOHH 核心功能验证")
    print("="*70 + "\n")
    
    results = []
    
    # 执行检查
    results.append(("模块导入", check_imports()))
    results.append(("关键文件", check_files()))
    results.append(("数据库", check_database()))
    results.append(("示例代码", check_examples()))
    
    # 总结
    print("\n" + "="*70)
    print("验证总结")
    print("="*70)
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:20} - {status}")
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 所有检查通过！SOHH 已准备就绪。")
    else:
        print("⚠️  部分检查未通过，请查看上面的详细信息。")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
