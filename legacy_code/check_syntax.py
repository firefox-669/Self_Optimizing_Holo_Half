"""
验证所有 Python 文件的语法正确性
"""

import sys
import py_compile
from pathlib import Path
from typing import List, Tuple


def check_syntax(file_path: Path) -> Tuple[bool, str]:
    """检查单个文件的语法"""
    try:
        py_compile.compile(str(file_path), doraise=True)
        return True, ""
    except py_compile.PyCompileError as e:
        return False, str(e)


def main():
    """主函数"""
    project_root = Path(__file__).parent
    
    print("="*70)
    print("Python Syntax Checker")
    print("="*70)
    print()
    
    # 查找所有 Python 文件
    python_files = list(project_root.rglob("*.py"))
    python_files = [f for f in python_files if not f.name.startswith(".")]
    
    print(f"Found {len(python_files)} Python files\n")
    
    errors = []
    checked = 0
    
    for file_path in sorted(python_files):
        # 跳过虚拟环境和缓存目录
        if any(part in ['.venv', 'venv', '__pycache__', '.git'] for part in file_path.parts):
            continue
        
        checked += 1
        is_valid, error_msg = check_syntax(file_path)
        
        if is_valid:
            print(f"✅ {file_path.relative_to(project_root)}")
        else:
            print(f"❌ {file_path.relative_to(project_root)}")
            print(f"   Error: {error_msg}")
            errors.append((file_path, error_msg))
    
    print("\n" + "="*70)
    print(f"Checked: {checked} files")
    print(f"Errors: {len(errors)}")
    print("="*70)
    
    if errors:
        print("\n❌ SYNTAX ERRORS FOUND:")
        for file_path, error in errors:
            print(f"\n{file_path.relative_to(project_root)}:")
            print(f"  {error}")
        return False
    else:
        print("\n✅ ALL FILES PASSED SYNTAX CHECK!")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
