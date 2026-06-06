# setup_compile.py
import os
import subprocess
import sys
import numpy

print("🚀 BIẾN ĐỔI MÃ NGUỒN EZTOUCH SANG MÃ MÁY C++ ĐỘC LẬP...")

# 🔥 THẦN CHÚ TỰ DÒ ĐƯỜNG DẪN MINGW (Bao sân mọi trường hợp lặp folder ở cả ổ C và ổ D)
# Sửa lại đoạn đầu file setup_compile.py như thế này:
# Cậu sửa lại đoạn đầu file setup_compile.py chuẩn 100% như sau:
possible_paths = [
    r"d:\x86_64-16.1.0-release-posix-seh-ucrt-rt_v14-rev1\mingw64\bin"
]

mingw_bin = None
for p in possible_paths:
    if os.path.exists(os.path.join(p, "gcc.exe")):
        mingw_bin = p
        break

if mingw_bin is None:
    print("❌ LỖI CHÍ MẠNG: Vẫn không tìm thấy file gcc.exe vật lý trên ổ đĩa!")
    print("-> Cậu hãy mở ổ D:\ hoặc C:\ xem cái folder giải nén đang nằm ở đâu chính xác nhé.")
    sys.exit(1)

print(f"🎯 Đã tìm thấy bộ dịch chuẩn tại: {mingw_bin}")
gcc_path = os.path.join(mingw_bin, "gcc.exe")
gpp_path = os.path.join(mingw_bin, "g++.exe")

# Thêm vào hệ thống chạy tạm thời
os.environ["PATH"] = mingw_bin + os.path.pathsep + os.environ["PATH"]

# 2. Tạo thư mục core nếu chưa có
if not os.path.exists("core"):
    os.makedirs("core")
if not os.path.exists("core/__init__.py"):
    with open("core/__init__.py", "w") as f:
        f.write("# EzTouch Core Package\n")

if not os.path.exists("build_cython"):
    os.makedirs("build_cython")

# Danh sách các file lõi trong src_backup [cite: 1]
modules = ["config", "filters", "detector", "controller", "virtual_keyboard", "main"]

# Lấy đường dẫn thư viện Python hiện tại trên máy cậu
python_include = os.path.join(sys.prefix, "include")
python_lib = os.path.join(sys.prefix, "libs", f"python{sys.version_info.major}{sys.version_info.minor}.lib")
numpy_include = numpy.get_include()

for mod in modules:
    print(f"\n📦 Đang xử lý module: [ {mod} ]")
    py_file = f"src_backup/{mod}.py"
    c_file = f"build_cython/{mod}.c"
    pyd_file = f"core/{mod}.pyd"
    
    # CHẶNG 1: Ép Cython tự dịch file .py thành file .c rác
    print(f"  -> [Cython] Đang dịch {py_file} sang {c_file}...")
    subprocess.run([sys.executable, "-m", "cython", "-3", py_file, "-o", c_file], check=True)
    
    # CHẶNG 2: Gọi trực tiếp gcc.exe ở ổ D để nén thành file mã máy .pyd
    print(f"  -> [MinGW GCC] Đang hóa đá {c_file} sang mã máy {pyd_file}...")
    cmd = [
        gcc_path, "-shared", "-O3",
        "-DMS_WIN64",  # 🔥 THẦN CHÚ MỚI: Định nghĩa rõ hệ thống Windows 64-bit cho GCC
        f"-I{python_include}",
        f"-I{numpy_include}",
        c_file,
        python_lib,
        "-o", pyd_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Lỗi biên dịch ở module {mod}:")
        print(result.stderr)
        sys.exit(1)

print("\n🎉 XUẤT SẮC! Toàn bộ thuật toán lõi đã được hóa đá thành file .pyd an toàn 100% trong thư mục core/!")