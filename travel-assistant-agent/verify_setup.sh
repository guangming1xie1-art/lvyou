#!/bin/bash

# 简单验证脚本：检查项目结构和关键文件

echo "============================================"
echo "Travel Assistant Agent - Setup Verification"
echo "============================================"

PROJECT_ROOT="/home/engine/project/travel-assistant-agent"

echo ""
echo "[1/6] Checking project structure..."
for dir in "src/agents" "src/workflows" "src/tools" "src/utils" "src/models" "tests"; do
  if [ -d "$PROJECT_ROOT/$dir" ]; then
    echo "  ✓ $dir"
  else
    echo "  ✗ $dir (missing)"
  fi
done

echo ""
echo "[2/6] Checking key configuration files..."
for file in "pyproject.toml" "requirements.txt" "Dockerfile" "docker-compose.yml" ".env.example" "README.md"; do
  if [ -f "$PROJECT_ROOT/$file" ]; then
    echo "  ✓ $file"
  else
    echo "  ✗ $file (missing)"
  fi
done

echo ""
echo "[3/6] Checking Agent source files..."
for file in "src/agents/base.py" "src/agents/info_collection.py" "src/agents/search.py" "src/agents/recommendation.py" "src/agents/booking.py"; do
  if [ -f "$PROJECT_ROOT/$file" ]; then
    echo "  ✓ $file"
  else
    echo "  ✗ $file (missing)"
  fi
done

echo ""
echo "[4/6] Checking utility modules..."
for file in "src/config.py" "src/main.py" "src/utils/logger.py" "src/utils/db.py" "src/utils/claude.py" "src/utils/api_client.py"; do
  if [ -f "$PROJECT_ROOT/$file" ]; then
    echo "  ✓ $file"
  else
    echo "  ✗ $file (missing)"
  fi
done

echo ""
echo "[5/6] Checking workflows..."
if [ -f "$PROJECT_ROOT/src/workflows/planning_workflow.py" ]; then
  echo "  ✓ src/workflows/planning_workflow.py"
else
  echo "  ✗ src/workflows/planning_workflow.py (missing)"
fi

echo ""
echo "[6/6] Checking Python syntax (basic)..."
cd "$PROJECT_ROOT"
if command -v python3 &> /dev/null; then
  for file in src/*.py src/**/*.py; do
    if [ -f "$file" ]; then
      python3 -m py_compile "$file" 2>/dev/null
      if [ $? -eq 0 ]; then
        echo "  ✓ $file"
      else
        echo "  ✗ $file (syntax error)"
      fi
    fi
  done
else
  echo "  ! Python3 not found, skipping syntax check"
fi

echo ""
echo "============================================"
echo "Verification Complete!"
echo "============================================"
