import logging
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "sales_agent") -> logging.Logger:
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 文件输出
    log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    # 控制台输出
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(sh)

    return logger
