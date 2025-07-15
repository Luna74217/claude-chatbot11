#!/usr/bin/env python3
"""
파이썬 경로 및 버전 확인 스크립트
"""

import sys
import os
import subprocess

print("=== 파이썬 경로 및 버전 확인 ===\n")

# 1. 현재 파이썬 정보
print("1. 현재 실행 중인 파이썬:")
print(f"   실행 파일 경로: {sys.executable}")
print(f"   버전: {sys.version}")
print(f"   버전 정보: {sys.version_info}")

# 2. PATH에서 파이썬 찾기
print("\n2. PATH에서 파이썬 찾기:")
path_dirs = os.environ.get('PATH', '').split(os.pathsep)
python_found = []

for path_dir in path_dirs:
    if os.path.exists(path_dir):
        for file in os.listdir(path_dir):
            if file.lower().startswith('python'):
                full_path = os.path.join(path_dir, file)
                if os.path.isfile(full_path):
                    python_found.append(full_path)

if python_found:
    print("   발견된 파이썬 실행 파일들:")
    for i, path in enumerate(python_found, 1):
        print(f"   {i}. {path}")
else:
    print("   PATH에서 파이썬을 찾을 수 없습니다.")

# 3. 일반적인 설치 경로 확인
print("\n3. 일반적인 설치 경로 확인:")
common_paths = [
    r"C:\Python*",
    r"C:\Users\Administrator\AppData\Local\Programs\Python\Python*",
    r"C:\Program Files\Python*",
    r"C:\Program Files (x86)\Python*",
    r"C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\python*"
]

for pattern in common_paths:
    import glob
    matches = glob.glob(pattern)
    if matches:
        print(f"   {pattern}:")
        for match in matches:
            print(f"     - {match}")

# 4. pip 경로 확인
print("\n4. pip 경로 확인:")
try:
    result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                          capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print(f"   pip 버전: {result.stdout.strip()}")
    else:
        print(f"   pip 오류: {result.stderr}")
except Exception as e:
    print(f"   pip 확인 실패: {e}")

# 5. 환경 변수 확인
print("\n5. 환경 변수 확인:")
env_vars = ['PYTHONPATH', 'PYTHONHOME', 'PYTHONEXECUTABLE']
for var in env_vars:
    value = os.environ.get(var)
    if value:
        print(f"   {var}: {value}")
    else:
        print(f"   {var}: 설정되지 않음")

print("\n=== 확인 완료 ===") 