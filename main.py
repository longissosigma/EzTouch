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
    is_system_active = True       # Trạng thái đóng băng/hoạt động của chuột
    calibration_start = time.time()
    is_calibrated = False
    
    # Biến tích lũy mẫu để tính trung bình động cho Calibration
    calib_center_samples = []
    calib_mouth_samples = []

    # Quản lý thời gian của cử chỉ Đầu và Miệng
    mouth_open_start_time = None
    left_tilt_start_time = None
    right_tilt_start_time = None
    
    # Trạng thái UI
    ui_flash_trigger = 0
    ui_status_text = "DANG CAN CHINH (NHIN THANG & HA MOM TO MAX)..."

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
        # GIAI ĐOẠN 1: AUTO-CALIBRATION (5 GIÂY ĐẦU)
        # ==========================================
        if not is_calibrated:
            elapsed_calib = current_time - calibration_start
            countdown = int(5 - elapsed_calib)
            
            if nose_x is not None and nose_y is not None:
                calib_center_samples.append((nose_x, nose_y))
                calib_mouth_samples.append(mouth_ratio)

            # Vẽ màn hình chào mừng Calibration hiện đại
            cv2.rectangle(overlay, (0, 0), (w, h), (30, 30, 30), -1)
            cv2.putText(frame, "CHAO MUNG BAN DEN VOI FACILETOUCH", (w // 2 - 190, h // 2 - 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 127), 2, cv2.LINE_AA)
            cv2.putText(frame, "NHIN THANG vA HA MIENG TO NHAT TRONG: " + str(countdown) + "s", (w // 2 - 240, h // 2 - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            
            # Khởi tạo thanh progress đếm ngược
            cv2.rectangle(overlay, (150, h // 2 + 20), (150 + int(elapsed_calib * 68), h // 2 + 35), (0, 255, 127), -1)

            if elapsed_calib >= 5.0:
                # Tính toán lại thông số động dựa trên cơ địa người dùng
                avg_x = np.mean([p[0] for p in calib_center_samples])
                avg_y = np.mean([p[1] for p in calib_center_samples])
                max_mouth = np.max(calib_mouth_samples) if calib_mouth_samples else 0.15
                
                config.CALIBRATED_CENTER_X = avg_x
                config.CALIBRATED_CENTER_Y = avg_y
                # Ngưỡng kích hoạt động bằng 50% mức há lớn nhất thu thập được
                config.DYNAMIC_MOUTH_THRESH = max(0.04, max_mouth * 0.50)
                
                # Cập nhật lại biên an toàn bao quanh tâm mới
                config.FRAME_INNER_X1 = avg_x - 0.15
                config.FRAME_INNER_X2 = avg_x + 0.15
                config.FRAME_INNER_Y1 = avg_y - 0.15
                config.FRAME_INNER_Y2 = avg_y + 0.15
                
                is_calibrated = True
                ui_status_text = "HETHONG SAN SANG"
            
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
            cv2.imshow("Head Mouse Accessibility Dashboard", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            continue

        # ==========================================
        # GIAI ĐOẠN 2: ĐIỀU KHIỂN CHÍNH (MAIN LOOP)
        # ==========================================
        if nose_x is not None and nose_y is not None:
            # 1. KIỂM TRA CƠ CHẾ ĐÓNG BĂNG/KÍCH HOẠT CHUỘT (NGHIÊNG ĐẦU 3 GIÂY)
            # Sau khi flip gương: Nghiêng đầu sang TRÁI thực tế sẽ sinh ra góc Roll mang dấu ÂM
            if head_roll < config.ROLL_THRESHOLD_RIGHT: 
                if left_tilt_start_time is None: 
                    left_tilt_start_time = current_time
                
                elapsed_tilt = current_time - left_tilt_start_time
                ui_status_text = f"GIU NGHIENG TRAI DE KHOA... ({config.LOCK_HOLD_DURATION - elapsed_tilt:.1f}s)"
                
                if elapsed_tilt >= config.LOCK_HOLD_DURATION:
                    if is_system_active:
                        is_system_active = False
                        ui_status_text = "CHUOT DA KHOA (PAUSED)"
                        ui_flash_trigger = 8
                        mouse_controller.end_drag() # Thả chuột an toàn
            else:
                left_tilt_start_time = None

            # Sau khi flip gương: Nghiêng đầu sang PHẢI thực tế sẽ sinh ra góc Roll mang dấu DƯƠNG
            if head_roll > config.ROLL_THRESHOLD_LEFT:
                if right_tilt_start_time is None: 
                    right_tilt_start_time = current_time
                
                elapsed_tilt = current_time - right_tilt_start_time
                ui_status_text = f"GIU NGHIENG PHAI DE MO... ({config.LOCK_HOLD_DURATION - elapsed_tilt:.1f}s)"
                
                if elapsed_tilt >= config.LOCK_HOLD_DURATION:
                    if not is_system_active:
                        is_system_active = True
                        ui_status_text = "CHUOT HOAT DONG"
                        ui_flash_trigger = 8
            else:
                right_tilt_start_time = None

            # 2. XỬ LÝ DI CHUYỂN CHUỘT NẾU HỆ THỐNG ĐANG ACTIVE
            smooth_x, smooth_y = mouse_filter.update(nose_x, nose_y)
            if is_system_active:
                mouse_controller.move_to_smooth(smooth_x, smooth_y)
            
            # 🔴 ĐOẠN CODE VẼ HỒNG TÂM TRÊN CHÓP MŨI (ĐÃ ĐƯỢC ĐƯA TRỞ LẠI Ở ĐÂY)
            center_pt = (int(nose_x * w), int(nose_y * h))
            hud_color = (0, 255, 127) if is_system_active else (0, 0, 255) # Xanh neon nếu chạy, Đỏ nếu đang Pause
            cv2.circle(frame, center_pt, 6, hud_color, -1)     # Chấm tròn nhân bên trong
            cv2.circle(frame, center_pt, 14, (255, 255, 255), 2) # Vòng tròn mục tiêu bám đuổi bên ngoài

            # 3. LOGIC HÁ MỒM PHÂN CHIA THỜI GIAN (CLICK / DRAG & DROP)
            if is_system_active:
                if mouth_ratio > config.DYNAMIC_MOUTH_THRESH:
                    if mouth_open_start_time is None:
                        mouth_open_start_time = current_time
                    
                    if current_time - mouth_open_start_time >= config.DRAG_MIN_DURATION and not mouse_controller.is_dragging:
                        mouse_controller.start_drag()
                        ui_status_text = "DANG KEO THA (DRAGGING...)"
                else:
                    if mouth_open_start_time is not None:
                        duration = current_time - mouth_open_start_time
                        
                        if duration <= config.CLICK_MAX_DURATION:
                            mouse_controller.execute_click()
                            ui_status_text = "CLICK CHUOT TRAI"
                            ui_flash_trigger = 3
                        
                        if mouse_controller.is_dragging:
                            mouse_controller.end_drag()
                            ui_status_text = "DA THA CHUOT (RELEASED)"
                            ui_flash_trigger = 3
                            
                        mouth_open_start_time = None

        # ==========================================
        # GIAI ĐOẠN 3: ĐỒ HỌA HUD HIỂN THỊ (UX UI)
        # ==========================================
        # 1. Khung tương tác an toàn đã được hiệu chỉnh tự động
        x1, y1 = int(config.FRAME_INNER_X1 * w), int(config.FRAME_INNER_Y1 * h)
        x2, y2 = int(config.FRAME_INNER_X2 * w), int(config.FRAME_INNER_Y2 * h)
        box_color = (255, 255, 255) if is_system_active else (0, 0, 150)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), box_color, 2)
        cv2.putText(frame, "VUNG TUONG TAC AN TOAN", (x1 + 5, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, box_color, 1, cv2.LINE_AA)

        # 2. Thanh đo tiến trình há mồm động bên phải màn hình
        bar_x1, bar_y1 = w - 45, h - 230
        bar_x2, bar_y2 = w - 20, h - 40
        cv2.rectangle(overlay, (bar_x1, bar_y1), (bar_x2, bar_y2), (40, 40, 40), -1)
        
        max_exp = config.DYNAMIC_MOUTH_THRESH * 2.5
        fill_level = int(np.interp(mouth_ratio, [0, max_exp], [0, 190]))
        fill_level = max(0, min(190, fill_level))
        thresh_y = bar_y2 - int(np.interp(config.DYNAMIC_MOUTH_THRESH, [0, max_exp], [0, 190]))
        
        bar_color = (0, 0, 255) if mouse_controller.is_dragging else ((0, 255, 127) if mouth_ratio > config.DYNAMIC_MOUTH_THRESH else (255, 200, 0))
        cv2.rectangle(overlay, (bar_x1, bar_y2 - fill_level), (bar_x2, bar_y2), bar_color, -1)
        cv2.line(overlay, (bar_x1 - 5, thresh_y), (bar_x2 + 5, thresh_y), (0, 165, 255), 2)
        
        # 3. Panel thanh trạng thái HUD phía góc dưới
        cv2.rectangle(overlay, (15, h - 35), (320, h - 10), (20, 20, 20), -1)
        cv2.putText(frame, f"STATUS: {ui_status_text}", (20, h - 18), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
        
        # 4. Hiển thị thông số góc nghiêng đầu để giám khảo dễ quan sát
        cv2.putText(frame, f"Roll: {head_roll:.1f} deg", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        # Hiệu ứng Flash lóe sáng UI khi thực hiện thành công các Action
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