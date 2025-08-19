import requests
from bs4 import BeautifulSoup

def fetch_and_clean(url: str) -> str:
    """Descarga y limpia el contenido de una URL"""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Eliminar scripts, estilos y etiquetas innecesarias
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # Limpiar saltos de línea extra
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
