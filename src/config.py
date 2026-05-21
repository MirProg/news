import os

SITE_NAME = "Infinite Engine"
SITE_URL = "https://your-site.com"
SITE_DESC = "unprecedented sports prediction framework — PyTorch multi-model ensemble with Monte Carlo, Elo, Poisson, and Bayesian inference."

N_SIMS = 100000
N_SEASON_ROUNDS = 10

# Priority: 1) DEEPSEEK, 2) OPENAI, 3) ANTHROPIC, 4) GOOGLE, 5) LOCAL
_raw_deepseek = os.getenv("DEEPSEEK_API_KEY", "")
_raw_openai = os.getenv("OPENAI_API_KEY", "")
_raw_anthropic = os.getenv("ANTHROPIC_API_KEY", "")
_raw_google = os.getenv("GOOGLE_API_KEY", "")

DEEPSEEK_API_KEY = _raw_deepseek if _raw_deepseek.startswith("sk-") else ""
OPENAI_API_KEY = _raw_openai if _raw_openai.startswith("sk-") else ""
ANTHROPIC_API_KEY = _raw_anthropic if _raw_anthropic.startswith("sk-ant-") else ""
GOOGLE_API_KEY = _raw_google if _raw_google.startswith("AIza") else ""

DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")

LOCAL_AI_ENABLED = os.getenv("LOCAL_AI", "").lower() in ("1", "true", "yes")

AI_ENABLED = bool(DEEPSEEK_API_KEY or OPENAI_API_KEY or ANTHROPIC_API_KEY or GOOGLE_API_KEY or LOCAL_AI_ENABLED)

if DEEPSEEK_API_KEY:
    AI_PROVIDER = "deepseek"
elif OPENAI_API_KEY:
    AI_PROVIDER = "openai"
elif ANTHROPIC_API_KEY:
    AI_PROVIDER = "anthropic"
elif GOOGLE_API_KEY:
    AI_PROVIDER = "google"
elif LOCAL_AI_ENABLED:
    AI_PROVIDER = "local"
else:
    AI_PROVIDER = "none"


