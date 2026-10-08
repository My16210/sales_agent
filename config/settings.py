"""
统一配置加载模块
企业标准做法：所有配置从 .env 读取，代码中不硬编码密钥
用法：
    from config.settings import settings
    llm = ChatOpenAI(**settings.get_llm_kwargs("deepseek"))  # 指定模型
    llm = ChatOpenAI(**settings.get_llm_kwargs())              # 默认deepseek
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 无论从哪个子目录启动，都加载仓库根目录的 .env
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")


class Settings:
    """所有配置集中管理，方便全局调用"""

    # ===== 多模型配置（每个模型提供商一段） =====
    # 以后加新模型：在.env里加3行，在这里加一段配置即可
    LLM_CONFIGS: dict = {
        "deepseek": {
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", "0.3")),
        },
        "openai": {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
        },
        "qwen": {
            "model": os.getenv("QWEN_MODEL", "qwen-plus"),
            "api_key": os.getenv("QWEN_API_KEY", ""),
            "base_url": os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            "temperature": float(os.getenv("QWEN_TEMPERATURE", "0.3")),
        },
        # 以后加新模型，复制上面一段改名字就行
    }

    # ===== Embedding（RAG向量化用） =====
    # DeepSeek无官方embedding，需用其他服务（SiliconFlow/本地BGE等）
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", "")
    EMBEDDING_BASE_URL: str = os.getenv("EMBEDDING_BASE_URL", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "")

    # ===== 数据路径（集中管理，避免各节点硬编码） =====
    DATA_DIR: Path = _ROOT / "data"
    RAW_CSV_PATH: Path = DATA_DIR / "raw" / "sales.csv"
    OUTPUT_DIR: Path = DATA_DIR / "output"

    # ===== MySQL（Text-SQL用，可选） =====
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "")

    def get_mysql_url(self) -> str:
        """生成SQLAlchemy连接字符串"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    def get_llm_kwargs(self, provider: str = "deepseek") -> dict:
        """
        获取ChatOpenAI初始化参数
        :param provider: 模型提供商，默认deepseek，可选：deepseek/openai/qwen
        """
        if provider not in self.LLM_CONFIGS:
            available = list(self.LLM_CONFIGS.keys())
            raise ValueError(f"不支持的模型提供商: {provider}，可选: {available}")
        kwargs = self.LLM_CONFIGS[provider].copy()
        if not kwargs.get("api_key"):
            raise ValueError(
                f"未配置 {provider} 的 API Key。请复制 .env.example 为 .env 并填写对应变量。"
            )
        return kwargs

    def list_providers(self) -> list:
        """列出所有已配置的模型提供商"""
        return list(self.LLM_CONFIGS.keys())


# 全局单例，其他模块直接 import 使用
settings = Settings()
