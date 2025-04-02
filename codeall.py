import json
import xml.etree.ElementTree as ET
import zlib
import base64
import sys

def log(message):
    print("[LOG]", message)

# --- Funciones para crear secciones del XML a partir del JSON de Character ---

def create_build_from_character(char):
    log("Creando Build...")
    build = ET.Element("Build")
    # Mapeo de atributos básicos
    build.set("level", str(char.get("level", "")))
    build.set("className", char.get("class", "")[:-1])
    # Valores fijos o por defecto para atributos propios de PoB
    build.set("ascendClassName", "nil") #TODO cambiar segun mapa por hacer
    build.set("targetVersion", "0_1")
    build.set("characterLevelAutoMode", "true")
    build.set("mainSocketGroup", "1")
    build.set("viewMode", "IMPORT")
    # Agregar un TimelessData por defecto
    ps = ET.SubElement(build, "TimelessData")
    ps.set("devotionVariant2", "1")
    ps.set("searchListFallback", "")
    ps.set("searchList", "")
    ps.set("devotionVariant1", "1")
    return build

def create_tree_from_passives(passives, char):
    class_map = {
        "Ranger1": ("0", "1"), #Tested Deadeye
        "Ranger2": ("0", "2"),
        "Monk1": ("5", "2"), #Tested Invoker
        "Monk2": ("5", "1"),
        "Mercenary1": ("2", "1"),
        "Mercenary3": ("2", "2"), #Tested Gemling Legionary
        "Sorceress1": ("4", "1"), #Tested Stormweaver
        "Sorceress2": ("4", "2"), #Tested Chronomancer
        "Witch1": ("3", "1"), #Tested Infernalist
        "Witch2": ("3", "2") 
    }

    log("Creando Tree a partir de passives...")
    tree = ET.Element("Tree")
    tree.set("activeSpec", "1")
    spec = ET.SubElement(tree, "Spec")
    spec.set("masteryEffects", "")
    if "hashes" in passives and isinstance(passives["hashes"], list):
        nodes = ",".join(str(x) for x in passives["hashes"])
        spec.set("nodes", nodes)
        log(f"Set Spec nodes: {nodes}")
    else:
        spec.set("nodes", "")
    spec.set("secondaryAscendClassId", str(passives.get("secondaryAscendClassId", "nil")))
    spec.set("treeVersion", "0_1")
    
    if char.get("class", "") in class_map:
        class_id, ascend_class_id = class_map[char.get("class", "")]
        spec.set("classId", class_id)
        spec.set("ascendClassId", ascend_class_id)
    else:
        spec.set("classId", "0")
        spec.set("ascendClassId", char.get("class", "")[-1])
    
    # Agregar URL
    url_elem = ET.SubElement(spec, "URL")
    url_elem.text = "https://www.pathofexile.com/passive-skill-tree/AAAABgIBicpx5B3lvgD0wfljqfgmuQNE7oVYjuAadN5O8hU0Y22McUAJHnCj9ABvjI6qj6qLcIbFDInmlIyTrY5u0pbJk4dzJ4ubLPA5hRuWecQUuUW-Gxe9zJ8P01MJaMBE-ZClqiwzf6s1jKJsrug-ZyS9MDHqC38x1sjUCtfr8ckLH5yEQGm8CdNvqjoHMTMZyfsnRbrwvRFPrUwOMlrpSBSv6ele36hKi1cNZ6yQOpUmCbxG1ZNBKF4G-PP2CO0_U1jpXL37LjFg-WHfpSioe5d73g-EX68k_kMqnVLVQEy4Ltn6hN-Fud7XH5wjPL6FsNiOfyPMDoXLnXh3Th6MPQmXvs7sWW2Srj2uFsSYVPsXSWDtoPoAAA=="
        
    # Agregar WeaponSet1
    weapon_set1 = ET.SubElement(spec, "WeaponSet1")
    if "specialisations" in passives and "set1" in passives["specialisations"] and isinstance(passives["specialisations"]["set1"], list):
        weapon_set1_nodes = ",".join(str(x) for x in passives["specialisations"]["set1"])
        weapon_set1.set("nodes", weapon_set1_nodes)
        log(f"Set WeaponSet1 nodes: {weapon_set1_nodes}")
    else:
        weapon_set1.set("nodes", "")

    # Agregar WeaponSet2
    weapon_set2 = ET.SubElement(spec, "WeaponSet2")
    if "specialisations" in passives and "set2" in passives["specialisations"] and isinstance(passives["specialisations"].get("set2", []), list):
        weapon_set2_nodes = ",".join(str(x) for x in passives["specialisations"]["set2"])
        weapon_set2.set("nodes", weapon_set2_nodes)
        log(f"Set WeaponSet2 nodes: {weapon_set2_nodes}")
    else:
        weapon_set2.set("nodes", "")
    
    # Agregar Sockets
    sockets_elem = ET.SubElement(spec, "Sockets")
    # Sin rellenar los sockets ya que no se sabe la posicion (el poe planner lo pone aleatorio cosa que veo peor)
    #if "jewel_data" in passives and isinstance(passives["jewel_data"], dict):
    #    for node_id, jewel_info in passives["jewel_data"].items():
    #        socket = ET.SubElement(sockets_elem, "Socket")
    #        socket.set("nodeId", str(node_id))
    #        socket.set("itemId", str(jewel_info.get("type", "")))
    #        log(f"Added Socket: nodeId={node_id}, itemId={jewel_info.get('type', '')}")

    # Agregar Overrides
    overrides_elem = ET.SubElement(spec, "Overrides")
    attribute_override = ET.SubElement(overrides_elem, "AttributeOverride")

    # Inicializar listas para cada tipo de nodo
    str_nodes = []
    dex_nodes = []
    int_nodes = []

    # Analizar skill_overrides para clasificar los nodos
    if "skill_overrides" in passives and isinstance(passives["skill_overrides"], dict):
        for node_id, override_info in passives["skill_overrides"].items():
            if "grantedIntelligence" in override_info:
                int_nodes.append(node_id)
            elif "grantedDexterity" in override_info:
                dex_nodes.append(node_id)
            elif "grantedStrength" in override_info:
                str_nodes.append(node_id)

    # Establecer atributos en AttributeOverride
    attribute_override.set("strNodes", ",".join(str_nodes))
    attribute_override.set("dexNodes", ",".join(dex_nodes))
    attribute_override.set("intNodes", ",".join(int_nodes))

    log(f"Set AttributeOverride: strNodes={','.join(str_nodes)}, dexNodes={','.join(dex_nodes)}, intNodes={','.join(int_nodes)}")
    return tree

def create_skills_from_character(char):
    log("Creando Skills a partir de Character.skills...")
    skills = ET.Element("Skills")
    skills.set("sortGemsByDPSField", "CombinedDPS")
    skills.set("activeSkillSet", "1")
    skills.set("sortGemsByDPS", "true")
    skills.set("defaultGemQuality", "nil")
    skills.set("defaultGemLevel", "normalMaximum")
    skills.set("showSupportGemTypes", "ALL")
    skillset = ET.SubElement(skills, "SkillSet")
    skillset.set("id", "1")
    
    # Revisar si hay skills en el personaje
    if "skills" in char and isinstance(char["skills"], list):
        for sk_index, sk in enumerate(char["skills"]):
            if sk.get('typeLine', '') in ["Bow Shoot", "Punch", "Mace Strike"]: # Todo ir añadiendo si no son necesarios
                continue
            
            skill_elem = ET.SubElement(skillset, "Skill")
            skill_elem.set("mainActiveSkillCalcs", "1")
            skill_elem.set("includeInFullDPS", "nil")
            skill_elem.set("label", "")
            skill_elem.set("enabled", "true")
            skill_elem.set("mainActiveSkill", "1")
            
            log(f"Agregado Skill: {sk.get('typeLine', '')}")
            
            # Procesar la skill principal (la misma skill)
            main_gem = ET.SubElement(skill_elem, "Gem")
            main_gem.set("enableGlobal2", "true")
            main_gem.set("enableGlobal1", "true")
            main_gem.set("enabled", "true")
            main_gem.set("count", "1")
            
            # Obtener detalles de la skill principal
            quality_value = "0"
            if "properties" in sk:
                for prop in sk["properties"]:
                    if prop.get("name") == "Level" and prop.get("values"):
                        main_gem.set("level", str(prop["values"][0][0]).replace(" (Max)", ""))
                    if prop.get("name") == "[Quality]" and prop.get("values"):
                        quality_value = prop["values"][0][0].replace("+", "").replace("%", "")
                        
            main_gem.set("quality", quality_value)
            
            # Configurar atributos básicos
            main_gem.set("nameSpec", sk.get("typeLine", ""))
            base_type = sk.get("baseType", sk.get("typeLine", ""))
            main_gem.set("gemId", f"Metadata/Items/Gem/SkillGem{base_type.replace(' ', '')}")
            
            # Si hay un ID específico para la skill, usarlo
            main_gem.set("skillId", f"{base_type.replace(' ', '')}Player")
            main_gem.set("variantId", base_type.replace(' ', ''))
            
            # Procesar las gemas de soporte (socketedItems)
            if "socketedItems" in sk and isinstance(sk["socketedItems"], list):
                for gem_index, gem in enumerate(sk["socketedItems"]):
                    if isinstance(gem, dict):
                        support_gem = ET.SubElement(skill_elem, "Gem")
                        support_gem.set("enableGlobal2", "true")
                        support_gem.set("enableGlobal1", "true")
                        support_gem.set("enabled", "true")
                        support_gem.set("count", "1")
                        
                        # Obtener nivel y calidad si están disponibles
                        if "properties" in gem:
                            for prop in gem["properties"]:
                                if prop.get("name") == "Level" and prop.get("values"):
                                    support_gem.set("level", str(prop["values"][0][0]))
                                if prop.get("name") == "[Quality]" and prop.get("values"):
                                    quality_value = prop["values"][0][0].replace("+", "").replace("%", "")
                                    support_gem.set("quality", quality_value)
                        
                        # Si no se encontró nivel, establecer valor predeterminado
                        if "level" not in support_gem.attrib:
                            support_gem.set("level", "1")
                        
                        # Si no se encontró calidad, establecer valor predeterminado
                        if "quality" not in support_gem.attrib:
                            support_gem.set("quality", "0")
                        
                        gem_name = gem.get("typeLine", "")
                        support_gem.set("nameSpec", gem_name)
                        
                        # Crear IDs apropiados para la gema de soporte
                        gem_id = gem_name.replace(" ", "")
                        support_gem.set("gemId", f"Metadata/Items/Gems/SupportGem{gem_id}")
                        support_gem.set("skillId", f"Support{gem_id}Player")
                        support_gem.set("variantId", f"{gem_id}Support")
    else:
        log("No se encontraron skills en character.")
    
    return skills

def create_items_from_character(char):
    log("Creando Items a partir de Character.equipment y jewels...")
    items = ET.Element("Items")
    items.set("activeItemSet", "1")
    items.set("showStatDifferences", "true")
    items.set("useSecondWeaponSet", "false")
    
    item_id = 1
    item_inventory_map = {}  # Mapa para relacionar item_id con inventoryId
    item_basetype_map = {}   # Mapa para guardar el baseType de cada item
    
    # Procesar equipment
    if "equipment" in char and isinstance(char["equipment"], list):
        for eq in char["equipment"]:
            item_elem = ET.Element("Item")
            item_elem.set("id", str(item_id))
            
            # Guardar relación entre item_id e inventoryId
            if "inventoryId" in eq:
                item_inventory_map[item_id] = eq["inventoryId"]
                
            # Guardar baseType para usarlo luego en la asignación de Flask/Charm
            if "typeLine" in eq:
                item_basetype_map[item_id] = eq["typeLine"]
            
            item_id += 1
            
            text_lines = []
            
            # Rarity
            rarity_map = {
                "Unique": "UNIQUE",
                "Rare": "RARE",
                "Magic": "MAGIC",
                "Normal": "NORMAL"
            }
            rarity = rarity_map.get(eq.get('rarity', ''), eq.get('rarity', ''))
            text_lines.append(f"Rarity: {rarity}")
            
            # Name and type
            if eq.get("name", "") and eq.get("name") != "":
                text_lines.append(eq.get("name", ""))
            text_lines.append(eq.get("typeLine", ""))
            
            # Item level
            text_lines.append(f"Item Level: {eq.get('ilvl', '')}")
            
            # Quality
            if "properties" in eq and isinstance(eq["properties"], list):
                for prop in eq["properties"]:
                    if prop.get("name") == "[Quality]" and len(prop.get("values", [])) > 0:
                        quality_value = prop["values"][0][0].replace("+", "")
                        text_lines.append(f"Quality: {quality_value}")
                        break
            
            # Sockets
            if "sockets" in eq and isinstance(eq["sockets"], list):
                socket_str = ""
                for socket in eq["sockets"]:
                    if socket.get("type") == "rune":
                        socket_str += "S "
                socket_str = socket_str.strip()
                if socket_str:
                    text_lines.append(f"Sockets: {socket_str}")
            
            # Runes
            if "socketedItems" in eq and isinstance(eq["socketedItems"], list):
                for socket_item in eq["socketedItems"]:
                    if socket_item.get("typeLine"):
                        text_lines.append(f"Rune: {socket_item.get('typeLine', '')}")
            
            # Requirements
            if "requirements" in eq and isinstance(eq["requirements"], list):
                for req in eq["requirements"]:
                    if req.get("name") == "Level" and len(req.get("values", [])) > 0:
                        text_lines.append(f"LevelReq: {req['values'][0][0]}")
            
            # Implicits count
            implicit_count = 0
            if "enchantMods" in eq and isinstance(eq["enchantMods"], list):
                implicit_count += len(eq["enchantMods"])
            
            if "runeMods" in eq and isinstance(eq["runeMods"], list):
                implicit_count += len(eq["runeMods"])
                
            if "implicitMods" in eq and isinstance(eq["implicitMods"], list):
                implicit_count += len(eq["implicitMods"])
                
            if implicit_count > 0:
                text_lines.append(f"Implicits: {implicit_count}")
            
            # Enchant mods
            if "enchantMods" in eq and isinstance(eq["enchantMods"], list):
                for mod in eq["enchantMods"]:
                    text_lines.append(f"{{enchant}}{mod}")
            
            # Rune mods
            if "runeMods" in eq and isinstance(eq["runeMods"], list):
                for mod in eq["runeMods"]:
                    text_lines.append(f"{{enchant}}{{rune}}{mod}")
            
            # Implicit mods
            if "implicitMods" in eq and isinstance(eq["implicitMods"], list):
                for mod in eq["implicitMods"]:
                    text_lines.append(mod)
            
            # Properties like damage, critical chance, etc.
            if "properties" in eq and isinstance(eq["properties"], list):
                for prop in eq["properties"]:
                    if prop.get("name") == "[Physical] Damage" and len(prop.get("values", [])) > 0:
                        text_lines.append(f"Physical Damage: {prop['values'][0][0]}")
                    elif prop.get("name") == "[ElementalDamage|Elemental] Damage" and len(prop.get("values", [])) > 0:
                        for i, val in enumerate(prop["values"]):
                            if i == 0:  # Fire damage
                                text_lines.append(f"Fire Damage: {val[0]}")
                            elif i == 1:  # Cold damage
                                text_lines.append(f"Cold Damage: {val[0]}")
                            elif i == 2:  # Lightning damage
                                text_lines.append(f"Lightning Damage: {val[0]}")
                    elif prop.get("name") == "[Critical|Critical Hit] Chance" and len(prop.get("values", [])) > 0:
                        text_lines.append(f"Critical Hit Chance: {prop['values'][0][0]}")
                    elif prop.get("name") == "Attacks per Second" and len(prop.get("values", [])) > 0:
                        text_lines.append(f"Attacks per Second: {prop['values'][0][0]}")
                    elif prop.get("name") == "[Armour]" and len(prop.get("values", [])) > 0:
                        text_lines.append(f"Armour: {prop['values'][0][0]}")
                    elif prop.get("name") == "[Evasion|Evasion Rating]" and len(prop.get("values", [])) > 0:
                        text_lines.append(f"Evasion: {prop['values'][0][0]}")
                    elif prop.get("name") == "[EnergyShield|Energy Shield]" and len(prop.get("values", [])) > 0:
                        text_lines.append(f"Energy Shield: {prop['values'][0][0]}")
            
            # Explicit mods
            if "explicitMods" in eq and isinstance(eq["explicitMods"], list):
                for mod in eq["explicitMods"]:
                    text_lines.append(mod)
            
            # Flavour text
            if "flavourText" in eq and isinstance(eq["flavourText"], list):
                text_lines.append("")  # Add empty line before flavour text
                for line in eq["flavourText"]:
                    text_lines.append(line)
            
            # Corrupted status
            if eq.get("corrupted", False):
                text_lines.append("Corrupted")
            
            # Set the completed text to the item element
            item_elem.text = "\n".join(text_lines)
            log(f"Agregado Item: {eq.get('id', '')}")
            items.append(item_elem)
    else:
        log("No se encontró equipment en character.")
    
    # Procesar jewels
    jewel_ids = []  # Lista para guardar los IDs de los jewels
    if "jewels" in char and isinstance(char["jewels"], list):
        for jewel in char["jewels"]:
            item_elem = ET.Element("Item")
            item_elem.set("id", str(item_id))
            
            # Guardar ID del jewel para usarlo después
            jewel_ids.append(item_id)
            
            item_id += 1
            
            text_lines = []
            
            # Rarity
            rarity_map = {
                "Unique": "UNIQUE",
                "Rare": "RARE",
                "Magic": "MAGIC",
                "Normal": "NORMAL"
            }
            rarity = rarity_map.get(jewel.get('rarity', ''), jewel.get('rarity', ''))
            text_lines.append(f"Rarity: {rarity}")
            
            # Name and type
            if jewel.get("name", "") and jewel.get("name") != "":
                text_lines.append(jewel.get("name", ""))
            text_lines.append(jewel.get("typeLine", ""))
            
            # Item level
            text_lines.append(f"Item Level: {jewel.get('ilvl', '')}")
            
            # Implicits count
            implicit_count = 0
            if "implicitMods" in jewel and isinstance(jewel["implicitMods"], list):
                implicit_count += len(jewel["implicitMods"])
                
            if implicit_count > 0:
                text_lines.append(f"Implicits: {implicit_count}")
            else:
                text_lines.append("Implicits: 0")
            
            # Implicit mods
            if "implicitMods" in jewel and isinstance(jewel["implicitMods"], list):
                for mod in jewel["implicitMods"]:
                    text_lines.append(mod)
            
            # Explicit mods
            if "explicitMods" in jewel and isinstance(jewel["explicitMods"], list):
                for mod in jewel["explicitMods"]:
                    text_lines.append(mod)
                    
            # Radius
            if "properties" in jewel and isinstance(jewel["properties"], list):
                for prop in jewel["properties"]:
                    if prop.get("name") == "Radius" and len(prop.get("values", [])) > 0:
                        radius_value = prop["values"][0][0]
                        text_lines.append(f"Radius: {radius_value}")
                        break
            
            # Corrupted status
            if jewel.get("corrupted", False):
                text_lines.append("Corrupted")
            
            # Set the completed text to the item element
            item_elem.text = "\n".join(text_lines)
            log(f"Agregado Jewel: {jewel.get('id', '')}")
            items.append(item_elem)
    else:
        log("No se encontraron jewels en character.")
    
    # Add ItemSet
    itemset = ET.SubElement(items, "ItemSet")
    itemset.set("useSecondWeaponSet", "false")
    itemset.set("id", "1")
    
    # Mapeo entre inventoryId del JSON y los slot names del XML
    inventory_to_slot_map = {
        "Belt": "Belt",
        "BodyArmour": "Body Armour",
        "Weapon": "Weapon 1",
        "Helm": "Helmet",
        "Gloves": "Gloves",
        "Offhand": "Weapon 2",
        "Ring2": "Ring 2",
        "Ring": "Ring 1",
        "Boots": "Boots",
        "Amulet": "Amulet",
        "Weapon2": "Weapon 1 Swap",
        "Offhand2": "Weapon 2 Swap",
        # Flask ahora lo manejaremos de forma especial
    }
    
    # Crear listas para ordenar los flask y charms según su tipo
    life_flasks = []
    mana_flasks = []
    charm_items = []
    other_flasks = []  # Para otros tipos de flask
    
    # Contadores para asignación de slots
    flask_count = 1
    charm_count = 1
    
    # Add default slots
    slot_names = [
        "Gloves", "Weapon 1", "Flask 1", "Amulet", "Charm 3", "Charm 1", "Flask 2", 
        "Weapon 2", "Belt", "Weapon 1 Swap", "Ring 2", "Body Armour", "Weapon 2 Swap", 
        "Ring 1", "Charm 2", "Helmet", "Boots", "Flask 3", "Flask 4", "Flask 5"
    ]
    
    # Crear todos los slots con itemId=0 por defecto
    slots_dict = {}
    for slot_name in slot_names:
        slot = ET.SubElement(itemset, "Slot")
        slot.set("itemPbURL", "")
        slot.set("name", slot_name)
        slot.set("itemId", "0")  # Valor por defecto para slots vacíos
        slots_dict[slot_name] = slot
    
    # Clasificar los flask y charms por tipo
    for item_id, inventory_id in item_inventory_map.items():
        if inventory_id == "Flask" and item_id in item_basetype_map:
            # Obtener baseType y convertirlo a minúscula para la comparación
            base_type = item_basetype_map[item_id].lower()
            
            if "life" in base_type:
                life_flasks.append(item_id)
            elif "mana" in base_type:
                mana_flasks.append(item_id)
            elif "charm" in base_type:
                charm_items.append(item_id)
            else:
                other_flasks.append(item_id)
    
    # Asignar flasks y charms a sus slots específicos
    # Primero los life flasks
    for item_id in life_flasks:
        if flask_count <= 5:  # Solo tenemos 5 slots para flasks
            slots_dict[f"Flask {flask_count}"].set("itemId", str(item_id))
            flask_count += 1
    
    # Luego los mana flasks
    for item_id in mana_flasks:
        if flask_count <= 5:  # Solo tenemos 5 slots para flasks
            slots_dict[f"Flask {flask_count}"].set("itemId", str(item_id))
            flask_count += 1
    
    # Luego otros flasks si los hay
    for item_id in other_flasks:
        if flask_count <= 5:  # Solo tenemos 5 slots para flasks
            slots_dict[f"Flask {flask_count}"].set("itemId", str(item_id))
            flask_count += 1
    
    # Finalmente los charms
    for item_id in charm_items:
        if charm_count <= 3:  # Tenemos 3 slots para charms
            slots_dict[f"Charm {charm_count}"].set("itemId", str(item_id))
            charm_count += 1
    
    # Asignar el resto de los items a sus slots correspondientes
    for item_id, inventory_id in item_inventory_map.items():
        # Saltar los que ya procesamos (Flask y Charm)
        if inventory_id == "Flask":
            continue
            
        if inventory_id in inventory_to_slot_map:
            slot_name = inventory_to_slot_map[inventory_id]
            if slot_name in slots_dict:
                slots_dict[slot_name].set("itemId", str(item_id))
    
    # Asignar jewels a sus slots
    for i, jewel_id in enumerate(jewel_ids):
        jewel_slot_name = f"Jewel {i+1}"
        
        # Crear slot para jewel si no existe
        if jewel_slot_name not in slots_dict:
            slot = ET.SubElement(itemset, "Slot")
            slot.set("itemPbURL", "")
            slot.set("name", jewel_slot_name)
            slot.set("itemId", str(jewel_id))
            slots_dict[jewel_slot_name] = slot
        else:
            slots_dict[jewel_slot_name].set("itemId", str(jewel_id))
    
    return items

def create_notes(char):
    log("Creando Notas...")
    notes = ET.Element("Notes")
    notes_text = "^_xD02090--  REMEMBER (Build auto-imported):  --^_7\n"
    notes_text = notes_text+"The maxroll api does not return the position of the gems and puts them randomly, so to avoid the build being different, since there are gems with areas, they must be incorporated manually in the sockets.\n"
    notes_text = notes_text+"You also need to manually add the configuration of the rewards for the secondary missions.\n"
    notes.text = notes_text
    
    return notes

# --- Función para construir el XML completo desde el JSON de entrada ---
def build_xml_from_character(data):
    log("Construyendo XML desde JSON...")
    root = ET.Element("PathOfBuilding2")
    if "character" in data:
        char = data["character"]
        root.append(create_build_from_character(char))
        # Para el árbol de pasivas, usamos el campo "passives" del character si existe.
        if "passives" in char and isinstance(char["passives"], dict):
            root.append(create_tree_from_passives(char["passives"], char))
        else:
            log("No se encontró 'passives' en character, usando Tree por defecto.")
            root.append(create_tree_from_passives({}, char))
        root.append(create_skills_from_character(char))
        root.append(create_items_from_character(char))
        root.append(create_notes(char))
    else:
        log("El JSON no contiene la propiedad 'character'.")
    return root

def encode_to_pob(xml_bytes):
    log("Comprimiendo y codificando XML para generar código PoB...")
    compressed = zlib.compress(xml_bytes)
    b64encoded = base64.b64encode(compressed).decode('utf-8')
    # Convertir a variante URL-safe (quitando padding)
    pob_code = b64encoded.replace('+', '-').replace('/', '_').rstrip("=")
    return pob_code  # Sin prefijo

def main():
    if len(sys.argv) < 2:
        print("Uso: python code.py <archivo_character.json>")
        sys.exit(1)
    
    json_filename = sys.argv[1]
    log(f"Leyendo archivo JSON: {json_filename}")
    try:
        with open(json_filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("Error al leer el archivo JSON:", e)
        sys.exit(1)
    
    log("JSON cargado correctamente.")
    root = build_xml_from_character(data)
    
    # (Opcional) Indentar el XML para mejor lectura (requiere Python 3.9+)
    try:
        ET.indent(root, space="    ")
    except Exception as e:
        log("Indentación no soportada, se omite.")
    
    xml_bytes = ET.tostring(root, encoding="utf-8", method="xml")
    
    print("XML generado:")
    print(xml_bytes.decode('utf-8'))
    
    pob_code = encode_to_pob(xml_bytes)
    print("\nCódigo PoB generado:")
    print(pob_code)

if __name__ == "__main__":
    main()
