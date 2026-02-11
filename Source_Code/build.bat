@echo off
chcp 65001 >nul
echo ========================================
echo Terraria Auto-Installer - Build Script
echo ========================================
echo.

:: 1. Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден! Установите Python 3.8+ и добавьте в PATH.
    pause
    exit /b 1
)

:: 2. Установка зависимостей
echo [1/3] Установка библиотек...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Не удалось установить библиотеки.
    pause
    exit /b 1
)

:: 3. Проверка необходимых файлов
echo.
echo [2/3] Проверка файлов...
if not exist "terraria_installer.spec" (
    echo [ERROR] Файл terraria_installer.spec не найден!
    pause
    exit /b 1
)
if not exist "icon.ico" (
    echo [WARNING] Иконка icon.ico не найдена (будет стандартная).
)
if not exist "banner.jpg" (
    echo [ERROR] Баннер banner.jpg не найден! Интерфейс не запустится.
    pause
    exit /b 1
)

:: 4. Сборка EXE
echo.
echo [3/3] Сборка EXE через PyInstaller...
pyinstaller terraria_installer.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] Ошибка сборки! Смотрите лог выше.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] СБОРКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Ваш готовый файл находится здесь:
echo dist\Calamity_Ultra_Installer.exe
echo.
pause