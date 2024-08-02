@echo off

:mode_choice
echo Choose mode (1-2):
echo 1. raw
echo 2. saliency_sift
set /p mode_choice="Your choice (or press Enter to skip): "
if "%mode_choice%"=="1" set mode=raw
if "%mode_choice%"=="2" set mode=saliency_sift
if "%mode_choice%"=="" set mode=

:model_choice
echo Choose model (1-3):
echo 1. homography
echo 2. translation
echo 3. affine
set /p model_choice="Your choice (or press Enter to skip): "
if "%model_choice%"=="1" set model=homography
if "%model_choice%"=="2" set model=translation
if "%model_choice%"=="3" set model=affine
if "%model_choice%"=="" set model=

set cmd=py motion_parallex.py
if not "%mode%"=="" set cmd=%cmd% --mode %mode%
if not "%model%"=="" set cmd=%cmd% --model %model%

%cmd%