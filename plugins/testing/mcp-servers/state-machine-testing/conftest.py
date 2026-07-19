"""pytest 配置：把 src/ 加入 sys.path，让测试可直接 import。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
