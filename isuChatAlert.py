import ac
import acsys
import os
import configparser
import re
import winsound

app_dir = os.path.dirname(os.path.abspath(__file__))
settings_file = os.path.join(app_dir, "settings", "settings.ini")
sound_file = os.path.join(app_dir, "alert.wav")

# --- MAIN APP GLOBALS ---
appWindow = 0
bg_box = 0           
accent_line = 0      
chat_label = 0       
author_bold_1 = 0    
author_bold_2 = 0

display_timer = 0.0
current_max_time = 5.0 
is_alert_active = False
is_test_mode = False 
KEYWORDS = []
FADE_TIME = 0.5 
player_name = ""

# --- CONFIG APP GLOBALS ---
cfgWindow = 0
lbl_text_size = 0
lbl_color = 0
lbl_sound = 0
lbl_scale = 0
lbl_opacity = 0
lbl_time = 0
lbl_mention = 0
txt_keywords = 0
btn_save = 0
btn_test = 0 
save_feedback_timer = 0.0

# --- DEFAULT SETTINGS ---
SET_TEXT_SIZE = 32
SET_SCALE = 1.0
SET_SOUND = True
SET_MENTION_ME = True
SET_OPACITY = 0.85
SET_BASE_TIME = 3.0

COLORS = [
    ("Orange", 1.0, 0.55, 0.0),
    ("Red", 1.0, 0.1, 0.1),
    ("Blue", 0.1, 0.4, 1.0),
    ("Green", 0.1, 1.0, 0.1),
    ("Purple", 0.6, 0.1, 1.0),
    ("White", 1.0, 1.0, 1.0)
]
current_color_idx = 0

def save_settings(*args):
    global KEYWORDS, SET_TEXT_SIZE, SET_SCALE, SET_SOUND, SET_MENTION_ME, current_color_idx, COLORS
    global SET_OPACITY, SET_BASE_TIME, txt_keywords, btn_save, save_feedback_timer
    
    try:
        raw_keys = ac.getText(txt_keywords)
        KEYWORDS = [k.strip().lower() for k in raw_keys.split(",") if k.strip()]
            
        if not os.path.exists(os.path.dirname(settings_file)):
            os.makedirs(os.path.dirname(settings_file))
            
        parser = configparser.ConfigParser()
        parser.add_section("SETTINGS")
        parser.set("SETTINGS", "keywords", ",".join(KEYWORDS))
        parser.set("SETTINGS", "text_size", str(SET_TEXT_SIZE))
        parser.set("SETTINGS", "scale", str(SET_SCALE))
        parser.set("SETTINGS", "sound_on", "1" if SET_SOUND else "0")
        parser.set("SETTINGS", "mention_me", "1" if SET_MENTION_ME else "0")
        parser.set("SETTINGS", "color_idx", str(current_color_idx))
        parser.set("SETTINGS", "opacity", str(SET_OPACITY))
        parser.set("SETTINGS", "base_time", str(SET_BASE_TIME))
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            parser.write(f)
            
        ac.setText(btn_save, "SAVED SUCCESSFULLY!")
        save_feedback_timer = 2.0
    except:
        ac.setText(btn_save, "ERROR SAVING!")
        save_feedback_timer = 2.0

def load_settings():
    global KEYWORDS, SET_TEXT_SIZE, SET_SCALE, SET_SOUND, SET_MENTION_ME, current_color_idx
    global SET_OPACITY, SET_BASE_TIME
    
    if os.path.exists(settings_file):
        try:
            parser = configparser.ConfigParser()
            parser.read(settings_file, encoding='utf-8')
            if parser.has_section("SETTINGS"):
                if parser.has_option("SETTINGS", "keywords"):
                    raw_keys = parser.get("SETTINGS", "keywords")
                    KEYWORDS = [k.strip().lower() for k in raw_keys.split(",") if k.strip()]
                if parser.has_option("SETTINGS", "text_size"):
                    SET_TEXT_SIZE = int(parser.get("SETTINGS", "text_size"))
                if parser.has_option("SETTINGS", "scale"):
                    SET_SCALE = float(parser.get("SETTINGS", "scale"))
                if parser.has_option("SETTINGS", "sound_on"):
                    SET_SOUND = parser.get("SETTINGS", "sound_on") == "1"
                if parser.has_option("SETTINGS", "mention_me"):
                    SET_MENTION_ME = parser.get("SETTINGS", "mention_me") == "1"
                if parser.has_option("SETTINGS", "color_idx"):
                    current_color_idx = int(parser.get("SETTINGS", "color_idx"))
                    if current_color_idx >= len(COLORS): current_color_idx = 0
                if parser.has_option("SETTINGS", "opacity"):
                    SET_OPACITY = float(parser.get("SETTINGS", "opacity"))
                if parser.has_option("SETTINGS", "base_time"):
                    SET_BASE_TIME = float(parser.get("SETTINGS", "base_time"))
        except:
            pass

def update_config_labels():
    global lbl_text_size, lbl_color, lbl_sound, lbl_mention, lbl_scale, lbl_opacity, lbl_time, txt_keywords
    if cfgWindow:
        ac.setText(lbl_text_size, "Text: " + str(SET_TEXT_SIZE))
        ac.setText(lbl_color, "Color: " + COLORS[current_color_idx][0])
        ac.setText(lbl_sound, "Sound: ON" if SET_SOUND else "Sound: OFF")
        ac.setText(lbl_mention, "Mention Alert: ON" if SET_MENTION_ME else "Mention Alert: OFF")
        ac.setText(lbl_scale, "Scale: " + str(int(SET_SCALE * 100)) + "%")
        ac.setText(lbl_opacity, "Opacity: " + str(int(SET_OPACITY * 100)) + "%")
        ac.setText(lbl_time, "Time: " + str(round(SET_BASE_TIME, 1)) + "s")

# --- BUTTON CLICK EVENTS ---
def btn_txt_minus(x, y):
    global SET_TEXT_SIZE
    if SET_TEXT_SIZE > 16: SET_TEXT_SIZE -= 2
    update_config_labels()

def btn_txt_plus(x, y):
    global SET_TEXT_SIZE
    if SET_TEXT_SIZE < 48: SET_TEXT_SIZE += 2
    update_config_labels()

def btn_scale_minus(x, y):
    global SET_SCALE
    if SET_SCALE > 0.5: SET_SCALE -= 0.1
    update_config_labels()

def btn_scale_plus(x, y):
    global SET_SCALE
    if SET_SCALE < 1.5: SET_SCALE += 0.1
    update_config_labels()

def btn_op_minus(x, y):
    global SET_OPACITY
    if SET_OPACITY > 0.2: SET_OPACITY -= 0.05
    update_config_labels()

def btn_op_plus(x, y):
    global SET_OPACITY
    if SET_OPACITY < 1.0: SET_OPACITY += 0.05
    update_config_labels()

def btn_time_minus(x, y):
    global SET_BASE_TIME
    if SET_BASE_TIME > 1.0: SET_BASE_TIME -= 0.5
    update_config_labels()

def btn_time_plus(x, y):
    global SET_BASE_TIME
    if SET_BASE_TIME < 10.0: SET_BASE_TIME += 0.5
    update_config_labels()

def btn_color_toggle(x, y):
    global current_color_idx, COLORS
    current_color_idx = (current_color_idx + 1) % len(COLORS)
    update_config_labels()

def btn_sound_toggle(x, y):
    global SET_SOUND
    SET_SOUND = not SET_SOUND
    update_config_labels()

def btn_mention_toggle(x, y):
    global SET_MENTION_ME
    SET_MENTION_ME = not SET_MENTION_ME
    update_config_labels()

def toggle_test_mode(x, y):
    global is_test_mode, is_alert_active, display_timer, btn_test, FADE_TIME, appWindow
    is_test_mode = not is_test_mode
    if is_test_mode:
        ac.setText(btn_test, "STOP TEST MODE")
        ac.setTitle(appWindow, "IsuChat (Drag Me)") # Taşımak için başlığı görünür yapıyoruz!
        trigger_app_intro()
    else:
        ac.setText(btn_test, "TEST / MOVE MODE")
        ac.setTitle(appWindow, "") # Taşıma bitince tekrar ninja gibi gizliyoruz!
        display_timer = FADE_TIME 

# --- MAIN APP LOGIC ---
def wrap_text(text, max_chars=36):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        while len(word) > max_chars:
            if current_line:
                lines.append(current_line.strip())
                current_line = ""
            lines.append(word[:max_chars])
            word = word[max_chars:]
        if len(current_line) + len(word) <= max_chars:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    return "\n".join(lines)

def wake_up_window(box_height):
    global appWindow, bg_box, accent_line, chat_label, author_bold_1, author_bold_2, SET_SCALE, SET_TEXT_SIZE, COLORS, current_color_idx
    
    w = int(700 * SET_SCALE)
    h = int(box_height * SET_SCALE)
    t_size = int(SET_TEXT_SIZE * SET_SCALE)
    c_r, c_g, c_b = COLORS[current_color_idx][1], COLORS[current_color_idx][2], COLORS[current_color_idx][3]
    
    ac.setBackgroundColor(accent_line, c_r, c_g, c_b)
    
    ac.setSize(appWindow, w, h)
    ac.setSize(bg_box, w, h)
    ac.setPosition(bg_box, 0, 0)
    
    ac.setSize(accent_line, int(6 * SET_SCALE), h) 
    ac.setPosition(accent_line, 0, 0)
    
    ac.setFontSize(chat_label, t_size)
    ac.setFontSize(author_bold_1, t_size)
    ac.setFontSize(author_bold_2, t_size)
    
    pad_x = int(25 * SET_SCALE)
    pad_y = int(22 * SET_SCALE)
    ac.setPosition(chat_label, pad_x, pad_y)
    ac.setPosition(author_bold_1, pad_x + 1, pad_y + 1)
    ac.setPosition(author_bold_2, pad_x, pad_y)

def sleep_mode():
    global appWindow, bg_box, accent_line, chat_label, author_bold_1, author_bold_2, is_test_mode
    if not is_test_mode:
        ac.setTitle(appWindow, "") 
    ac.setSize(appWindow, 1, 1)
    ac.setBackgroundOpacity(bg_box, 0.0)
    ac.setBackgroundOpacity(accent_line, 0.0)
    ac.setPosition(bg_box, 0, -9999)
    ac.setPosition(accent_line, 0, -9999)
    ac.setPosition(chat_label, 0, -9999)
    ac.setPosition(author_bold_1, 0, -9999)
    ac.setPosition(author_bold_2, 0, -9999)

def trigger_app_intro():
    global display_timer, is_alert_active, chat_label, author_bold_1, author_bold_2, appWindow, current_max_time, sound_file, SET_SOUND
    
    safe_author = "IsuChat :"
    message = "App is active! You can drag and pin me anywhere on the screen."
    full_message = "{} {}".format(safe_author, message)
    wrapped_message = wrap_text(full_message, 36)
    
    ac.setText(chat_label, wrapped_message)
    ac.setText(author_bold_1, safe_author)
    ac.setText(author_bold_2, safe_author)
    
    line_count = len(wrapped_message.split("\n"))
    box_height = 80 if line_count == 1 else 50 + (line_count * 35)
    
    wake_up_window(box_height)
    
    current_max_time = 8.0 
    display_timer = current_max_time
    is_alert_active = True
    
    if SET_SOUND and os.path.exists(sound_file):
        try:
            winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass

def on_app_activated(*args):
    if not is_test_mode:
        trigger_app_intro()

def on_chat_message(message, author):
    global display_timer, is_alert_active, chat_label, author_bold_1, author_bold_2, appWindow, current_max_time, sound_file, SET_SOUND, SET_BASE_TIME, player_name, SET_MENTION_ME
    
    if is_test_mode:
        return

    if not player_name:
        try:
            player_name = ac.getDriverName(0)
        except:
            pass

    msg_lower = message.lower()
    matched = False
    
    for word in KEYWORDS:
        pattern = r'(?<!\w)' + re.escape(word) + r'(?!\w)'
        if re.search(pattern, msg_lower, re.UNICODE):
            matched = True
            break
            
    if not matched and SET_MENTION_ME and player_name:
        if player_name.lower() in msg_lower:
            matched = True

    if matched:
        
        safe_author = author[:15] + " :"
        full_message = "{} {}".format(safe_author, message)
        wrapped_message = wrap_text(full_message, 36)
        
        ac.setText(chat_label, wrapped_message)
        ac.setText(author_bold_1, safe_author)
        ac.setText(author_bold_2, safe_author)
        
        line_count = len(wrapped_message.split("\n"))
        box_height = 80 if line_count == 1 else 50 + (line_count * 35)
        
        wake_up_window(box_height)
        
        dynamic_time = SET_BASE_TIME + (len(full_message) * 0.08)
        current_max_time = dynamic_time
        display_timer = current_max_time
        
        is_alert_active = True
        
        if SET_SOUND and os.path.exists(sound_file):
            try:
                winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except:
                pass

def acMain(ac_version):
    global appWindow, cfgWindow, bg_box, accent_line, chat_label, author_bold_1, author_bold_2
    global lbl_text_size, lbl_color, lbl_sound, lbl_mention, lbl_scale, lbl_opacity, lbl_time, txt_keywords, btn_save, btn_test
    
    load_settings()
    
    appWindow = ac.newApp("IsuChatAlert")
    ac.setSize(appWindow, 700, 200) 
    ac.drawBorder(appWindow, 0)
    ac.drawBackground(appWindow, 0)
    ac.setBackgroundOpacity(appWindow, 0.0)
    
    # SENPAI İÇİN YENİ BÜYÜ: Oyun ekranını temiz tutmak için başlangıçta başlığı tamamen siliyoruz!
    ac.setTitle(appWindow, "") 
    ac.setIconPosition(appWindow, -9999, -9999)
    
    bg_box = ac.addLabel(appWindow, "")
    ac.setBackgroundColor(bg_box, 0.1, 0.1, 0.12) 
    ac.setBackgroundOpacity(bg_box, SET_OPACITY) 
    
    accent_line = ac.addLabel(appWindow, "")
    ac.setBackgroundOpacity(accent_line, 1.0)
    
    chat_label = ac.addLabel(appWindow, "")
    author_bold_1 = ac.addLabel(appWindow, "")
    author_bold_2 = ac.addLabel(appWindow, "")
    
    ac.addOnChatMessageListener(appWindow, on_chat_message)
    ac.addOnAppActivatedListener(appWindow, on_app_activated)
    
    # --- 2. APP: ISUCHAT CONFIG ---
    cfgWindow = ac.newApp("IsuChat Config")
    ac.setSize(cfgWindow, 300, 490) 
    
    btn_t_minus = ac.addButton(cfgWindow, "-")
    ac.setPosition(btn_t_minus, 20, 40)
    ac.setSize(btn_t_minus, 40, 30)
    ac.addOnClickedListener(btn_t_minus, btn_txt_minus)
    
    lbl_text_size = ac.addLabel(cfgWindow, "Text: ")
    ac.setPosition(lbl_text_size, 80, 45)
    
    btn_t_plus = ac.addButton(cfgWindow, "+")
    ac.setPosition(btn_t_plus, 160, 40)
    ac.setSize(btn_t_plus, 40, 30)
    ac.addOnClickedListener(btn_t_plus, btn_txt_plus)
    
    btn_s_minus = ac.addButton(cfgWindow, "-")
    ac.setPosition(btn_s_minus, 20, 80)
    ac.setSize(btn_s_minus, 40, 30)
    ac.addOnClickedListener(btn_s_minus, btn_scale_minus)
    
    lbl_scale = ac.addLabel(cfgWindow, "Scale: ")
    ac.setPosition(lbl_scale, 80, 85)
    
    btn_s_plus = ac.addButton(cfgWindow, "+")
    ac.setPosition(btn_s_plus, 160, 80)
    ac.setSize(btn_s_plus, 40, 30)
    ac.addOnClickedListener(btn_s_plus, btn_scale_plus)

    btn_op_minus = ac.addButton(cfgWindow, "-")
    ac.setPosition(btn_op_minus, 20, 120)
    ac.setSize(btn_op_minus, 40, 30)
    ac.addOnClickedListener(btn_op_minus, btn_op_minus)
    
    lbl_opacity = ac.addLabel(cfgWindow, "Opacity: ")
    ac.setPosition(lbl_opacity, 80, 125)
    
    btn_op_plus = ac.addButton(cfgWindow, "+")
    ac.setPosition(btn_op_plus, 160, 120)
    ac.setSize(btn_op_plus, 40, 30)
    ac.addOnClickedListener(btn_op_plus, btn_op_plus)

    btn_tm_minus = ac.addButton(cfgWindow, "-")
    ac.setPosition(btn_tm_minus, 20, 160)
    ac.setSize(btn_tm_minus, 40, 30)
    ac.addOnClickedListener(btn_tm_minus, btn_time_minus)
    
    lbl_time = ac.addLabel(cfgWindow, "Time: ")
    ac.setPosition(lbl_time, 80, 165)
    
    btn_tm_plus = ac.addButton(cfgWindow, "+")
    ac.setPosition(btn_tm_plus, 160, 160)
    ac.setSize(btn_tm_plus, 40, 30)
    ac.addOnClickedListener(btn_tm_plus, btn_time_plus)
    
    btn_col = ac.addButton(cfgWindow, "Change")
    ac.setPosition(btn_col, 20, 200)
    ac.setSize(btn_col, 80, 30)
    ac.addOnClickedListener(btn_col, btn_color_toggle)
    
    lbl_color = ac.addLabel(cfgWindow, "Color: ")
    ac.setPosition(lbl_color, 110, 205)
    
    btn_snd = ac.addButton(cfgWindow, "Toggle")
    ac.setPosition(btn_snd, 20, 240)
    ac.setSize(btn_snd, 80, 30)
    ac.addOnClickedListener(btn_snd, btn_sound_toggle)
    
    lbl_sound = ac.addLabel(cfgWindow, "Sound: ")
    ac.setPosition(lbl_sound, 110, 245)
    
    btn_men = ac.addButton(cfgWindow, "Toggle")
    ac.setPosition(btn_men, 20, 280)
    ac.setSize(btn_men, 80, 30)
    ac.addOnClickedListener(btn_men, btn_mention_toggle)
    
    btn_test = ac.addButton(cfgWindow, "TEST / MOVE MODE")
    ac.setPosition(btn_test, 20, 320)
    ac.setSize(btn_test, 260, 30)
    ac.addOnClickedListener(btn_test, toggle_test_mode)
    
    lbl_kw = ac.addLabel(cfgWindow, "Keywords (comma separated):")
    ac.setPosition(lbl_kw, 20, 360) 
    
    txt_keywords = ac.addTextInput(cfgWindow, "txt_kw")
    ac.setPosition(txt_keywords, 20, 385) 
    ac.setSize(txt_keywords, 260, 30)
    ac.setText(txt_keywords, ",".join(KEYWORDS))
    
    btn_save = ac.addButton(cfgWindow, "SAVE SETTINGS")
    ac.setPosition(btn_save, 20, 430) 
    ac.setSize(btn_save, 260, 40)
    ac.addOnClickedListener(btn_save, save_settings)
    
    update_config_labels() 
    
    return "IsuChatAlert"

def acUpdate(deltaT):
    global display_timer, is_alert_active, bg_box, accent_line, chat_label, author_bold_1, author_bold_2, current_max_time
    global save_feedback_timer, btn_save, SET_OPACITY, is_test_mode, FADE_TIME
    
    if save_feedback_timer > 0:
        save_feedback_timer -= deltaT
        if save_feedback_timer <= 0:
            ac.setText(btn_save, "SAVE SETTINGS")
            
    if is_alert_active:
        current_opacity = 1.0
        
        if not is_test_mode:
            display_timer -= deltaT
            
            # Sadece normal moddayken fade animasyonu hesapla
            if display_timer > (current_max_time - FADE_TIME):
                current_opacity = (current_max_time - display_timer) / FADE_TIME
            elif display_timer < FADE_TIME:
                current_opacity = max(0.0, display_timer / FADE_TIME)
        else:
            # TEST MODUNDAYKEN HEP %100 GÖRÜNÜR OLACAK SENPAI!
            current_opacity = 1.0
            display_timer = current_max_time # Kapanmaması için süreyi donduruyoruz
            
        ac.setBackgroundOpacity(bg_box, current_opacity * SET_OPACITY) 
        ac.setBackgroundOpacity(accent_line, current_opacity)   
        
        ac.setFontColor(chat_label, 1.0, 0.98, 0.9, current_opacity) 
        ac.setFontColor(author_bold_1, 1.0, 1.0, 1.0, current_opacity) 
        ac.setFontColor(author_bold_2, 1.0, 1.0, 1.0, current_opacity) 
        
        if display_timer <= 0 and not is_test_mode:
            ac.setText(chat_label, "")
            ac.setText(author_bold_1, "")
            ac.setText(author_bold_2, "")
            sleep_mode() 
            is_alert_active = False
            
def acShutdown():
    global appWindow
    # EN ÖNEMLİ KISIM: Assetto Corsa kapanırken pencere pozisyonunu kaydetsin diye saniyelik olarak başlığı geri veriyoruz!
    ac.setTitle(appWindow, "IsuChatAlert")
