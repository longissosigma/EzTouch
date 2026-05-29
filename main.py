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

    # --- BIẾN QUẢN LÝ TIẾN TRÌNH ---
    is_mode_selected = False       # Giai đoạn 0: Đợi người dùng nghiêng đầu chọn chế độ
    is_calibrated = False          # Giai đoạn 1: 🌟 Đợi chốt tâm động vững chắc 4 giây
    is_system_active = True       
    
    calibration_start = None
    calib_mouth_samples = []

    # Quản lý thời gian của cử chỉ Miệng
    mouth_open_start_time = None
    mouth_frame_counter = 0
    REQUIRED_SUSTAINED_FRAMES = 2 

    # Biến quản lý tính năng cuộn chuột dọc
    scroll_anchor_y = None  

    # Quản lý thời gian của các tính năng tự động khóa
    face_last_seen_time = time.time()  
    hot_corner_start_time = None       
    resume_mouth_start_time = None     
    is_paused_by_absence = False       

    # --- BIẾN THEO DÕI THỜI GIAN NGHIÊNG ĐẦU CHỌN CHE DO ---
    tilt_start_time = None
    pending_mode = None

    # --- 🌟 BIẾN QUẢN LÝ AUTO-CENTER TÂM MŨI ĐỘNG 4 GIÂY ---
    stable_center_start_time = None
    last_stable_nose_x = 0.5
    last_stable_nose_y = 0.5

    # Trạng thái UI
    ui_flash_trigger = 0
    ui_status_text = "CHO CHON CHE DO..."

    while True:
        success, frame = cap.read()
        if not success: break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        overlay = frame.copy()

        results = detector.process_frame(frame)
        nose_x, nose_y = detector.get_nose_position(results)
        mouth_ratio = detector.get_mouth_open_ratio(results)
        head_roll = detector.get_head_roll(results) 

        current_time = time.time()

        # ==========================================
        # GIAI ĐOẠN 0: CHỌN CHẾ ĐỘ BẰNG CÁCH NGHIÊNG TRÁI / PHẢI 2 GIÂY
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
                        config.MOUSE_LERP_BASE_ALPHA = 0.25 
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
                        config.MOUSE_LERP_BASE_ALPHA = 0.60 
                        config.FILTER_MIN_CUTOFF = 0.30      
                        is_mode_selected = True
                        calibration_start = time.time()
                
                else:
                    tilt_start_time = None
                    pending_mode = None
                    ui_status_text = "HAY NGHIENG DAU DE CHON CHE DO"

            # Giao diện HUD khảo sát bằng cơ chế nghiêng đầu
            cv2.rectangle(overlay, (0, 0), (w, h), (25, 25, 25), -1)
            cv2.putText(frame, "KHAO SAT HE THONG FACILETOUCH", (w // 2 - 170, h // 2 - 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, "BAN CO TIEN SU BI CAC VAN DE VE RUN KHONG?", (w // 2 - 250, h // 2 - 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 127), 1, cv2.LINE_AA)
            cv2.putText(frame, f"Goc nghieng co: {head_roll:.1f} deg", (w // 2 - 100, h // 2 - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
            
            # 2 Bảng chỉ dẫn
            box_left_color = (0, 255, 127) if pending_mode == "PARKINSON" else (100, 100, 100)
            cv2.rectangle(overlay, (40, h // 2 + 30), (280, h // 2 + 90), box_left_color, 1 if pending_mode != "PARKINSON" else 2)
            cv2.putText(frame, "NGHIENG TRAI = CO", (85, h // 2 + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.45, box_left_color, 1, cv2.LINE_AA)
            cv2.putText(frame, "(Che do cho nguoi run)", (75, h // 2 + 75), cv2.FONT_HERSHEY_SIMPLEX, 0.35, box_left_color, 1, cv2.LINE_AA)
            
            box_right_color = (0, 165, 255) if pending_mode == "REGULAR" else (100, 100, 100)
            cv2.rectangle(overlay, (w - 280, h // 2 + 30), (w - 40, h // 2 + 90), box_right_color, 1 if pending_mode != "REGULAR" else 2)
            cv2.putText(frame, "NGHIENG PHAI = KHONG", (w - 240, h // 2 + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.45, box_right_color, 1, cv2.LINE_AA)
            cv2.putText(frame, "(Che do phan xa nhanh)", (w - 245, h // 2 + 75), cv2.FONT_HERSHEY_SIMPLEX, 0.35, box_right_color, 1, cv2.LINE_AA)
            
            cv2.rectangle(overlay, (15, h - 35), (420, h - 10), (20, 20, 20), -1)
            cv2.putText(frame, f"STATUS: {ui_status_text}", (20, h - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            cv2.imshow("Head Mouse Accessibility Dashboard", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            continue

        # ==========================================
        # 🌟 GIAI ĐOẠN 1: AUTO-CENTER TÌM TÂM ĐỘNG TRONG 4 GIÂY ĐỨNG IM
        # ==========================================
        if not is_calibrated:
            if nose_x is not None and nose_y is not None:
                calib_mouth_samples.append(mouth_ratio)
                
                # Kiểm tra xem mũi có đang đứng im tương đối trong một phạm vi nhỏ không
                if stable_center_start_time is None:
                    stable_center_start_time = current_time
                    last_stable_nose_x = nose_x
                    last_stable_nose_y = nose_y
                else:
                    # Nếu nhích đầu quá xa khỏi điểm đang giữ im, reset đếm ngược để tìm vị trí ngồi tĩnh mới
                    if abs(nose_x - last_stable_nose_x) > 0.025 or abs(nose_y - last_stable_nose_y) > 0.025:
                        stable_center_start_time = current_time
                        last_stable_nose_x = nose_x
                        last_stable_nose_y = nose_y

                elapsed_stable = current_time - stable_center_start_time
                countdown_stable = max(0.0, config.AUTOCENTER_STABLE_DURATION - elapsed_stable)
                
                # Vẽ màn hình chỉ dẫn chốt tâm động thông minh
                cv2.rectangle(overlay, (0, 0), (w, h), (30, 30, 30), -1)
                cv2.putText(frame, f"KICH HOAT: {config.CURRENT_MODE} MODE", (w // 2 - 140, h // 2 - 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 127), 1, cv2.LINE_AA)
                cv2.putText(frame, "GIU NGOI CO DINH THOAI MAI VA HA MOM MAX TRONG: " + f"{countdown_stable:.1f}s", (w // 2 - 290, h // 2 - 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
                
                # Vẽ hồng tâm động tại chính vị trí mũi người dùng đang ngồi để báo hiệu bám đuổi
                cv2.circle(frame, (int(nose_x * w), int(nose_y * h)), 15, (0, 165, 255), 2)
                
                # Thanh progress đếm ngược
                cv2.rectangle(overlay, (150, h // 2 + 20), (150 + int(elapsed_stable * 85), h // 2 + 35), (0, 255, 127), -1)

                if elapsed_stable >= config.AUTOCENTER_STABLE_DURATION:
                    # 🌟 CHỐT TÂM ĐỘNG THỰC TẾ: Lấy ngay vị trí người dùng đang ngồi làm trọng tâm
                    config.CALIBRATED_CENTER_X = last_stable_nose_x
                    config.CALIBRATED_CENTER_Y = last_stable_nose_y
                    
                    max_mouth = np.max(calib_mouth_samples) if calib_mouth_samples else 0.15
                    config.DYNAMIC_MOUTH_THRESH = max(0.04, max_mouth * 0.30)
                    
                    # 🌟 VÙNG AN TOÀN TO LÊN (MỞ BIÊN TỪ 0.22 LÊN ĐỘNG 0.25): Tạo không gian bao bọc quanh tâm thực tế rộng rãi
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
        # TÍNH NĂNG: XỬ LÝ BỊ ĐỘNG (MẤT DẤU KHUÔN MẶT)
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

        # ==========================================
        # GIAI ĐOẠN 2: ĐIỀU KHIỂN CHÍNH (MAIN LOOP)
        # ==========================================
        if nose_x is not None and nose_y is not None:
            
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

            smooth_x, smooth_y = mouse_filter.update(nose_x, nose_y)
            
            if is_system_active and not mouse_controller.is_scroll_mode:
                mouse_controller.move_to_smooth(smooth_x, smooth_y)
            
            if is_system_active and mouse_controller.is_scroll_mode and scroll_anchor_y is not None:
                mouse_controller.execute_scroll(scroll_anchor_y, smooth_y)
            
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
            
            center_pt = (int(nose_x * w), int(nose_y * h))
            if mouse_controller.is_scroll_mode:
                hud_color = (255, 0, 127) 
            else:
                hud_color = (0, 255, 127) if is_system_active else (0, 0, 255) 
            cv2.circle(frame, center_pt, 6, hud_color, -1)     
            cv2.circle(frame, center_pt, 14, (255, 255, 255), 2) 

            if is_system_active:
                if mouth_ratio > config.DYNAMIC_MOUTH_THRESH:
                    mouth_frame_counter += 1
                    
                    if mouth_frame_counter >= REQUIRED_SUSTAINED_FRAMES:
                        if mouth_open_start_time is None:
                            mouth_open_start_time = current_time - (REQUIRED_SUSTAINED_FRAMES / config.FILTER_FREQ)
                        
                        if current_time - mouth_open_start_time >= config.DRAG_MIN_DURATION and not mouse_controller.is_scroll_mode:
                            mouse_controller.is_scroll_mode = True
                            scroll_anchor_y = smooth_y 
                            ui_status_text = "CHEDO: CUON CHUOT DOC..."
                else:
                    if mouth_open_start_time is not None:
                        duration = current_time - mouth_open_start_time
                        
                        if duration <= config.CLICK_MAX_DURATION and not mouse_controller.is_scroll_mode:
                            mouse_controller.execute_click()
                            ui_status_text = "CLICK CHUOT TRAI"
                            ui_flash_trigger = 3
                        
                        if mouse_controller.is_scroll_mode:
                            mouse_controller.is_scroll_mode = False
                            scroll_anchor_y = None
                            ui_status_text = "THOAT CHEDO CUON CHUOT"
                            ui_flash_trigger = 3
                            
                        mouth_open_start_time = None
                    mouth_frame_counter = 0 

        # ==========================================
        # GIAI ĐOẠN 3: ĐỒ HỌA HUD HIỂN THỊ (UX UI)
        # ==========================================
        # Khung an toàn động bao bọc linh hoạt quanh vị trí ngồi thực tế của người dùng
        x1 = int(max(0.0, config.FRAME_INNER_X1) * w)
        y1 = int(max(0.0, config.FRAME_INNER_Y1) * h)
        x2 = int(min(1.0, config.FRAME_INNER_X2) * w)
        y2 = int(min(1.0, config.FRAME_INNER_Y2) * h)
        
        box_color = (255, 255, 255) if is_system_active else (0, 0, 150)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), box_color, 2)
        cv2.putText(frame, f"VUNG AN TOAN DI DONG ({config.CURRENT_MODE})", (x1 + 5, y1 - -15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, box_color, 1, cv2.LINE_AA)

        bar_x1, bar_y1 = w - 45, h - 230
        bar_x2, bar_y2 = w - 20, h - 40
        cv2.rectangle(overlay, (bar_x1, bar_y1), (bar_x2, bar_y2), (40, 40, 40), -1)
        
        max_exp = config.DYNAMIC_MOUTH_THRESH * 2.5
        fill_level = int(np.interp(mouth_ratio, [0, max_exp], [0, 190]))
        fill_level = max(0, min(190, fill_level))
        thresh_y = bar_y2 - int(np.interp(config.DYNAMIC_MOUTH_THRESH, [0, max_exp], [0, 190]))
        
        bar_color = (255, 0, 127) if mouse_controller.is_scroll_mode else ((0, 255, 127) if mouth_ratio > config.DYNAMIC_MOUTH_THRESH else (255, 200, 0))
        cv2.rectangle(overlay, (bar_x1, bar_y2 - fill_level), (bar_x2, bar_y2), bar_color, -1)
        cv2.line(overlay, (bar_x1 - 5, thresh_y), (bar_x2 + 5, thresh_y), (0, 165, 255), 2)
        
        cv2.rectangle(overlay, (15, h - 35), (420, h - 10), (20, 20, 20), -1)
        cv2.putText(frame, f"STATUS: {ui_status_text}", (20, h - 18), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
        
        if is_system_active:
            import pyautogui as pg
            mx, my = pg.position()
            cv2.putText(frame, f"Mouse Pixel: X={mx} Y={my}", (20, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

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