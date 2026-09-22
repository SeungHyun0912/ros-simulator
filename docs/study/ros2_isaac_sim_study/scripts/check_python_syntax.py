from pathlib import Path
import ast
root=Path(__file__).resolve().parents[1]
files=sorted(root.rglob("*.py"))
for path in files:
    ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
print(f"AST syntax checked: {len(files)} Python files (imports not executed)")
