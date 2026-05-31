# FacileTouch - Head Mouse Accessibility Tool

Ứng dụng hỗ trợ công nghệ (Accessibility) giúp người khuyết tật vận động hoặc người mắc hội chứng Parkinson có thể điều khiển chuột máy tính thông qua cử động mặt và ánh mắt.

## Tính năng nổi bật
- tính năng phân loại: lúc khởi chạy: nghiêng trái 2s = chế độ cho người bị run ( chuột chậm hơn vì có tính năng chống run). Nghiêng phải 2s = chế độ cho người ko bị run (chuột nhanh hơn)
- Tính năng adaptive: sau khi chọn chế độ người dùng giữ 1 ví trí cố định (tự chọn) trong 4 giây để xác định tâm và vẽ vùng an toàn (vùng hoạt động) 
- Há mồm = click
- Há mồm + giữ 3 giây = bật tính năng cuộn chuột. Trong lúc giữ nguyên trạng thái há mồm người dùng kéo mũi xuống = cuộn xuống, kéo mũi lên = cuộn lên
- Pause/Resume: 
(chủ động) kéo mũi lên góc trái trên cùng giữ đó khoảng 3 giây = pause. Há mồm 3s = resume
(bị động) người dùng biến mất = pause. Xuất hiện lại = resume

## Yêu cầu hệ thống
- Python 3.x
- OpenCV, MediaPipe, PyAutoGUI, NumPy

## Cập Nhật Mới
- camera quét to hơn
- đã fix độ nhạy của click và di chuyển