# main.py
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import cv2
import numpy as np
import time
import pygetwindow as gw # Thư viện bọc Win32 API điều khiển cửa sổ chuyên dụng
from . import config
from .detector import FaceDetector
from .filters import DualOneEuroFilter
from .controller import MouseController
from .virtual_keyboard import VirtualKeyboard

RUNNING = True

def stop_system():
    global RUNNING
    RUNNING = False

def main():
    global RUNNING
    RUNNING = True

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)

    detector = FaceDetector()
    mouse_filter = DualOneEuroFilter(freq=config.FILTER_FREQ, min_cutoff=config.FILTER_MIN_CUTOFF, beta=config.FILTER_BETA)
    mouse_controller = MouseController()
    virtual_kb = VirtualKeyboard()

    is_mode_selected = False       
    is_calibrated = False          
    has_minimized = False 
    
    tilt_start_time = None
    pending_mode = None
    stable_center_start_time = None
    last_stable_nose_x = 0.5
    last_stable_nose_y = 0.5

    mouth_open_start_time = None
    hot_corner_start_time = None       
    resume_mouth_start_time = None     
    scroll_anchor_y = None

    window_name = "EzTouch Biometric Dashboard"
    widget_name = "EzTouch Status Widget"
    
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

    cv2.namedWindow(widget_name, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty(widget_name, cv2.WND_PROP_TOPMOST, 1)
    widget_w, widget_h = 380, 120
    cv2.moveWindow(widget_name, config.SCREEN_WIDTH - widget_w - 15, (config.SCREEN_HEIGHT - widget_h) // 2)

    while cap.isOpened() and RUNNING:
        success, frame = cap.read()
        if not success: break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        overlay = frame.copy()

        results = detector.process_frame(frame)
        raw_nose_x, raw_nose_y = detector.get_nose_position(results)
        mouth_ratio = detector.get_mouth_open_ratio(results)
        head_roll = detector.get_head_roll(results)
        current_time = time.time()

        widget_frame = np.zeros((widget_h, widget_w, 3), dtype=np.uint8) + 24

        # ==========================================
        # GIAI ĐOẠN 0: NGHIÊNG ĐẦU CHỌN CHẾ ĐỘ
        # ==========================================
        if not is_mode_selected:
            rem_time = 2.0
            if head_roll is not None:
                if head_roll < config.ROLL_SELECT_LEFT:
                    if pending_mode != "PARKINSON":
                        pending_mode = "PARKINSON"
                        tilt_start_time = current_time
                    elapsed_tilt = current_time - tilt_start_time
                    rem_time = max(0.0, config.SELECT_HOLD_DURATION - elapsed_tilt)
                    config.trial_countdown_pct = min(50, int((elapsed_tilt / config.SELECT_HOLD_DURATION) * 50))
                    if elapsed_tilt >= config.SELECT_HOLD_DURATION:
                        config.CURRENT_MODE = "PARKINSON"
                        config.FILTER_MIN_CUTOFF = 0.04      
                        is_mode_selected = True
                        stable_center_start_time = time.time()
                elif head_roll > config.ROLL_SELECT_RIGHT:
                    if pending_mode != "REGULAR":
                        pending_mode = "REGULAR"
                        tilt_start_time = current_time
                    elapsed_tilt = current_time - tilt_start_time
                    rem_time = max(0.0, config.SELECT_HOLD_DURATION - elapsed_tilt)
                    config.trial_countdown_pct = min(50, int((elapsed_tilt / config.SELECT_HOLD_DURATION) * 50))
                    if elapsed_tilt >= config.SELECT_HOLD_DURATION:
                        config.CURRENT_MODE = "REGULAR"
                        config.FILTER_MIN_CUTOFF = 0.45      
                        is_mode_selected = True
                        stable_center_start_time = time.time()
                else:
                    tilt_start_time = None
                    pending_mode = None
                    config.trial_countdown_pct = 0

            cv2.putText(widget_frame, "TRAI THAI: KHAO SAT MOI", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 225, 255), 2, cv2.LINE_AA)
            if pending_mode:
                cv2.putText(widget_frame, f"Dang chon: {pending_mode} ({rem_time:.1f}s)", (15, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(widget_frame, "Hay nghieng dau de chon...", (15, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1, cv2.LINE_AA)
            cv2.imshow(widget_name, widget_frame)

            cv2.rectangle(overlay, (0, 0), (w, h), (25, 25, 25), -1)
            cv2.putText(frame, "KHAO SAT THET LAP HE THONG EZTOUCH", (w // 2 - 240, h // 2 - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
            box_l_col = (0, 255, 127) if pending_mode == "PARKINSON" else (100, 100, 100)
            cv2.rectangle(overlay, (60, h // 2 + 20), (400, h // 2 + 100), box_l_col, 2)
            cv2.putText(frame, "NGHIENG TRAI: BAO VE CHONG RUN", (85, h // 2 + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_l_col, 2, cv2.LINE_AA)
            box_r_col = (0, 165, 255) if pending_mode == "REGULAR" else (100, 100, 100)
            cv2.rectangle(overlay, (w - 400, h // 2 + 20), (w - 60, h // 2 + 100), box_r_col, 2)
            cv2.putText(frame, "NGHIENG PHAI: LUOT SIEU TOC", (w - 365, h // 2 + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_r_col, 2, cv2.LINE_AA)
            
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            continue

        # ==========================================
        # GIAI ĐOẠN 1: AUTO-CENTER CHỐT VÙNG AN TOÀN
        # ==========================================
        if not is_calibrated:
            rem_stable = 1.5
            if raw_nose_x is not None and raw_nose_y is not None:
                if stable_center_start_time is None:
                    stable_center_start_time = current_time
                    last_stable_nose_x = raw_nose_x
                    last_stable_nose_y = raw_nose_y
                else:
                    if abs(raw_nose_x - last_stable_nose_x) > 0.025 or abs(raw_nose_y - last_stable_nose_y) > 0.025:
                        stable_center_start_time = current_time
                        last_stable_nose_x = raw_nose_x
                        last_stable_nose_y = raw_nose_y

                elapsed_stable = current_time - stable_center_start_time
                rem_stable = max(0.0, config.AUTOCENTER_STABLE_DURATION - elapsed_stable)
                config.trial_countdown_pct = min(100, 50 + int((elapsed_stable / config.AUTOCENTER_STABLE_DURATION) * 50))

                if elapsed_stable >= config.AUTOCENTER_STABLE_DURATION:
                    config.CALIBRATED_CENTER_X = last_stable_nose_x
                    config.CALIBRATED_CENTER_Y = last_stable_nose_y
                    config.FRAME_INNER_X1 = last_stable_nose_x - 0.25
                    config.FRAME_INNER_X2 = last_stable_nose_x + 0.25
                    config.FRAME_INNER_Y1 = last_stable_nose_y - 0.25
                    config.FRAME_INNER_Y2 = last_stable_nose_y + 0.25
                    is_calibrated = True
                    config.trial_countdown_pct = 100

            cv2.putText(widget_frame, f"CHE DO: {config.CURRENT_MODE}", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 127), 2, cv2.LINE_AA)
            cv2.putText(widget_frame, f"Dang chot tam an toan: {rem_stable:.1f}s", (15, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow(widget_name, widget_frame)

            cv2.putText(frame, f"DA CHON CHEDE: {config.CURRENT_MODE}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 127), 2, cv2.LINE_AA)
            cv2.putText(frame, "HAY GIU YEN VI TRI DAU CO DINH THOAI MAI DE CHOT TAM AN TOAN", (30, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            if raw_nose_x is not None:
                cv2.circle(frame, (int(raw_nose_x * w), int(raw_nose_y * h)), 20, (0, 165, 255), 2)
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            continue

        # ==========================================
        # GIAI ĐOẠN 2: LUỒNG ĐIỀU KHIỂN CHÍNH (🌟 FIX AUTO-MINIMIZE BẰNG PYGETWINDOW)
        # ==========================================
        if is_calibrated and not has_minimized:
            try:
                target_window = gw.getWindowsWithTitle(window_name)
                if target_window:
                    target_window[0].minimize() # Ép camera tự động thu nhỏ vật lý xuống thanh Taskbar
                    has_minimized = True
            except:
                pass

        sub_action_text = "Chuot: San sang dieu khien"
        
        if raw_nose_x is not None and raw_nose_y is not None:
            filtered_x, filtered_y = mouse_filter.update(raw_nose_x, raw_nose_y)

            if config.system_state == "PAUSED":
                rem_resume = 3.0
                if mouth_ratio > config.DYNAMIC_MOUTH_THRESH:
                    if resume_mouth_start_time is None:
                        resume_mouth_start_time = current_time
                    elapsed_res = current_time - resume_mouth_start_time
                    rem_resume = max(0.0, config.RESUME_MOUTH_DURATION - elapsed_res)
                    sub_action_text = f"Dang mo khoa khoi Pause: {rem_resume:.1f}s"
                    if elapsed_res >= config.RESUME_MOUTH_DURATION:
                        config.system_state = "RUNNING"
                        resume_mouth_start_time = None
                else:
                    resume_mouth_start_time = None
                    sub_action_text = "He thong dang PAUSED. Ha mom 3s de mo"

            if config.system_state == "RUNNING":
                if mouth_ratio > config.DYNAMIC_MOUTH_THRESH:
                    if mouth_open_start_time is None:
                        mouth_open_start_time = current_time
                    elapsed_mouth = current_time - mouth_open_start_time
                    
                    if elapsed_mouth >= config.DRAG_MIN_DURATION:
                        if not mouse_controller.is_scroll_mode:
                            mouse_controller.is_scroll_mode = True
                            scroll_anchor_y = filtered_y if config.CURRENT_MODE == "PARKINSON" else raw_nose_y
                        sub_action_text = "🔥 DANG DI CHUYEN CUON TRANG"
                    else:
                        rem_drag = max(0.0, config.DRAG_MIN_DURATION - elapsed_mouth)
                        sub_action_text = f"Giu mom mo: {rem_drag:.1f}s de bat Cuon chuot"
                else:
                    if mouth_open_start_time is not None:
                        duration = current_time - mouth_open_start_time
                        if duration <= config.CLICK_MAX_DURATION and not mouse_controller.is_scroll_mode:
                            was_typing = False
                            if config.is_keyboard_open:
                                was_typing = virtual_kb.execute_active_mouth_type()
                            if not was_typing:
                                mouse_controller.execute_click()
                        if mouse_controller.is_scroll_mode:
                            mouse_controller.is_scroll_mode = False
                        mouth_open_start_time = None

            input_x = filtered_x if config.CURRENT_MODE == "PARKINSON" else raw_nose_x
            input_y = filtered_y if config.CURRENT_MODE == "PARKINSON" else raw_nose_y

            clamped_x = np.clip(input_x, config.FRAME_INNER_X1, config.FRAME_INNER_X2)
            clamped_y = np.clip(input_y, config.FRAME_INNER_Y1, config.FRAME_INNER_Y2)
            
            if config.system_state == "RUNNING" and not mouse_controller.is_scroll_mode:
                mouse_controller.move_to_smooth(clamped_x, clamped_y)
            if config.system_state == "RUNNING" and mouse_controller.is_scroll_mode and scroll_anchor_y is not None:
                mouse_controller.execute_scroll(scroll_anchor_y, input_y)

            if config.system_state == "RUNNING":
                import pyautogui as pg 
                cx, cy = pg.position()
                if cx <= 15 and cy <= 15:
                    if hot_corner_start_time is None:
                        hot_corner_start_time = current_time
                    elapsed_corner = current_time - hot_corner_start_time
                    rem_corner = max(0.0, 2.0 - elapsed_corner)
                    sub_action_text = f"Ghim HotCorner! Pause sau: {rem_corner:.1f}s"
                    if elapsed_corner >= 2.0:
                        config.system_state = "PAUSED"
                        mouse_controller.is_scroll_mode = False
                        hot_corner_start_time = None
                else:
                    hot_corner_start_time = None

            center_pt = (int(clamped_x * w), int(clamped_y * h))
            hud_color = (255, 0, 127) if mouse_controller.is_scroll_mode else ((0, 255, 127) if config.system_state == "RUNNING" else (0, 0, 255))
            cv2.circle(frame, center_pt, 6, hud_color, -1)
            cv2.circle(frame, center_pt, 14, (255, 255, 255), 2)
            
            x1, y1 = int(config.FRAME_INNER_X1 * w), int(config.FRAME_INNER_Y1 * h)
            x2, y2 = int(config.FRAME_INNER_X2 * w), int(config.FRAME_INNER_Y2 * h)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)

        virtual_kb.check_dwell_clicking()
        
        status_color = (0, 255, 127) if config.system_state == "RUNNING" else (0, 0, 255)
        cv2.putText(widget_frame, f"TRANG THAI: {config.system_state}", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.58, status_color, 2, cv2.LINE_AA)
        
        kb_status = "ON (DANG MO)" if config.is_keyboard_open else "OFF (DANG AN)"
        kb_color = (0, 165, 255) if config.is_keyboard_open else (140, 140, 140)
        cv2.putText(widget_frame, f"Ban phim ao: {kb_status}", (15, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.48, kb_color, 1, cv2.LINE_AA)
        cv2.putText(widget_frame, f"Hanh vi -> {sub_action_text}", (15, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)
        
        cv2.imshow(widget_name, widget_frame)

        cv2.putText(frame, f"STATE: {config.system_state} | MODE: {config.CURRENT_MODE}", (20, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    try:
        cv2.destroyWindow(window_name)
        cv2.destroyWindow(widget_name)
    except:
        pass

if __name__ == "__main__":
    main()