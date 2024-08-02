@echo off

:model_choice
echo Choose model (1-3):
echo 1. homography
echo 2. translation
echo 3. affine
set /p model_choice="Your choice: "
if "%model_choice%"=="1" set model=homography
if "%model_choice%"=="2" set model=translation
if "%model_choice%"=="3" set model=affine
if "%model_choice%"=="" set model=

:mode_choice
echo Choose mode (1-2):
echo 1. raw
echo 2. saliency_sif
set /p mode_choice="Your choice: "
if "%mode_choice%"=="1" set mode=raw
if "%mode_choice%"=="2" set mode=saliency_sift
if "%mode_choice%"=="" set mode=

:fixbg_choice
echo Choose the option to fix the background (1-4):
echo 1. no
echo 2. saliency
echo 3. rgb_stddev
echo 4. hsv_stddev
set /p fixbg_choice="Your choice: "
if "%fixbg_choice%"=="1" set fixbg=no
if "%fixbg_choice%"=="2" set fixbg=saliency
if "%fixbg_choice%"=="3" set fixbg=rgb_stddev
if "%fixbg_choice%"=="4" set fixbg=hsv_stddev
if "%fixbg_choice%"=="" set fixbg=

set cmd=py live_photo.py
if not "%model%"=="" set cmd=%cmd% --model %model%
if not "%mode%"=="" set cmd=%cmd% --mode %mode%
if not "%fixbg%"=="" set cmd=%cmd% --fixbg %fixbg%

%cmd%