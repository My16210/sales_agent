"""统一配置包。密钥从 .env 读取，示例代码通过本包复用。"""
from config.settings import settings

__all__ = ["settings"]
