import json
import re
from functools import lru_cache
from pathlib import Path
from app.config import settings


# Common barista aliases not always spelled identically to the master sheet
MATERIAL_ALIASES: dict[str, list[str]] = {
    "KOP01": ["kopi", "biji kopi", "espresso", "bean", "beans"],
    "KOP03": ["susu", "susu uht", "uht", "fresh milk", "milk", "diamond"],
    "KOP14": ["butterscotch", "sirup butterscotch"],
    "KOP15": ["karamel", "caramel", "sirup karamel", "sirup caramel"],
    "KOP16": ["gula aren", "aren", "sirup aren"],
    "KOP17": ["vanilla", "vanila", "sirup vanilla"],
    "MAT01": ["matcha", "bubuk matcha", "green tea"],
    "BAR14": ["cup reguler", "cup r", "gelas reguler"],
    "BAR19": ["cup large", "cup l", "gelas large"],
    "BAR12": ["es batu", "es", "ice"],
    "BAR15": ["tutup cup", "lid"],
    "BAR16": ["sedotan", "straw"],
}


class KnowledgeBase:
    def __init__(self, kb_path: Path):
        with open(kb_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self.materials: dict[str, dict] = {m["id"]: m for m in raw.get("materials", [])}
        self.menus: dict[str, dict] = {m["id"]: m for m in raw.get("menus", [])}
        self.recipes: list[dict] = raw.get("recipes", [])
        self._material_to_menus: dict[str, list[str]] = {}
        self._menu_recipes: dict[str, list[dict]] = {}
        self._build_indexes()

    def _build_indexes(self) -> None:
        for recipe in self.recipes:
            menu_id = recipe["menu_id"]
            menu_name = recipe["menu_name"]
            self._menu_recipes.setdefault(menu_id, []).append(recipe)
            for ing in recipe.get("ingredients", []):
                mat_id = ing["material_id"]
                menus = self._material_to_menus.setdefault(mat_id, [])
                if menu_name not in menus:
                    menus.append(menu_name)

        # Fallback to menu candidate_ingredients when a material has no formal recipe rows yet
        name_to_id = {m["name"].lower(): mid for mid, m in self.materials.items()}
        for menu in self.menus.values():
            for cand in menu.get("candidate_ingredients", []):
                mat_id = name_to_id.get(cand.lower())
                if mat_id:
                    menus = self._material_to_menus.setdefault(mat_id, [])
                    if menu["name"] not in menus:
                        menus.append(menu["name"])

    def get_affected_menus(self, material_id: str) -> list[str]:
        return self._material_to_menus.get(material_id, [])

    def get_affected_menu_records(self, material_id: str) -> list[dict]:
        affected_names = set(self.get_affected_menus(material_id))
        return [m for m in self.menus.values() if m["name"] in affected_names]

    def find_materials_in_text(self, normalized_text: str) -> list[str]:
        matched: list[str] = []
        padded = f" {normalized_text} "

        for mat_id, mat in self.materials.items():
            candidates = [mat["name"].lower()] + MATERIAL_ALIASES.get(mat_id, [])
            # Sort longest first so "sirup karamel" matches before "karamel"
            for term in sorted(candidates, key=len, reverse=True):
                if re.search(rf"\b{re.escape(term)}\b", padded):
                    if mat_id not in matched:
                        matched.append(mat_id)
                    break
        return matched

    def find_menus_in_text(self, normalized_text: str) -> list[dict]:
        matched: list[dict] = []
        for menu in self.menus.values():
            name_lower = menu["name"].lower()
            if name_lower in normalized_text:
                matched.append(menu)
        return matched

    def get_recipes_for_menu(self, menu_id: str) -> list[dict]:
        return self._menu_recipes.get(menu_id, [])


@lru_cache(maxsize=1)
def get_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase(settings.kb_path)
