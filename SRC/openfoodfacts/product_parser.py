import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from constants import (
    TITLE_SELECTORS,
    NUTRITION_TABLE_ARIA_LABEL,
    NUTRITION_LABEL_MAP,
    QUANTITY_SELECTOR,
    UNIT_MAP,
    DESCRIPTION_SELECTORS,
    ALLERGENS_LABEL_REGEX,
    ALLERGENS_SPLIT_REGEX,
    INGREDIENTS_PANEL_SELECTOR,
    MAIN_CONTENT_SELECTOR,
)

def _get_text(node) -> str:
    return node.get_text(" ", strip=True) if node else ""

def _extract_title(sp: BeautifulSoup) -> Optional[str]:
    for sel in TITLE_SELECTORS:
        node = sp.select_one(sel)
        if node:
            return _get_text(node)
    return None

def _norm(s: str) -> str:
    """
    Normaliza texto para matching: minúsculas, sin tildes, espacios colapsados.
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", s).strip().lower()

def _find_nutrition_column_index(table) -> int:
    """
    Encuentra el índice de la columna 'por 100 g / 100 ml' usando SOLO la fila de cabecera.
    Fallback al índice 1 si no se detecta.
    """
    head_tr = table.select_one("thead tr") or next((tr for tr in table.select("tr") if tr.find_all("th")), None)
    if head_tr:
        headers = [th.get_text(" ", strip=True) for th in head_tr.find_all(["th", "td"], recursive=False)]
        for i, th in enumerate(headers):
            low = _norm(th).replace(" ", "")
            if "100g" in low or "100ml" in low or "por100g" in low or "por100ml" in low:
                return i if i > 0 else 1
        if len(headers) >= 2:
            return 1
    return 1

def _extract_nutrition(sp: BeautifulSoup) -> Dict[str, str]:
    nutri: Dict[str, str] = {}
    tabla = sp.find("table", attrs={"aria-label": NUTRITION_TABLE_ARIA_LABEL})
    if not tabla:
        return nutri

    idx_col = _find_nutrition_column_index(tabla)
    rows = tabla.tbody.find_all("tr") if getattr(tabla, "tbody", None) else tabla.find_all("tr")

    for tr in rows:
        celdas = tr.find_all(["th", "td"], recursive=False)
        if len(celdas) < 2:
            continue

        etiqueta_raw = _get_text(celdas[0])
        etiqueta = _norm(etiqueta_raw)
        if not etiqueta or etiqueta.startswith("informacion nutricional"):
            continue

        j = idx_col if idx_col < len(celdas) else len(celdas) - 1
        if j == 0 and len(celdas) >= 2:
            j = 1
        valor = _get_text(celdas[j]).strip()
        if not valor:
            continue

        # Ignorar filas no base (por ejemplo, % de frutas/verduras).
        if "frutas" in etiqueta and "verduras" in etiqueta:
            continue

        # Energía (kJ/kcal)
        if "energia" in etiqueta:
            nutri.setdefault("energia", valor)
            continue

        # Grasas saturadas: evitar mono/poli-saturadas
        if "saturad" in etiqueta and "monoinsaturad" not in etiqueta and "poliinsaturad" not in etiqueta:
            nutri.setdefault("grasas_saturadas", valor)
            continue

        # Grasas totales: evitar mono/poli/trans
        if "grasa" in etiqueta and "monoinsaturad" not in etiqueta and "poliinsaturad" not in etiqueta and "trans" not in etiqueta:
            nutri.setdefault("grasas", valor)
            continue

        # Hidratos de carbono
        if "hidrato" in etiqueta or "carbo" in etiqueta:
            nutri.setdefault("hidratos", valor)
            continue

        # Azúcares (excluye añadidos)
        if "azuc" in etiqueta and "anad" not in etiqueta and "añad" not in etiqueta:
            nutri.setdefault("azucares", valor)
            continue

        # Proteínas
        if "prote" in etiqueta:
            nutri.setdefault("proteinas", valor)
            continue

        # Fibra
        if "fibra" in etiqueta:
            nutri.setdefault("fibra", valor)
            continue

        # Sal
        if "sal" in etiqueta:
            nutri.setdefault("sal", valor)
            continue

    return nutri

def _parse_number_and_unit(raw: str) -> Optional[Tuple[float, str]]:
    m = re.search(r"([\d\.,]+)\s*([a-zA-Z]+)", raw)
    if not m:
        return None
    num_txt = m.group(1).replace(".", "").replace(",", ".")
    unidad = m.group(2).lower()
    try:
        val = float(num_txt)
    except Exception:
        return None
    if unidad in UNIT_MAP:
        out_unit, factor = UNIT_MAP[unidad]
        return (val * factor, out_unit)
    return None

def _extract_weight(sp: BeautifulSoup, texto_plano: str) -> Optional[List[Any]]:
    texto = None
    span = sp.select_one(QUANTITY_SELECTOR)
    if span:
        texto = _get_text(span)
    else:
        m = re.search(r"Cantidad\s*:?\s*([^\n\r]+)", texto_plano, flags=re.I)
        if m:
            texto = m.group(1).strip()
    if not texto:
        return None
    parsed = _parse_number_and_unit(texto)
    if not parsed:
        return None
    val, unidad = parsed
    return [val, unidad]

def _clean_after_colon(text: str) -> str:
    return text.split(":", 1)[1].strip() if ":" in text else text

def _extract_description(sp: BeautifulSoup) -> Dict[str, str]:
    descripcion: Dict[str, str] = {}
    bloque = sp.select_one(MAIN_CONTENT_SELECTOR)
    if not bloque:
        return descripcion
    for key, selector in DESCRIPTION_SELECTORS:
        node = bloque.select_one(selector)
        if not node:
            continue
        # Algunos campos contienen span.field_value; si existe, priorizarlo.
        val_node = node.select_one("span.field_value") or node
        valor = _clean_after_colon(_get_text(val_node))
        if valor:
            descripcion[key] = valor
    return descripcion

def _extract_allergens(sp: BeautifulSoup, texto_plano: str) -> List[str]:
    alergenos: List[str] = []
    panel = sp.select_one(INGREDIENTS_PANEL_SELECTOR)
    if panel:
        texto = _get_text(panel)
        m = ALLERGENS_LABEL_REGEX.search(texto)
        if m:
            alergenos = [i.strip() for i in ALLERGENS_SPLIT_REGEX.split(m.group(1)) if i.strip()]
    if not alergenos:
        etiqueta_alerg = sp.find(string=re.compile(r"Al[eé]rgenos\s*:"))
        if etiqueta_alerg:
            par = getattr(etiqueta_alerg, "parent", None)
            texto_alerg = _get_text(par) if par else ""
            m = re.search(r"Al[eé]rgenos\s*:\s*(.+)", texto_alerg, flags=re.I)
            if m:
                lista = m.group(1)
                lista = re.split(r"\bInformaci[oó]n\b|\bicon\b", lista)[0]
                alergenos = [i.strip() for i in ALLERGENS_SPLIT_REGEX.split(lista) if i.strip()]
    if not alergenos:
        m = ALLERGENS_LABEL_REGEX.search(texto_plano)
        if m:
            alergenos = [i.strip() for i in ALLERGENS_SPLIT_REGEX.split(m.group(1)) if i.strip()]
    return alergenos

def parse_product_html(html: str) -> Dict[str, Any]:
    sp = BeautifulSoup(html, "lxml")
    titulo = _extract_title(sp)
    texto_plano = sp.get_text("\n", strip=True)
    nutri = _extract_nutrition(sp)
    peso_volumen = _extract_weight(sp, texto_plano)
    descripcion = _extract_description(sp)
    alergenos = _extract_allergens(sp, texto_plano)

    # Construir el dict final incluyendo solo claves con valor "existente".
    producto: Dict[str, Any] = {}
    if titulo:
        producto["titulo"] = titulo
    if nutri:
        producto["valores_nutricionales_100_g"] = nutri
    if peso_volumen:
        producto["peso_volumen"] = peso_volumen
    if descripcion:
        producto["descripcion"] = descripcion
    if alergenos:
        producto["alergenos"] = alergenos

    return producto
