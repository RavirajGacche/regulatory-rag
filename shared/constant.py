from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version

API_TITLE = "Regulatory RAG API"
API_DESCRIPTION = "Compliance intelligence over RBI circulars."
API_V1_PREFIX = "/v1"

try:
    APP_VERSION = pkg_version("regulatory-rag")  # Read from the installed package
except PackageNotFoundError:
    APP_VERSION = "0.0.0-dev"  # not installed
