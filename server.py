import json
import sys
import os
from functools import lru_cache
from jmcc_extension import *

TRIGGERS = {'.', '=', '(', '"', ',', "'", '<', '@', '[', '%'}

def send_message(message: dict) -> None:
    content = json.dumps(message).encode('utf-8')
    sys.stdout.buffer.write(b"Content-Length: %d\r\n\r\n%s" % (len(content), content))
    sys.stdout.buffer.flush()
    
def read_message():
    while ((line := sys.stdin.buffer.readline()) != b'\r\n' and line):
        if line.startswith(b"Content-Length:"): content_length = line.split(b":")[1]
    body = sys.stdin.buffer.read(int(content_length))
    return json.loads(body)

@lru_cache(maxsize=32)
def get_cached_context(func_token, p_id, p_type, p_val, depth, is_array):
    TEXT_ARG_MAP = {('@item', 'id'): items_completions,('item', 'id'): items_completions, ('sound', 'sound'): sound_completions,('particle', 'particle'): particle_completions, ('particle', 'material'): block_completions,('potion', 'potion'): potion_completions}
    items = []
    match p_type:
        case 'enum':
            items = [{'label': x, 'kind': 13, 'insertText': f'"{x}"'} for x in (p_val or [])]
        case 'map' if p_id == "enchantments":
            fmt, f_fmt = ('{{"{0}": 1}}', '{{"\\"{0}"}}') if depth == 0 else ('"{0}": 1', None)
            for y in enchant_completions:
                item = {'label': y, 'kind': 13, 'insertText': fmt.format(y)}
                if f_fmt: item['filterText'] = f_fmt.format(y)
                items.append(item)
        case 'text':
            if p_id == 'enchantment':
                items = [{'label': y, 'kind': 13, 'insertText': f'"{y}', 'filterText': f'{y}'} for y in enchant_completions]
            else:
                items = TEXT_ARG_MAP.get((func_token, p_id), [])
        case 'block': items = block_completions
        case _: items = value_type_cache.get(p_type, [])
    if is_array and depth == 0 and items:
        return [{**i, 'insertText': f"[{i.get('insertText', i['label'])}$0]", "insertTextFormat": 2} for i in items]
    return items


def load_assets(lang: str = 'ru_RU') -> None:
    global ASSETS, WITH_CONDITIONAL_COMPLETIONS, STATIC_CODE_COMPLETIONS, ORIGIN_COMPLETIONS, SELECTOR_COMPLETIONS, DECORATOR_COMPLETIONS
    global block_completions, enchant_completions, items_completions, particle_completions, potion_completions, items_completions, sound_completions, minimessage_completions, placeholder_completions
    global STATIC_CODE_SIGNATURES
    global origin_linked, with_conditional_cache, value_type_cache
    origin_linked, with_conditional_cache = {}, set()
    STATIC_CODE_SIGNATURES = {}
    ASSETS, STATIC_CODE_COMPLETIONS, WITH_CONDITIONAL_COMPLETIONS, ORIGIN_COMPLETIONS = [], [], [], []
    base_path = os.path.dirname(__file__)
    read = lambda *path: json.load(open(os.path.join(base_path, *path), encoding='utf-8'))
    base_types = ['item', 'location', 'vector', 'potion', 'sound','text', 'particle', 'number', 'block', 'variable', 'array', 'map', 'any', 'none']
    rich_types = ['item', 'location', 'vector', 'potion', 'sound', 'particle']
    math_funcs = ['abs', 'sqrt','cbrt','ceil','floor','sin','cos','round','pow','min','max']
    player_selectors = ['current','default','default_player','killer_player','damager_player','shooter_player','victim_player','random_player','all_players']
    value_selectors = ['current','default','default_entity','killer_entity','damager_entity','victim_entity','shooter_entity','projectile','last_entity']
    entity_selectors = ['current', 'default_entity','killer_entity','shooter_entity','projectile','victim_entity','random_entity','all_mobs','all_entities','last_entity']
    placeholders = ["%player%", "%player_uuid%", "%entity%", "%entity_uuid%", "%victim%", "%victim_uuid%", "%damager%", "%damager_uuid%", "%shooter%", "%shooter_uuid%", "%killer%", "%killer_uuid%", "%selected%", "%selected_uuid%", "%display_name%", "%uuid%", "%space%", "%empty%", "%var%", "%var_local%", "%var_save%", "%var_line%", "%length%", "%length_local%", "%length_save%", "%length_line%", "%index%", "%index_local%", "%index_save%", "%index_line%", "%entry%", "%entry_local%", "%entry_save%", "%entry_line%", "%var%", "%math%", "%player_amount%", "%entity_count%", "%entity_amount%", "%global_online%", "%online%", "%time%", "%worlds%", "%damage%", "%random%", "%random_uuid%"]
    decorators = ['@item', '@description', '@args', '@return_var', '@hidden','@getter','@setter','@overload']
    magic_methods = ['__add__', '__subtract__', '__multiply__', '__divide__', '__remainder__', '__pow__', '__equals__', '__not_equals__', '__greater__', '__less__', '__greater_or_equals__', '__less_or_equals__', '__contains__', '__iadd__', '__isubtract__', '__imultiply__', '__idivide__', '__iremainder__', '__ipow__', '__dict__', '__custom__', '__slots__', '__get_attribute__', '__set_attribute__', '__subscript__', '__slice__', '__init__']
    opened_minimessage_tags = ['black', 'dark_blue', 'dark_green', 'dark_aqua', 'dark_red', 'dark_purple', 'gold', 'gray', 'dark_gray', 'blue', 'green', 'aqua', 'red', 'light_purple', 'yellow', 'white', 'bold', 'b', 'italic', 'i', 'em', 'underlined', 'u', 'strikethrough', 'st', 'obfuscated', 'obf', 'reset', 'r', 'pre', 'click:open_url', 'click:run_command', 'click:suggest_command', 'click:copy_to_clipboard', 'click:change_page', 'hover:show_text', 'hover:show_item', 'hover:show_entity', 'key:key.jump', 'key:key.sneak', 'key:key.sprint', 'key:key.left', 'key:key.right', 'key:key.back', 'key:key.forward', 'key:key.attack', 'key:key.pickItem', 'key:key.use', 'key:key.drop', 'key:key.swapOffhand', 'key:key.inventory', 'key:key.loadToolbarActivator', 'key:key.saveToolbarActivator', 'key:key.playerlist', 'key:key.chat', 'key:key.command', 'key:key.socialInteractions', 'key:key.advancements', 'key:key.screenshot', 'key:key.fullscreen', 'key:key.spectatorOutlines', 'key:key.togglePerspective', 'key:key.smoothCamera', 'key:key.cinematicCamera', 'key:key.hotbar.1', 'key:key.hotbar.2', 'key:key.hotbar.3', 'key:key.hotbar.4', 'key:key.hotbar.5', 'key:key.hotbar.6', 'key:key.hotbar.7', 'key:key.hotbar.8', 'key:key.hotbar.9', 'pride:trans', 'pride:bi', 'pride:lesbian', 'pride:gay', 'pride:pan', 'pride:ace', 'pride:nonbinary', 'pride:genderqueer', 'font:minecraft:default', 'font:minecraft:uniform', 'font:minecraft:alt', 'selector:@p', 'selector:@a', 'selector:@r', 'selector:@s', 'selector:@e', 'gradient:', 'rainbow:', 'transition:', 'font:', 'lang:', 'translate:', 'trans:', 'tr:', 'insert:', 'color:', 'colour:', 'c:', 'shadow:', 'score:', 'nbt:', 'sprite:', 'head:', 'newline', 'br']
    closed_minimessage_tags = ['/black', '/dark_blue', '/dark_green', '/dark_aqua', '/dark_red', '/dark_purple', '/gold', '/gray', '/dark_gray', '/blue', '/green', '/aqua', '/red', '/light_purple', '/yellow', '/white', '/bold', '/b', '/italic', '/i', '/em', '/underlined', '/u', '/strikethrough', '/st', '/obfuscated', '/obf', '/pre', '/click', '/hover', '/insert', '/gradient', '/rainbow', '/transition', '/pride', '/font', '/shadow', '/color', '/colour', '/c']
    value_type_cache = {t: [] for t in base_types}
    for rt in rich_types: value_type_cache[rt].append({'label': rt, 'kind': 3})
    SELECTOR_COMPLETIONS = {k: [{'label': s, 'kind': 13, 'insertText': f"{s}>"} for s in v] for k, v in {'player': player_selectors, 'value': value_selectors, 'entity': entity_selectors}.items()}
    ASSETS = read('assets', f'completions_{lang}.json')
    enchant_completions = read('data', 'enchants.json')
    particle_completions = [{'label': p, 'kind': 13, 'insertText': f'"{p}"'} for p in read('data', 'particles.json')]
    potion_completions = [{'label': p, 'kind': 13, 'insertText': f'"{p}"'} for p in read('data', 'potions.json')]
    items_completions = [{'label': i, 'kind': 13, 'insertText': f'"{i}"'} for i in read('data', 'items.json')]
    sound_completions = [{'label': s, 'kind': 13, 'insertText': f'"{s}"'} for s in read('data', 'sounds.json')]
    block_completions = [{'label': b, 'kind': 13, 'insertText': f'"{b}"'} for b in read('data', 'blocks.json')]
    placeholder_completions = [{'label': b, 'kind': 13} for b in placeholders]
    minimessage_completions = [{'label': b, 'kind': 13, 'insertText': f'{b}'} for b in opened_minimessage_tags]
    minimessage_completions.extend([{'label': b, 'kind': 13, 'insertText': f'{b}', 'sortText': 'z'} for b in closed_minimessage_tags])
    DECORATOR_COMPLETIONS = [{'label': d, 'kind': 13} for d in decorators]
    STATIC_CODE_COMPLETIONS.extend({'label': m, 'kind': 3} for m in magic_methods)
    STATIC_CODE_COMPLETIONS.extend({'label': t, 'kind': 3} for t in rich_types)
    STATIC_CODE_COMPLETIONS.extend({'label': t, 'kind': 3} for t in math_funcs)
    for x in read('data', 'events.json'):
        name = f"event<{x['id']}>"
        detail = ASSETS.get(name, {}).get('detail')
        STATIC_CODE_COMPLETIONS.append({'label': name, 'kind': 3, 'detail': detail})
    for x in read('data', 'values.json'):
        name = f"value::{x['id']}"
        detail = ASSETS.get(name, {}).get('detail')
        comp = {'label': name, 'kind': 3, 'detail': detail}
        STATIC_CODE_COMPLETIONS.append(comp)
        value_type_cache.setdefault(x['type'], []).append(comp)
    for x in read('data', 'actions.json'):
        name = f"{x['object']}::{x['name']}"
        asset = ASSETS.get(name)
        if asset:
            comp = {'label': name, 'kind': 3, 'detail': asset.get('detail')}
            STATIC_CODE_COMPLETIONS.append(comp)
            if 'boolean' in x: WITH_CONDITIONAL_COMPLETIONS.append(comp)
            if 'origin' in x:
                ORIGIN_COMPLETIONS.append({'label': x['name'], 'kind': 3, 'detail': asset.get('detail')})
                origin_linked[x['name']] = [name, x['origin']]
            if x['type'].endswith('conditional'): with_conditional_cache.add(name)
            valid_args = [arg for arg in x.get('args', []) if 'id' in arg]
            valid_assigns = [arg['id'] for arg in x.get('assign', [])]
            STATIC_CODE_SIGNATURES[name] = {
                'id': [arg['id'] for arg in valid_args],
                'type': [arg.get('type') for arg in valid_args],
                'value': [arg.get('values') for arg in valid_args],
                'array': [arg.get('array') for arg in valid_args],
                'assign': valid_assigns
            }
    STATIC_CODE_SIGNATURES.update( { 'location': {'id': ['x', 'y', 'z', 'yaw', 'pitch'], 'type': ['number'] * 5, 'value': [None] * 5},'item': {'id': ['id', 'name', 'count', 'lore', 'nbt', 'custom_tags'], 'type': ['text', 'text', 'number', 'text', 'components', 'map'], 'value': [None] * 6},'sound': {'id': ['sound', 'volume', 'pitch', 'variation', 'source'], 'type': ['text', 'number', 'number', 'text', 'enum'], 'value': [None, None, None, None, ['RECORD', 'BLOCK', 'MASTER', 'VOICE', 'WEATHER', 'AMBIENT', 'NEUTRAL', 'HOSTILE', 'PLAYER', 'MUSIC']]},'vector': {'id': ['x', 'y', 'z'], 'type': ['number'] * 3, 'value': [None] * 3},'particle': {'id': ['particle', 'count', 'spread_x', 'spread_y', 'motion_x', 'motion_y', 'motion_z', 'material', 'color', 'size', 'to_color'], 'type': ['text', 'number', 'number', 'number', 'number', 'number', 'number', 'text', 'number', 'number', 'number'], 'value': [None] * 11},'potion': {'id': ['potion', 'amplifier', 'duration'], 'type': ['text', 'number', 'number'], 'value': [None] * 3}})
    STATIC_CODE_SIGNATURES.update( { 'abs': {'id': ['number'], 'type': ['number'], 'value': [None]}, 'sqrt': {'id': ['number'], 'type': ['number'], 'value': [None]},'cbrt': {'id': ['number'], 'type': ['number'], 'value': [None]},'ceil': {'id': ['number'], 'type': ['number'], 'value': [None]},'floor': {'id': ['number'], 'type': ['number'], 'value': [None]},'sin': {'id': ['number'], 'type': ['number'], 'value': [None]},'cos': {'id': ['number'], 'type': ['number'], 'value': [None]},'round': {'id': ['number','precision'], 'type': ['number']*2, 'value': [None]*2},'pow': {'id': ['number', 'pow'], 'type': ['number']*2, 'value': [None]*2},'min': {'id': ['number1','number2'], 'type': ['number']*2, 'value': [None]*2},'max': {'id': ['number1','number2'], 'type': ['number']*2, 'value': [None]*2} } )
    STATIC_CODE_SIGNATURES.update( { '@item': {'id': ['id'], 'type': ['text'], 'value': [None]} ,'@args': {'id': ['*position'], 'type': ['text'], 'value': [None]}, '@description': {'id': ['*description'], 'type': ['text'], 'value': [None]},'@return_var': {'id': ['variable'], 'type': ['variable'], 'value': [None]} } )
    # jmcc compiler directives
    jmcc_directives = ['jmcc::error', 'jmcc::run_function']
    for name in jmcc_directives:
        asset = ASSETS.get(name, {})
        STATIC_CODE_COMPLETIONS.append({'label': name, 'kind': 3, 'detail': asset.get('detail')})
    STATIC_CODE_SIGNATURES['jmcc::error'] = {
        'id': ['message'],
        'type': ['text'],
        'value': [None],
        'array': [False],
        'assign': []
    }
    STATIC_CODE_SIGNATURES['jmcc::run_function'] = {
        'id': ['file', 'function', 'args'],
        'type': ['text', 'text', 'array'],
        'value': [None, None, None],
        'array': [False, False, True],
        'assign': []
    }

def handle_initialize(message: dict) -> dict:
    params = message["params"]
    init_opts = params["initializationOptions"]
    lang = init_opts.get("properties", {}).get("lang", "en_US")
    load_assets(lang)
    HIDE_HOVER          = bool(init_opts.get("hideHover", False))
    HIDE_COMPLETION     = bool(init_opts.get("hideCompletion", False))
    HIDE_SIGNATURE_HELP = bool(init_opts.get("hideSignatureHelp", False))
    capabilities: dict = {"textDocumentSync": 1, "hoverProvider": not HIDE_HOVER}
    if not HIDE_COMPLETION: capabilities["completionProvider"] = {"triggerCharacters": [".", "(", "[", "'", "<", '"', "@", ",","=", "%"]}
    if not HIDE_SIGNATURE_HELP: capabilities["signatureHelpProvider"] = {"triggerCharacters": ["(",",", "="], "retriggerCharacters": [")"]}
    return { "jsonrpc": "2.0", "id": message["id"],"result":{"capabilities": capabilities} }

def handle_didOpen(message: dict) -> None:
    textDocument: dict = message["params"]["textDocument"]
    text: str = textDocument["text"]
    uri: str = textDocument["uri"]
    tokenize(text, uri)

def handle_didClose(message: dict) -> None:
    uri = message["params"]["textDocument"]["uri"]
    clear(uri)

def handle_didChange(message: dict) -> None:
    params: dict = message["params"]
    uri: str = params["textDocument"]["uri"]
    text: str = params["contentChanges"][0]["text"]
    tokenize(text, uri)

def handle_hover(message):
    uri, pos = message["params"]["textDocument"]["uri"], message["params"]["position"]
    txt = global_text[uri]
    pos = line_and_offset_to_pos(txt, pos["line"], pos["character"]) + 1
    if (idx := pos_to_idx(uri,pos)) != -1: token = global_tokens[uri][idx]
    else: token = None
    if not token: return {"jsonrpc": "2.0", "id": message["id"], "result": None}
    key, left_token_index, right_token_index = try_find_object(uri, pos)
    (line1, char1), (line2, char2) = pos_to_line_and_offset(global_text[uri],global_tokens[uri][left_token_index].starting_pos, global_tokens[uri][right_token_index].ending_pos+1)
    if key.startswith('.'): key, id = origin_linked.get(token.value, (key, None))
    # если ключ не найден в ассетах — пробуем с префиксом jmcc::
    if key not in ASSETS and f"jmcc::{key}" in ASSETS:
        key = f"jmcc::{key}"
    contents = [f"```justcode\n{key}\n```"]
    if desc := ASSETS.get(key, {}).get('desc', None): contents.append(desc)
    return {"jsonrpc": "2.0", "id": message["id"], "result": {"contents": contents, "range": {"start": {"line": line1, "character": char1},"end": {"line": line2, "character": char2}}}}


def handle_signatureHelp(message):
    uri, pos_params = message["params"]["textDocument"]["uri"], message["params"]["position"]
    func_token, commas, active_key, used_keys, depth, assign_cnt = get_call_context(uri, line_and_offset_to_pos(global_text[uri], pos_params["line"], pos_params["character"]))
    params, active_idx = get_signature_context(func_token, commas, active_key, used_keys, origin_linked,STATIC_CODE_SIGNATURES, assign_count=assign_cnt)
    if not params: return {"jsonrpc": "2.0", "id": message['id'], "result": None}
    label = ", ".join(f"{k}: {v}" for k, v, _ in params)
    return {"jsonrpc": "2.0", "id": message['id'], "result": {"signatures": [{"label": label, "parameters": [{"label": f"{k}: {v}"} for k, v, _ in params]}],"activeSignature": 0,  "activeParameter": active_idx}}

def handle_completion(message):
    uri, line, char = message["params"]["textDocument"]["uri"], message["params"]["position"]["line"], message["params"]["position"]["character"]
    trigger = message["params"]['context'].get('triggerCharacter')
    pos = line_and_offset_to_pos(global_text[uri], line, char)
    curr, prev = get_token(uri, pos), get_token(uri, pos, -1)
    if not trigger and ((curr.value in TRIGGERS and (trigger := curr.value)) or (prev.value in TRIGGERS and (trigger := prev.value))): pass
    if curr.type == 4: trigger = '<'
    rng_toks = None
    if trigger == '@' and (idx := pos_to_idx(uri, pos)) is not None:
        rng_toks = (global_tokens[uri][idx].starting_pos, global_tokens[uri][idx].ending_pos, -1)
    elif global_tokens[uri]:
        _, l, r = try_find_object(uri, pos)
        if l is not None and r is not None:
            rng_toks = (global_tokens[uri][l].starting_pos, global_tokens[uri][r].ending_pos, 0)
    result = {}
    if rng_toks:
        (l1, c1), (l2, c2) = pos_to_line_and_offset(global_text[uri], rng_toks[0], rng_toks[1])
        result = {'itemDefaults': {'editRange': {'start': {'line': l1, 'character': max(0, c1 + rng_toks[2])}, 'end': {'line': l2, 'character': c2}}}}
    func_token, commas, active_key, used_keys, depth, ac = get_call_context(uri, pos)
    params, idx = get_signature_context(func_token, commas, active_key, used_keys, origin_linked, STATIC_CODE_SIGNATURES, assign_count=ac)
    context_items = []
    real_tok = origin_linked.get(func_token, [func_token])[0]
    key_context_items = []
    if params and 0 <= idx < len(params):
        p_id, p_type, p_val = params[idx]
        sig_arr = STATIC_CODE_SIGNATURES.get(real_tok, {}).get('array', [])
        is_arr = idx < len(sig_arr) and sig_arr[idx]
        cached_items = get_cached_context(func_token, p_id, p_type, tuple(p_val) if isinstance(p_val, list) else p_val, depth, is_arr)
        context_items = list(cached_items) if cached_items else []
    if params and func_token and active_key is None and trigger != '=':
        for param in params:
            p_name = param[0]
            p_type = param[1]
            if p_name and p_name not in used_keys:
                key_context_items.append({
                    'label': p_name,
                    'kind': 5,
                    'insertText': f"{p_name} = ",
                    'detail': f'{p_type}',
                    'sortText': f'0_{p_name}'
                })
    items = []
    match trigger:
        case '.':
            reprev = get_token(uri, pos, -2)
            if (prev and prev.type == 11) or (reprev and reprev.type == 11):
                result, items = {}, ORIGIN_COMPLETIONS
        case '=' | ',': 
            result = {}
            items = context_items if func_token else STATIC_CODE_COMPLETIONS
            if trigger == ',' and func_token: items.extend(key_context_items)
        case '"' | "'": 
            (l1, c1), (l2, c2) = pos_to_line_and_offset(global_text[uri],curr.starting_pos,curr.ending_pos)
            result = {'itemDefaults': {'editRange': {'start': {'line': l1, 'character': c1+1}, 'end': {'line': l2, 'character': c2}}}}
            items = context_items if func_token else []
        case '(':
            result = {}
            items = WITH_CONDITIONAL_COMPLETIONS if (real_tok in with_conditional_cache or prev.type == 33) else context_items
            if func_token:
                items.extend(key_context_items)
        case '<':
            if prev and (who := try_find_object(uri, pos-1)[0].split("::")[0]) in {'player','entity','value'}:
                result, items = {}, SELECTOR_COMPLETIONS[who]
            elif curr.type == 30:  result, items = {}, minimessage_completions
            else: items = STATIC_CODE_COMPLETIONS if prev and prev.type == 43 else []
        case '@': items = DECORATOR_COMPLETIONS
        case '%':
            val = curr.value
            percent_index = val.rfind('%')
            if percent_index != -1:
                percent_start_abs = curr.starting_pos + percent_index
                percent_end_abs = percent_start_abs + 1 
                (l1, c1), (l2, c2) = pos_to_line_and_offset(global_text[uri], percent_start_abs, percent_end_abs)
                result = {
                    'itemDefaults': {
                        'editRange': {
                            'start': {'line': l2, 'character': c2},
                            'end': {'line': l2, 'character': c2}
                        }
                    }
                }
                if curr.type in {3, 28, 29, 30}: 
                    items = placeholder_completions  
                else: 
                    items = []
            else:
                items = []
        case _: items = context_items or STATIC_CODE_COMPLETIONS
    return {"jsonrpc": "2.0", "id": message["id"], "result": {**result, 'items': items}}

def main():
    while (message := read_message()) is not None:
        method: str = message["method"]
        match method:
            case "initialize": send_message(handle_initialize(message))
            case "textDocument/hover": send_message(handle_hover(message))
            case "textDocument/completion": send_message(handle_completion(message))
            case "textDocument/signatureHelp": send_message(handle_signatureHelp(message))
            case "textDocument/didOpen": handle_didOpen(message)
            case "textDocument/didClose": handle_didClose(message)
            case "textDocument/didChange": handle_didChange(message)
            case "shutdown": send_message({"jsonrpc": "2.0", "id": message["id"], "result": None})
    return 0

sys.exit(main())