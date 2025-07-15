@echo off
echo === 메타 ARIA 의존성 설치 ===
echo.

echo 1. torch 설치 중...
python -m pip install torch==2.2.0
if %errorlevel% neq 0 (
    echo ❌ torch 설치 실패
) else (
    echo ✅ torch 설치 완료
)

echo.
echo 2. numpy 설치 중...
python -m pip install numpy==1.24.3
if %errorlevel% neq 0 (
    echo ❌ numpy 설치 실패
) else (
    echo ✅ numpy 설치 완료
)

echo.
echo 3. 설치 확인 중...
python -c "import torch; print('torch 버전:', torch.__version__)"
python -c "import numpy; print('numpy 버전:', numpy.__version__)"

echo.
echo 4. 메타 ARIA 테스트 중...
python -c "from meta_aria_persona_simple import SimpleMetaARIA; aria = SimpleMetaARIA(); print('메타 ARIA 생성 성공:', aria.name)"

echo.
echo === 설치 완료 ===
pause 