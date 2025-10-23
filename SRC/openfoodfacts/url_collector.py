import requests
from urllib.parse import urlsplit, urlunsplit
from typing import List, Set
from constants import PRODUCT_URL_REGEX

def _normalize_url(u: str) -> str:
    partes = urlsplit(u)
    return urlunsplit((partes.scheme, partes.netloc, partes.path, "", ""))

def collect_product_urls(
    base_url: str,
    target_count: int,
    headers: dict,
    timeout: int,
    max_pages: int,
) -> List[str]:
    urls: List[str] = []
    vistos: Set[str] = set()
    pagina = 1

    while len(urls) < target_count and pagina <= max_pages:
        url_listado = base_url if pagina == 1 else f"{base_url}{pagina}"
        print(f"\nListado página {pagina}: {url_listado}")
        try:
            r = requests.get(url_listado, headers=headers, timeout=timeout)
            html = r.text
            print("  Estado:", r.status_code, "Tamaño:", len(html))
        except Exception as e:
            print("  Error al descargar listado:", e)
            break

        encontrados = PRODUCT_URL_REGEX.findall(html)
        nuevos = 0
        for u in encontrados:
            limpia = _normalize_url(u)
            if limpia in vistos:
                continue
            vistos.add(limpia)
            urls.append(limpia)
            nuevos += 1
            if len(urls) >= target_count:
                break

        print(f"  Encontradas en la página: {nuevos} (acumuladas: {len(urls)})")
        pagina += 1

    print(f"\nTotal URLs recolectadas: {len(urls)}")
    for i, u in enumerate(urls[:5], start=1):
        print(f"  Ejemplo {i}: {u}")
    return urls
