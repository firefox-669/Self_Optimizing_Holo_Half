# Git 提交前安全检查清单

## ⚠️ 重要：提交前必须检查的项目

### 1. 隐私和敏感信息检查

#### ❌ 绝对不能提交的文件

- [ ] `.env` - 包含真实 API Keys
- [ ] `Self_Optimizing_Holo_Evolution/` - 独立项目，不应在此仓库
- [ ] `ARCHITECTURE_LIMITATIONS.md` - 内部分析文档（72.9KB）
- [ ] `ARCHITECTURE_LIMITATION_MODIFY.md` - 超大内部文档（429.4KB）

#### ✅ .gitignore 已排除的目录

以下目录已在 `.gitignore` 中配置，**不会**被提交：

```
ai_news/          # AI 资讯相关（不属于 SOHH）
analyzer/         # 旧的 analyzer（已被 integrations 替代）
evaluation/       # 旧的 evaluation（已被 evolution_engine 替代）
evolution/        # 旧的 evolution（已被 evolution_engine 替代）
executor/         # 旧的 executor
monitor/          # 旧的 monitor
optimizer/        # 旧的 optimizer（已被 evolution_engine/optimizer 替代）
patches/          # 补丁文件
```

---

### 2. 运行清理检查

```bash
# Windows
cleanup_before_commit.bat

# Linux/Mac
python -c "
import os
import sys

# 检查敏感文件
sensitive_files = ['.env', 'ARCHITECTURE_LIMITATIONS.md', 'ARCHITECTURE_LIMITATION_MODIFY.md']
for f in sensitive_files:
    if os.path.exists(f):
        print(f'[WARNING] {f} exists but should be ignored')
    else:
        print(f'[OK] {f} not found')

# 检查 API Keys
import glob
for py_file in glob.glob('**/*.py', recursive=True):
    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if 'api_key = \"sk-' in content or 'password = \"' in content:
            print(f'[WARNING] Potential secrets in {py_file}')
"
```

---

### 3. 验证 .gitignore 规则

```bash
# 测试关键文件是否被忽略
git check-ignore ARCHITECTURE_LIMITATIONS.md
git check-ignore ARCHITECTURE_LIMITATION_MODIFY.md
git check-ignore ai_news/
git check-ignore .env

# 如果返回文件路径，说明已被正确忽略
# 如果没有输出，说明未被忽略（需要修复）
```

---

### 4. 检查暂存区文件

```bash
# 查看所有将被提交的文件
git add .
git status

# 仔细检查输出，确保没有：
# - .env 文件
# - ARCHITECTURE_LIMITATIONS*.md
# - ai_news/, analyzer/ 等旧目录
# - Self_Optimizing_Holo_Evolution/ 目录
```

**预期应该看到的文件**:
```
README.md
LICENSE
.gitignore
.env.example
requirements.txt
IMPLEMENTATION_PLAN.md
COMPLETION_REPORT.md
RELEASE_CHECKLIST.md
quick_test.py
run_tests.bat

core/
integrations/
evolution_engine/
user_scoring/
mode_management/
version_control/
reporting/
```

**不应该看到的文件**:
```
.env
ARCHITECTURE_LIMITATIONS.md
ARCHITECTURE_LIMITATION_MODIFY.md
ai_news/
analyzer/
evaluation/
evolution/
executor/
monitor/
optimizer/
patches/
Self_Optimizing_Holo_Evolution/
```

---

### 5. 如果发现敏感文件已被暂存

```bash
# 从暂存区移除（但保留在本地）
git rm --cached .env
git rm --cached ARCHITECTURE_LIMITATIONS.md
git rm --cached ARCHITECTURE_LIMITATION_MODIFY.md
git rm --cached -r ai_news/
git rm --cached -r analyzer/
# ... 其他目录

# 重新检查
git status
```

---

### 6. 搜索代码中的硬编码密钥

```bash
# Windows PowerShell
Get-ChildItem -Recurse -Filter *.py | Select-String -Pattern "api_key\s*=\s*['\"]sk-"

# Linux/Mac
grep -r "api_key.*=.*['\"]sk-" --include="*.py" .

# 如果发现，立即删除或移到 .env 文件
```

---

### 7. 最终确认清单

提交前确认：

- [ ] 没有 `.env` 文件在暂存区
- [ ] 没有 `ARCHITECTURE_LIMITATIONS*.md` 文件
- [ ] 没有旧目录（ai_news, analyzer, 等）
- [ ] 没有 `Self_Optimizing_Holo_Evolution/` 目录
- [ ] 代码中没有硬编码的 API Keys
- [ ] README.md 已更新
- [ ] LICENSE 已添加
- [ ] .gitignore 已配置
- [ ] requirements.txt 已更新

---

## 🚨 如果不小心提交了敏感信息

### 立即行动：

1. **撤销最后一次提交**（如果还没推送）:
   ```bash
   git reset HEAD~1
   ```

2. **从历史记录中完全删除**:
   ```bash
   # 使用 BFG Repo-Cleaner（推荐）
   java -jar bfg.jar --delete-files .env my-repo.git
   
   # 或使用 git filter-branch
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env' \
     --prune-empty --tag-name-filter cat -- --all
   ```

3. **强制推送**（谨慎使用）:
   ```bash
   git push origin --force --all
   ```

4. **轮换所有泄露的密钥**:
   - 立即更改所有 API Keys
   - 更新密码
   - 通知相关人员

---

## ✅ 安全提交流程

```bash
# 1. 运行清理检查
cleanup_before_commit.bat

# 2. 添加文件
git add .

# 3. 检查暂存区
git status

# 4. 确认无误后提交
git commit -m "Your message"

# 5. 推送到远程
git push origin main
```

---

## 📞 需要帮助？

如果不确定某个文件是否应该提交，请问：
1. 这个文件包含敏感信息吗？（API Keys, passwords, tokens）
2. 这个文件是内部文档吗？（不对外公开的分析）
3. 这个文件是临时文件吗？（logs, cache, build artifacts）
4. 这个文件在其他项目中吗？（不应该跨项目共享）

如果以上任一答案是 "是"，则**不应该提交**。
