#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper launcher script to open FreeCAD GUI with FreshVend_Machine_3D.FCStd
"""
import subprocess
import os

freecad_exe = r"E:\programs\bin\freecad.exe"
project_file = os.path.abspath(r"cad\FreshVend_Machine_3D.FCStd")

if os.path.exists(freecad_exe) and os.path.exists(project_file):
    print(f"Opening FreeCAD with {project_file}...")
    subprocess.Popen([freecad_exe, project_file])
    print("\n[HƯỚNG DẪN XEM CHUYỂN ĐỘNG TRONG FREECAD]:")
    print("1. Sau khi FreeCAD mở file 'FreshVend_Machine_3D.FCStd'")
    print("2. Trên thanh menu, chọn: Macro -> Macros... (hoặc phím tắt)")
    print("3. Chọn 'simulate_dual_iris_dispense.FCMacro' và bấm 'Execute'")
    print("4. Hộp thoại điều khiển chuyển động sẽ hiện ra:")
    print("   - Bấm 'CHẠY CHU TRÌNH ĐẦY ĐỦ (AUTO FIFO)' để xem toàn bộ chuyển động tự động.")
    print("   - Hoặc bấm từng bước 1 -> 5 để quan sát chi tiết cơ chế kẹp nhả và cảm biến IR!")
else:
    print(f"Error: Could not locate {freecad_exe} or {project_file}")
