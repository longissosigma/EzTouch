# FacileTouch - Head Mouse Accessibility Tool

Ứng dụng hỗ trợ công nghệ (Accessibility) giúp người khuyết tật vận động hoặc người mắc hội chứng Parkinson có thể điều khiển chuột máy tính thông qua cử động mặt và ánh mắt.

## Tính năng nổi bật
- **Auto-Calibration:** Tự động hiệu chỉnh tâm điều khiển và ngưỡng há mồm động theo cơ địa từng người.
- **Adaptive Smooth Filter:** Tích hợp bộ lọc One Euro Filter kết hợp LERP động giúp con trỏ chuột ghìm chắc chắn, triệt tiêu hoàn toàn hiện tượng rung lắc (Jitter).
- **Mouse Acceleration:** Hệ số tăng tốc thông minh giúp nhích nhẹ đầu chuột đã có thể lướt ra kịch biên màn hình.
- **Smart Actions:** Phân biệt cử chỉ há mồm nhanh để Click đơn và há mồm lâu để Kéo thả (Drag & Drop).
- **Physical Hot Corner & Absence Lock:** Tự động khóa chuột (Pause) khi đưa chuột về góc màn hình (0,0) trong 3 giây hoặc khi người dùng rời khỏi camera. Há mồm 3 giây để kích hoạt lại (Resume).
- Há mồm/lè lưỡi = click 
- Há mồm 3s = kéo thả, bôi 

## Yêu cầu hệ thống
- Python 3.x
- OpenCV, MediaPipe, PyAutoGUI, NumPy