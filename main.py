# main.py
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import cv2
import numpy as np
import time
import config
from detector import FaceDetector
from filters import DualOneEuroFilter
from controller import MouseController
from virtual_keyboard import VirtualKeyboard

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

    # --- BIẾN QUẢN LÝ TIẾN TRÌNH ---
    is_mode_selected = False       
    is_calibrated = False          
    is_system_active = True       
    
    calibration_start = None
    calib_mouth_samples = []

    # Logic Timing
    mouth_open_start_time = None
    hot_corner_start_time = None       
    resume_mouth_start_time = None     

    # Bộ đệm thời gian đóng mở phím ảo
    kb_open_timer = None
    kb_close_timer = None

    # Quản lý thời gian Auto-Sleep
    face_last_seen_time = time.time()  

    # Biến theo dõi nghiêng đầu chọn chế độ sơ khởi
    tilt_start_time = None
    pending_mode = None

    # Biến quản lý Auto-Center tâm mũi động
    stable_center_start_time = None
    last_stable_nose_x = 0.5
    last_stable_nose_y = 0.5

    ui_flash_trigger = 0
    ui_status_text = "CHO CHON CHE DO..."
    widget_countdown_text = ""

    # Khởi tạo Widget thanh trạng thái độc lập Alway-on-Top kịch biên phải máy tính
    widget_name = "FacileTouch Status Widget"
    cv2.namedWindow(widget_name, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty(widget_name, cv2.WND_PROP_TOPMOST, 1)
    widget_w, widget_h = 360, 110
    cv2.moveWindow(widget_name, config.SCREEN_WIDTH - widget_w - 10, (config.SCREEN_HEIGHT - widget_h) // 2)

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

        # Luồng xử lý trạng thái Auto-Sleep (Mất mặt)
        if results.multi_face_landmarks:
            face_last_seen_time = current_time  
            if config.system_state == "SLEEP":
                config.system_state = config.prev_system_state
                ui_status_text = f"WELCOME BACK! HE THONG: {config.system_state}"
                ui_flash_trigger = 8
        else:
            if config.system_state != "SLEEP" and (current_time - face_last_seen_time >= config.FACE_ABSENCE_DURATION):
                config.prev_system_state = config.system_state
                config.system_state = "SLEEP"
                mouse_controller.is_scroll_mode = False
                ui_flash_trigger = 8
                
        if config.system_state == "SLEEP":
            widget_frame = np.zeros((widget_h, widget_w, 3), dtype=np.uint8) + 25
            cv2.putText(widget_frame, "STATE: SLEEP (KHOA MÁY)", (15, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 120, 120), 2, cv2.LINE_AA)
            cv2.putText(widget_frame, "HAY QUAY LAI TRUOC CAM", (15, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.imshow(widget_name, widget_frame)
            
            cv2.rectangle(overlay, (0, 0), (w, h), (15, 15, 15), -1)
            cv2.putText(frame, "STATUS: SLEEP MODE - DETECTING FACE...", (30, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
            cv2.imshow("Head Mouse Accessibility Dashboard", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            continue

        widget_countdown_text = ""
        is_toggling_keyboard = False  # Cờ an toàn chặn gõ lặp gây crash

        # ==========================================
        # GIAI ĐOẠN 0: NGHIÊNG ĐẦU CHỌN CHẾ ĐỘ 3.0 GIÂY
        # ==========================================
        if not is_mode_selected:
            if head_roll is not None:
                if head_roll < config.ROLL_SELECT_LEFT:
                    if pending_mode != "PARKINSON":
                        pending_mode = "PARKINSON"
                        tilt_start_time = current_time
                    
                    elapsed_tilt = current_time - tilt_start_time
                    rem_time = max(0.0, config.SELECT_HOLD_DURATION - elapsed_tilt)
                    widget_countdown_text = f"Giu {rem_time:.1f}s de vao PARKINSON"
                    ui_status_text = f"DANG CHON PARKINSON... ({rem_time:.1f}s)"
                    
                    if elapsed_tilt >= config.SELECT_HOLD_DURATION:
                        config.CURRENT_MODE = "PARKINSON"
                        config.FILTER_MIN_CUTOFF = 0.04      
                        is_mode_selected = True
                        stable_center_start_time = time.time()
                        ui_status_text = "DA KICH HOAT: CHE DO CHONG RUN"
                
                elif head_roll > config.ROLL_SELECT_RIGHT:
                    if pending_mode != "REGULAR":
                        pending_mode = "REGULAR"
                        tilt_start_time = current_time
                    
                    elapsed_tilt = current_time - tilt_start_time
                    rem_time = max(0.0, config.SELECT_HOLD_DURATION - elapsed_tilt)
                    widget_countdown_text = f"Giu {rem_time:.1f}s de vao SIEU TOC"
                    ui_status_text = f"DANG CHON SIEU TOC... ({rem_time:.1f}s)"
                    
                    if elapsed_tilt >= config.SELECT_HOLD_DURATION:
                        config.CURRENT_MODE = "REGULAR"
                        config.FILTER_MIN_CUTOFF = 0.50      
                        is_mode_selected = True
                        stable_center_start_time = time.time()
                        ui_status_text = "DA KICH HOAT: CHE DO SIEU TOC"
                
                else:
                    tilt_start_time = None
                    pending_mode = None
                    ui_status_text = "HAY NGHIENG DAU DE CHON CHE DO"

            cv2.rectangle(overlay, (0, 0), (w, h), (25, 25, 25), -1)
            cv2.putText(frame, "KHAO SAT HE THONG FACILETOUCH", (w // 2 - 240, h // 2 - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "BAN CO TIEN SU BI CAC VAN DE VE RUN KHONG?", (w // 2 - 320, h // 2 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 127), 1, cv2.LINE_AA)
            cv2.putText(frame, f"Goc nghieng co: {head_roll:.1f} deg", (w // 2 - 110, h // 2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            
            box_left_color = (0, 255, 127) if pending_mode == "PARKINSON" else (100, 100, 100)
            cv2.rectangle(overlay, (80, h // 2 + 50), (380, h // 2 + 130), box_left_color, 1 if pending_mode != "PARKINSON" else 2)
            cv2.putText(frame, "NGHIENG TRAI = CO", (140, h // 2 + 85), cv2.FONT_HERSHEY_SIMPLEX, 0.55, box_left_color, 2, cv2.LINE_AA)
            cv2.putText(frame, "(Che do cho nguoi run)", (135, h // 2 + 110), cv2.FONT_HERSHEY_SIMPLEX, 0.45, box_left_color, 1, cv2.LINE_AA)
            
            box_right_color = (0, 165, 255) if pending_mode == "REGULAR" else (100, 100, 100)
            cv2.rectangle(overlay, (w - 380, h // 2 + 50), (w - 80, h // 2 + 130), box_right_color, 1 if pending_mode != "REGULAR" else 2)
            cv2.putText(frame, "NGHIENG PHAI = KHONG", (w - 330, h // 2 + 85), cv2.FONT_HERSHEY_SIMPLEX, 0.55, box_right_color, 2, cv2.LINE_AA)
            cv2.putText(frame, "(Che do phan xa nhanh)", (w - 335, h // 2 + 110), cv2.FONT_HERSHEY_SIMPLEX, 0.45, box_right_color, 1, cv2.LINE_AA)
            
            cv2.rectangle(overlay, (15, h - 45), (550, h - 15), (20, 20, 20), -1)
            cv2.putText(frame, f"STATUS: {ui_status_text}", (25, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            cv2.imshow("Head Mouse Accessibility Dashboard", frame)
            
            widget_frame = np.zeros((widget_h, widget_w, 3), dtype=np.uint8) + 25
            cv2.putText(widget_frame, "STATE: KHAO SAT", (15, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2, cv2.LINE_AA)
            cv2.text_display = widget_countdown_text if widget_countdown_text else "Nghieng co de chon..."
            cv2.putText(widget_frame, cv2.text_display, (15, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow(widget_name, widget_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            continue

        # ==========================================
        # GIAI ĐOẠN 1: AUTO-CENTER TRONG 2 GIÂY CHUẨN XÁC
        # ==========================================
        if not is_calibrated:
            if raw_nose_x is not None and raw_nose_y is not None:
                calib_mouth_samples.append(mouth_ratio)
                
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
                countdown_stable = max(0.0, config.AUTOCENTER_STABLE_DURATION - elapsed_stable)
                widget_countdown_text = f"Giu {countdown_stable:.1f}s de CHOT TAM"
                ui_status_text = f"DANG CHOT TAM... ({countdown_stable:.1f}s)"

                cv2.rectangle(overlay, (0, 0), (w, h), (30, 30, 30), -1)
                cv2.putText(frame, f"KICH HOAT: {config.CURRENT_MODE} MODE", (w // 2 - 180, h // 2 - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 127), 2, cv2.LINE_AA)
                cv2.putText(frame, "GIU NGOI CO DINH THOAI MAI VA HA MOM MAX TRONG: " + f"{countdown_stable:.1f}s", (w // 2 - 380, h // 2 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
                
                cv2.circle(frame, (int(raw_nose_x * w), int(raw_nose_y * h)), 18, (0, 165, 255), 2)
                cv2.rectangle(overlay, (w // 2 - 200, h // 2 + 30), (w // 2 - 200 + int(elapsed_stable * 200), h // 2 + 45), (0, 255, 127), -1)

                if elapsed_stable >= config.AUTOCENTER_STABLE_DURATION:
                    config.CALIBRATED_CENTER_X = last_stable_nose_x
                    config.CALIBRATED_CENTER_Y = last_stable_nose_y
                    config.DYNAMIC_MOUTH_THRESH = max(0.04, np.max(calib_mouth_samples) * 0.30) if calib_mouth_samples else 0.045
                    
                    config.FRAME_INNER_X1 = last_stable_nose_x - 0.25
                    config.FRAME_INNER_X2 = last_stable_nose_x + 0.25
                    config.FRAME_INNER_Y1 = last_stable_nose_y - 0.25
                    config.FRAME_INNER_Y2 = last_stable_nose_y + 0.25
                    
                    is_calibrated = True
                    ui_status_text = "HETHONG SAN SANG"
                    face_last_seen_time = time.time()
            
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
            cv2.imshow("Head Mouse Accessibility Dashboard", frame)
            
            widget_frame = np.zeros((widget_h, widget_w, 3), dtype=np.uint8) + 25
            cv2.putText(widget_frame, f"MODE: {config.CURRENT_MODE}", (15, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 127), 2, cv2.LINE_AA)
            cv2.putText(widget_frame, widget_countdown_text, (15, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow(widget_name, widget_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            continue

        # ==========================================
        # GIAI ĐOẠN 2: LUỒNG ĐIỀU KHIỂN CHÍNH
        # ==========================================
        if raw_nose_x is not None and raw_nose_y is not None:
            
            # Logic đóng mở bàn phím ảo bằng cử chỉ phối hợp
            if config.system_state == "RUNNING" and head_roll is not None:
                if (head_roll > config.ROLL_SELECT_RIGHT) and (mouth_ratio > config.DYNAMIC_MOUTH_THRESH):
                    if not config.is_keyboard_open:
                        if kb_open_timer is None:
                            kb_open_timer = current_time
                        elapsed_kb = current_time - kb_open_timer
                        rem_kb = max(0.0, 3.6 - elapsed_kb)
                        widget_countdown_text = f"Giu {rem_kb:.1f}s de BAT BAN PHIM"
                        ui_status_text = f"DANG DE NGHI MO PHIM AO... ({rem_kb:.1f}s)"
                        if elapsed_kb >= 3.6:
                            config.is_keyboard_open = True
                            is_toggling_keyboard = True  
                            ui_status_text = "DA MO BAN PHIM AO FLOATING CHINH"
                            ui_flash_trigger = 5
                            kb_open_timer = None
                else:
                    kb_open_timer = None

                if (head_roll < config.ROLL_SELECT_LEFT) and (mouth_ratio > config.DYNAMIC_MOUTH_THRESH):
                    if config.is_keyboard_open:
                        if kb_close_timer is None:
                            kb_close_timer = current_time
                        elapsed_kb = current_time - kb_close_timer
                        rem_kb = max(0.0, 3.6 - elapsed_kb)
                        widget_countdown_text = f"Giu {rem_kb:.1f}s de TAT BAN PHIM"
                        ui_status_text = f"DANG DE NGHI TAT PHIM... ({rem_kb:.1f}s)"
                        if elapsed_kb >= 3.6:
                            config.is_keyboard_open = False
                            is_toggling_keyboard = True  
                            ui_status_text = "DA TAT BAN PHIM AO"
                            ui_flash_trigger = 5
                            kb_close_timer = None
                else:
                    kb_close_timer = None

            if config.system_state == "PAUSED":
                if mouth_ratio > config.DYNAMIC_MOUTH_THRESH:
                    if resume_mouth_start_time is None:
                        resume_mouth_start_time = current_time
                    elapsed_resume = current_time - resume_mouth_start_time
                    rem_res = max(0.0, config.RESUME_MOUTH_DURATION - elapsed_resume)
                    widget_countdown_text = f"Giu {rem_res:.1f}s de KICH HOAT"
                    ui_status_text = f"HA MOM DE RESUME... ({rem_res:.1f}s)"
                    if elapsed_resume >= config.RESUME_MOUTH_DURATION:
                        config.system_state = "RUNNING"
                        ui_status_text = "HE THONG TRO LAI HOAT DONG"
                        ui_flash_trigger = 8
                        resume_mouth_start_time = None
                else:
                    resume_mouth_start_time = None
                    ui_status_text = "HE THONG DANG TAM DUNG (PAUSED) - HA MOM 3S DE MO"

            # Luồng gõ Click / Scroll thích ứng tự do
            if config.system_state == "RUNNING":
                if mouth_ratio > config.DYNAMIC_MOUTH_THRESH:
                    if mouth_open_start_time is None:
                        mouth_open_start_time = current_time
                    if (current_time - mouth_open_start_time >= config.DRAG_MIN_DURATION) and not mouse_controller.is_scroll_mode:
                        mouse_controller.is_scroll_mode = True
                        scroll_anchor_y = raw_nose_y
                        ui_status_text = "CHEDO: CUON CHUOT DOC..."
                else:
                    if mouth_open_start_time is not None:
                        duration = current_time - mouth_open_start_time
                        if duration <= config.CLICK_MAX_DURATION and not mouse_controller.is_scroll_mode:
                            if config.is_keyboard_open and virtual_kb.is_dragging_mode:
                                virtual_kb.is_dragging_mode = False
                                ui_status_text = "DA GHIM BAN PHIM AO CO DINH"
                                ui_flash_trigger = 3
                            else:
                                was_typing = False
                                if config.is_keyboard_open:
                                    was_typing = virtual_kb.execute_active_mouth_type()
                                
                                # 🌟 VÁ LỖI CRASH: Tuyệt đối không click chuột đè lên màn hình nền nếu vừa phát sinh cử chỉ Mở/Đóng bàn phím
                                if not was_typing and not is_toggling_keyboard:
                                    mouse_controller.execute_click()
                                    ui_status_text = "CLICK CHUOT TRAI TỨC THỜI"
                                    ui_flash_trigger = 3
                        if mouse_controller.is_scroll_mode:
                            mouse_controller.is_scroll_mode = False
                            ui_status_text = "THOAT CHEDO CUON CHUOT"
                            ui_flash_trigger = 3
                        mouth_open_start_time = None

            # Ánh xạ tọa độ chuột kịch biên an toàn 1:1
            clamped_x = np.clip(raw_nose_x, config.FRAME_INNER_X1, config.FRAME_INNER_X2)
            clamped_y = np.clip(raw_nose_y, config.FRAME_INNER_Y1, config.FRAME_INNER_Y2)
            
            if config.system_state == "RUNNING" and not mouse_controller.is_scroll_mode:
                mouse_controller.move_to_smooth(clamped_x, clamped_y)
            
            if config.system_state == "RUNNING" and mouse_controller.is_scroll_mode and scroll_anchor_y is not None:
                mouse_controller.execute_scroll(scroll_anchor_y, raw_nose_y)
            
            # Hot corner vật lý góc (0,0) chuyển sang PAUSED
            if config.system_state == "RUNNING":
                import pyautogui as pg 
                current_mouse_x, current_mouse_y = pg.position()
                if (current_mouse_x <= 15) and (current_mouse_y <= 15):
                    if hot_corner_start_time is None:
                        hot_corner_start_time = current_time
                    elapsed_corner = current_time - hot_corner_start_time
                    rem_corner = max(0.0, config.HOT_CORNER_DURATION - elapsed_corner)
                    widget_countdown_text = f"Giu {rem_corner:.1f}s de PAUSE CHUOT"
                    ui_status_text = f"GIU GOV MAN HINH DE PAUSE... ({rem_corner:.1f}s)"
                    if elapsed_corner >= config.HOT_CORNER_DURATION:
                        config.system_state = "PAUSED"
                        mouse_controller.is_scroll_mode = False
                        ui_flash_trigger = 8
                        hot_corner_start_time = None
                else:
                    hot_corner_start_time = None

            # Đồ họa tâm xanh lá
            center_pt = (int(clamped_x * w), int(clamped_y * h))
            hud_color = (255, 0, 127) if mouse_controller.is_scroll_mode else ((0, 255, 127) if config.system_state == "RUNNING" else (0, 0, 255))
            cv2.circle(frame, center_pt, 6, hud_color, -1)    
            cv2.circle(frame, center_pt, 14, (255, 255, 255), 2)
            
            real_nose_pt = (int(raw_nose_x * w), int(raw_nose_y * h))
            if real_nose_pt != center_pt:
                cv2.circle(frame, real_nose_pt, 4, (120, 120, 120), -1)

        # Chạy kiểm tra gõ Dwell-Click phím nổi ngoài đời thực
        virtual_kb.check_dwell_clicking()

        # CẬP NHẬT GIAO DIỆN THANH WIDGET NỔI ĐỘC LẬP NGOÀI MÀN HÌNH
        widget_frame = np.zeros((widget_h, widget_w, 3), dtype=np.uint8) + 25
        status_color = (0, 255, 127) if config.system_state == "RUNNING" else ((0, 0, 255) if config.system_state == "PAUSED" else (120, 120, 120))
            
        cv2.putText(widget_frame, f"STATE: {config.system_state}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.58, status_color, 2, cv2.LINE_AA)
        cv2.putText(widget_frame, f"MODE : {config.CURRENT_MODE} | KB: {'DRAG' if virtual_kb.is_dragging_mode else ('ON' if config.is_keyboard_open else 'OFF')}", (15, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
        
        text_display = widget_countdown_text if widget_countdown_text else "FACILETOUCH READY"
        text_color = (0, 165, 255) if widget_countdown_text else (150, 150, 150)
        cv2.putText(widget_frame, text_display, (15, 86), cv2.FONT_HERSHEY_SIMPLEX, 0.45, text_color, 1, cv2.LINE_AA)
        cv2.imshow(widget_name, widget_frame)

        # ĐỒ HỌA HUD TRÊN CAMERA GỐC
        x1 = int(max(0.0, config.FRAME_INNER_X1) * w)
        y1 = int(max(0.0, config.FRAME_INNER_Y1) * h)
        x2 = int(min(1.0, config.FRAME_INNER_X2) * w)
        y2 = int(min(1.0, config.FRAME_INNER_Y2) * h)
        
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 255, 255) if config.system_state == "RUNNING" else (0, 0, 150), 2)
        cv2.putText(frame, f"VUNG AN TOAN QUY CHUAN ({config.CURRENT_MODE} MODE)", (x1 + 5, y1 + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        bar_x1, bar_y1 = w - 45, h - 250
        bar_x2, bar_y2 = w - 20, h - 50
        cv2.rectangle(overlay, (bar_x1, bar_y1), (bar_x2, bar_y2), (40, 40, 40), -1)
        
        max_exp = config.DYNAMIC_MOUTH_THRESH * 2.5
        fill_level = int(np.interp(mouth_ratio, [0, max_exp], [0, 200]))
        fill_level = max(0, min(200, fill_level))
        thresh_y = bar_y2 - int(np.interp(config.DYNAMIC_MOUTH_THRESH, [0, max_exp], [0, 200]))
        
        bar_color = (255, 0, 127) if mouse_controller.is_scroll_mode else ((0, 255, 127) if mouth_ratio > config.DYNAMIC_MOUTH_THRESH else (255, 200, 0))
        cv2.rectangle(overlay, (bar_x1, bar_y2 - fill_level), (bar_x2, bar_y2), bar_color, -1)
        cv2.line(overlay, (bar_x1 - 5, thresh_y), (bar_x2 + 5, thresh_y), (0, 165, 255), 2)
        
        cv2.rectangle(overlay, (15, h - 45), (650, h - 15), (20, 20, 20), -1)
        cv2.putText(frame, f"STATE: {config.system_state} | STATUS: {ui_status_text}", (25, h - 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        if ui_flash_trigger > 0:
            flash = np.zeros_like(frame)
            flash[:] = (0, 255, 127) if config.system_state == "RUNNING" else (0, 0, 255)
            cv2.addWeighted(flash, 0.3, frame, 0.7, 0, frame)
            ui_flash_trigger -= 1

        cv2.imshow("Head Mouse Accessibility Dashboard", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyWindow(widget_name)
    if virtual_kb.is_window_created:
        cv2.destroyWindow(virtual_kb.window_name)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()