# Generate bindings helper shell script

AVPY_BUILDS=~/dev/Avpy_builds
LIBAV08_CONFIG=config/libav08.yml
LIBAV9_CONFIG=config/libav9.yml
LIBAV10_CONFIG=config/libav10.yml
LIBAV11_CONFIG=config/libav11.yml
FFMPEG12_CONFIG=config/ffmpeg12.yml
FFMPEG25_CONFIG=config/ffmpeg25.yml
FFMPEG26_CONFIG=config/ffmpeg26.yml
FFMPEG27_CONFIG=config/ffmpeg27.yml
FFMPEG28_CONFIG=config/ffmpeg28.yml

python gen.py -l libav -v 0.8.1 -b $AVPY_BUILDS && python fix.py -s av008.py -d av008_fix.py -c $LIBAV08_CONFIG && python genClean.py -s av008_fix.py -d av8.py -c $LIBAV08_CONFIG && cp -v av8.py ../avpy/version/av8.py

python gen.py -l libav -v 9.1 -b $AVPY_BUILDS && python fix.py -s av091.py -d av009_fix.py -c $LIBAV9_CONFIG && python genClean.py -s av009_fix.py -d av9.py -c $LIBAV9_CONFIG && cp -v av9.py ../avpy/version/av9.py

python gen.py -l libav -v 10.1 -b $AVPY_BUILDS && python fix.py -s av101.py -d av101_fix.py -c $LIBAV10_CONFIG && python genClean.py -s av101_fix.py -d av10.py -c $LIBAV10_CONFIG && cp -v av10.py ../avpy/version/av10.py

python gen.py -l libav -v 11.1 -b $AVPY_BUILDS && python fix.py -s av111.py -d av111_fix.py -c $LIBAV11_CONFIG && python genClean.py -s av111_fix.py -d av11.py -c $LIBAV11_CONFIG && cp -v av11.py ../avpy/version/av11.py

python gen.py -l ffmpeg -v 1.2.1 -b $AVPY_BUILDS && python fix.py -s ff012.py -d ff012_fix.py -c $FFMPEG12_CONFIG && python genClean.py -s ff012_fix.py -d ff12.py -c $FFMPEG12_CONFIG && cp -v ff12.py ../avpy/version/ff12.py

python gen.py -l ffmpeg -v 2.5.1 -b $AVPY_BUILDS && python fix.py -s ff025.py -d ff025_fix.py -c $FFMPEG25_CONFIG && python genClean.py -s ff025_fix.py -d ff25.py -c $FFMPEG25_CONFIG && cp -v ff25.py ../avpy/version/ff25.py

python gen.py -l ffmpeg -v 2.6.1 -b $AVPY_BUILDS && python fix.py -s ff026.py -d ff026_fix.py -c $FFMPEG26_CONFIG && python genClean.py -s ff026_fix.py -d ff26.py -c $FFMPEG26_CONFIG && cp -v ff26.py ../avpy/version/ff26.py

python gen.py -l ffmpeg -v 2.7.1 -b $AVPY_BUILDS && python fix.py -s ff027.py -d ff027_fix.py -c $FFMPEG27_CONFIG && python genClean.py -s ff027_fix.py -d ff27.py -c $FFMPEG27_CONFIG && cp -v ff27.py ../avpy/version/ff27.py

python gen.py -l ffmpeg -v 2.8.1 -b $AVPY_BUILDS && python fix.py -s ff028.py -d ff028_fix.py -c $FFMPEG28_CONFIG && python genClean.py -s ff028_fix.py -d ff28.py -c $FFMPEG28_CONFIG && cp -v ff28.py ../avpy/version/ff28.py

