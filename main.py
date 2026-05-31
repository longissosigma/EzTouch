# Vòng lặp chính, kết nối các module lại với nhau

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

def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)

    detector = FaceDetector()
    mouse_filter = DualOneEuroFilter(freq=config.FILTER_FREQ, min_cutoff=config.FILTER_MIN_CUTOFF, beta=config.FILTER_BETA)
    mouse_controller = MouseController()

    is_mode_selected = False       
    is_calibrated = False          
    is_system_active = True       
    
    calibration_start = None
    calib_mouth_samples = []

    # 🌟 XÓA BỎ BỘ ĐẾM KHUNG HÌNH - CHUYỂN SANG QUẢN LÝ THỜI GIAN THỰC TUYỆT ĐỐI
    mouth_open_start_time = None

    scroll_anchor_y = None  

    face_last_seen_time = time.time()  
    hot_corner_start_time = None       
    resume_mouth_start_time = None     
    is_paused_by_absence = False       

    tilt_start_time = None
    pending_mode = None

    stable_center_start_time = None
    last_stable_nose_x = 0.5
    last_stable_nose_y = 0.5

    ui_flash_trigger = 0
    ui_status_text = "CHO CHON CHE DO..."

    while True:
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

        # ==========================================
        # GIAI ĐOẠN 0: CHỌN CHẾ ĐỘ NGHIÊNG ĐẦU
        # ==========================================
        if not is_mode_selected:
            if head_roll is not None:
                if head_roll < config.ROLL_SELECT_LEFT:
                    if pending_mode != "PARKINSON":
                        pending_mode = "PARKINSON"
                        tilt_start_time = current_time
                    
                    elapsed_tilt = current_time - tilt_start_time
                    ui_status_text = f"DANG CHON PARKINSON... ({config.SELECT_HOLD_DURATION - elapsed_tilt:.1f}s)"
                    
                    if elapsed_tilt >= config.SELECT_HOLD_DURATION:
                        config.CURRENT_MODE = "PARKINSON"
                        config.FILTER_MIN_CUTOFF = 0.04      
                        is_mode_selected = True
                        calibration_start = time.time()
                
                elif head_roll > config.ROLL_SELECT_RIGHT:
                    if pending_mode != "REGULAR":
                        pending_mode = "REGULAR"
                        tilt_start_time = current_time
                    
                    elapsed_tilt = current_time - tilt_start_time
                    ui_status_text = f"DANG CHON SIEU TOC... ({config.SELECT_HOLD_DURATION - elapsed_tilt:.1f}s)"
                    
                    if elapsed_tilt >= config.SELECT_HOLD_DURATION:
                        config.CURRENT_MODE = "REGULAR"
                        config.FILTER_MIN_CUTOFF = 0.50      
                        is_mode_selected = True
                        calibration_start = time.time()
                
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
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            continue

        # ==========================================
        # GIAI ĐOẠN 1: AUTO-CENTER TỰ TÌM TÂM
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
                
                cv2.rectangle(overlay, (0, 0), (w, h), (30, 30, 30), -1)
                cv2.putText(frame, f"KICH HOAT: {config.CURRENT_MODE} MODE", (w // 2 - 180, h // 2 - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 127), 2, cv2.LINE_AA)
                cv2.putText(frame, "GIU NGOI CO DINH THOAI MAI VA HA MOM MAX TRONG: " + f"{countdown_stable:.1f}s", (w // 2 - 380, h // 2 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
                
                cv2.circle(frame, (int(raw_nose_x * w), int(raw_nose_y * h)), 18, (0, 165, 255), 2)
                cv2.rectangle(overlay, (w // 2 - 200, h // 2 + 30), (w // 2 - 200 + int(elapsed_stable * 100), h // 2 + 45), (0, 255, 127), -1)

                if elapsed_stable >= config.AUTOCENTER_STABLE_DURATION:
                    config.CALIBRATED_CENTER_X = last_stable_nose_x
                    config.CALIBRATED_CENTER_Y = last_stable_nose_y
                    
                    max_mouth = np.max(calib_mouth_samples) if calib_mouth_samples else 0.15
                    # Đặt ngưỡng kích hoạt động nhạy bén bằng 30% mốc há lớn nhất
                    config.DYNAMIC_MOUTH_THRESH = max(0.04, max_mouth * 0.30)
                    
                    config.FRAME_INNER_X1 = last_stable_nose_x - 0.25
                    config.FRAME_INNER_X2 = last_stable_nose_x + 0.25
                    config.FRAME_INNER_Y1 = last_stable_nose_y - 0.25
                    config.FRAME_INNER_Y2 = last_stable_nose_y + 0.25
                    
                    is_calibrated = True
                    ui_status_text = "HETHONG SAN SANG"
                    face_last_seen_time = time.time()
            
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
            cv2.imshow("Head Mouse Accessibility Dashboard", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            continue

        # ==========================================
        # GIAI ĐOẠN 2: LUỒNG ĐIỀU KHIỂN CHÍNH
        # ==========================================
        if results.multi_face_landmarks:
            face_last_seen_time = current_time  
            if is_paused_by_absence:
                is_system_active = True
                is_paused_by_absence = False
                ui_status_text = "WELCOME BACK! CHUOT HOAT DONG"
                ui_flash_trigger = 8
        else:
            if is_system_active and (current_time - face_last_seen_time >= config.FACE_ABSENCE_DURATION):
                is_system_active = False
                is_paused_by_absence = True  
                ui_status_text = "MAT NGUOI DUNG - TUDONG PAUSE"
                ui_flash_trigger = 8
                mouse_controller.is_scroll_mode = False
                scroll_anchor_y = None

        if raw_nose_x is not None and raw_nose_y is not None:
            # KIỂM TRA KHÓA/MỞ KHI HÁ MỒM (Hệ thống lock)
            if not is_system_active:
                if mouth_ratio > config.DYNAMIC_MOUTH_THRESH:
                    if resume_mouth_start_time is None:
                        resume_mouth_start_time = current_time
                    
                    elapsed_resume = current_time - resume_mouth_start_time
                    ui_status_text = f"HA MOM DE MO KHOA... ({config.RESUME_MOUTH_DURATION - elapsed_resume:.1f}s)"
                    
                    if elapsed_resume >= config.RESUME_MOUTH_DURATION:
                        is_system_active = True
                        is_paused_by_absence = False 
                        ui_status_text = "MO KHOA THANH CONG - CHUOT HOAT DONG"
                        ui_flash_trigger = 8
                        resume_mouth_start_time = None
                else:
                    resume_mouth_start_time = None

            # 🌟 XỬ LÝ CLICK/CUỘN THEO TIMING REALTIME (KHÔNG TRỄ KHUNG HÌNH)
            if is_system_active:
                if mouth_ratio > config.DYNAMIC_MOUTH_THRESH:
                    # Móng ngựa thời gian bắt đầu tính ngay khi vừa vượt ngưỡng
                    if mouth_open_start_time is None:
                        mouth_open_start_time = current_time
                    
                    # Nếu ngâm mồm mở quá mốc DRAG_MIN_DURATION -> Vào chế độ cuộn trang ngay lập tức
                    if (current_time - mouth_open_start_time >= config.DRAG_MIN_DURATION) and not mouse_controller.is_scroll_mode:
                        mouse_controller.is_scroll_mode = True
                        scroll_anchor_y = raw_nose_y 
                        ui_status_text = "CHEDO: CUON CHUOT DOC..."
                else:
                    # Khi người dùng đóng miệng lại -> Đo đạc mốc thời gian tĩnh để phát lệnh
                    if mouth_open_start_time is not None:
                        duration = current_time - mouth_open_start_time
                        
                        # Cú nhấp nhả nhanh hoàn hảo -> Bắn tín hiệu Click đơn ngay lập tức!
                        if duration <= config.CLICK_MAX_DURATION and not mouse_controller.is_scroll_mode:
                            mouse_controller.execute_click()
                            ui_status_text = "CLICK CHUOT TRAI TỨC THỜI"
                            ui_flash_trigger = 3
                        
                        if mouse_controller.is_scroll_mode:
                            mouse_controller.is_scroll_mode = False
                            scroll_anchor_y = None
                            ui_status_text = "THOAT CHEDO CUON CHUOT"
                            ui_flash_trigger = 3
                            
                        mouth_open_start_time = None

            # LUỒNG TỌA ĐỘ CHUỘT (Giữ nguyên vẹn toán học 1:1 không đổi của ông)
            smooth_x, smooth_y = mouse_filter.update(raw_nose_x, raw_nose_y)
            clamped_x = np.clip(smooth_x, config.FRAME_INNER_X1, config.FRAME_INNER_X2)
            clamped_y = np.clip(smooth_y, config.FRAME_INNER_Y1, config.FRAME_INNER_Y2)
            
            if is_system_active and not mouse_controller.is_scroll_mode:
                mouse_controller.move_to_smooth(clamped_x, clamped_y)
            
            if is_system_active and mouse_controller.is_scroll_mode and scroll_anchor_y is not None:
                mouse_controller.execute_scroll(scroll_anchor_y, smooth_y)
            
            # Hot corner vật lý góc (0,0)
            if is_system_active:
                import pyautogui as pg 
                current_mouse_x, current_mouse_y = pg.position()
                if (current_mouse_x <= 15) and (current_mouse_y <= 15):
                    if hot_corner_start_time is None:
                        hot_corner_start_time = current_time
                    elapsed_corner = current_time - hot_corner_start_time
                    ui_status_text = f"GIU GOC MAN HINH DE KHOA... ({config.HOT_CORNER_DURATION - elapsed_corner:.1f}s)"
                    if elapsed_corner >= config.HOT_CORNER_DURATION:
                        is_system_active = False
                        is_paused_by_absence = False
                        ui_status_text = "KHOA CHUOT BANG GOC MAN HINH (0,0)"
                        ui_flash_trigger = 8
                        mouse_controller.is_scroll_mode = False
                        scroll_anchor_y = None
                        hot_corner_start_time = None
                else:
                    hot_corner_start_time = None
            else:
                hot_corner_start_time = None
            
            # Đồ họa tâm xanh lá
            center_pt = (int(clamped_x * w), int(clamped_y * h))
            hud_color = (255, 0, 127) if mouse_controller.is_scroll_mode else ((0, 255, 127) if is_system_active else (0, 0, 255))
            cv2.circle(frame, center_pt, 6, hud_color, -1)     
            cv2.circle(frame, center_pt, 14, (255, 255, 255), 2) 
            
            real_nose_pt = (int(raw_nose_x * w), int(raw_nose_y * h))
            if real_nose_pt != center_pt:
                cv2.circle(frame, real_nose_pt, 4, (120, 120, 120), -1)

        # ==========================================
        # GIAI ĐOẠN 3: ĐỒ HỌA HUD
        # ==========================================
        x1 = int(max(0.0, config.FRAME_INNER_X1) * w)
        y1 = int(max(0.0, config.FRAME_INNER_Y1) * h)
        x2 = int(min(1.0, config.FRAME_INNER_X2) * w)
        y2 = int(min(1.0, config.FRAME_INNER_Y2) * h)
        
        box_color = (255, 255, 255) if is_system_active else (0, 0, 150)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), box_color, 2)
        cv2.putText(frame, f"VUNG AN TOAN QUY CHUAN ({config.CURRENT_MODE})", (x1 + 5, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, box_color, 1, cv2.LINE_AA)

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
        
        cv2.rectangle(overlay, (15, h - 45), (550, h - 15), (20, 20, 20), -1)
        cv2.putText(frame, f"STATUS: {ui_status_text}", (25, h - 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        
        if is_system_active:
            import pyautogui as pg
            mx, my = pg.position()
            cv2.putText(frame, f"Mouse Pixel: X={mx} Y={my}", (25, 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        if ui_flash_trigger > 0:
            flash = np.zeros_like(frame)
            flash[:] = (0, 255, 127) if is_system_active else (0, 0, 255)
            cv2.addWeighted(flash, 0.3, frame, 0.7, 0, frame)
            ui_flash_trigger -= 1

        cv2.imshow("Head Mouse Accessibility Dashboard", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()