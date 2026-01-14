import os
import re
import sys
import subprocess
import platform

TXT_PATH = 'singers.txt'

# --- 歌手文件处理 (保持不变) ---
def parse_singers_txt():
    if not os.path.exists(TXT_PATH): return []
    singers = []
    try:
        with open(TXT_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            match = re.match(r'^([^,]+),([^,]+),\(([^)]+)\),(.*),([0-9A-Fa-f]+)$', line)
            if not match: continue
            name, eng_name, langs_str, voice_data_str, color = match.groups()
            langs = langs_str.split(',')
            voice_blocks = re.findall(r'\{([^}]+)\}', voice_data_str)
            voicebanks = {}
            for block in voice_blocks:
                if ':' not in block: continue
                lang_code, vb_str = block.split(':', 1)
                vbs = []
                for raw_vb in re.findall(r'\[(.*?)\]', vb_str):
                    parts = raw_vb.split('|')
                    if len(parts) == 3: vbs.append({'engine': parts[0], 'version': parts[1], 'name': parts[2]})
                voicebanks[lang_code] = vbs
            singers.append({'id': idx, 'name': name, 'eng_name': eng_name, 'langs': langs, 'voicebanks': voicebanks, 'color': color})
    except Exception as e: print(f"Parse Error: {e}")
    return singers

def save_all_singers(singers_list):
    lines = []
    for data in singers_list:
        langs_str = f"({','.join(data['langs'])})"
        vb_blocks = []
        for lang in data['langs']:
            if lang in data['voicebanks']:
                vb_items = [f"[{item['engine']}|{item['version']}|{item['name']}]" for item in data['voicebanks'][lang]]
                vb_blocks.append(f"{{{lang}:{','.join(vb_items)}}}")
        voice_data_str = ",".join(vb_blocks)
        line = f"{data['name']},{data['eng_name']},{langs_str},{voice_data_str},{data['color']}"
        lines.append(line)
    
    with open(TXT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

# --- 适配多系统的“打开文件夹” ---
def open_local_folder(path):
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"路径不存在: {path}")

    system_name = platform.system()

    try:
        if system_name == 'Windows':
            os.startfile(path)
        elif system_name == 'Darwin':  # macOS
            subprocess.call(['open', path])
        else:  # Linux / Ubuntu / HarmonyOS (Based on Linux kernel)
            subprocess.call(['xdg-open', path])
    except Exception as e:
        print(f"打开文件夹失败: {e}")
        raise e