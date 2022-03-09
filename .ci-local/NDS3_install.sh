#!/bin/bash 

# This script installs NDS3
# Use for mingw builds assumes that nds-core is a sub-module of nds-epics.

# check if user has right permissions
if [ "$(id -u)" != "0" ]; then
    echo "Sorry, you are not root. Please try again using sudo."
    exit 1
fi

# terminate script after first line that fails
set -e

pushd nds-core
chmod +x ./scripts/ci-build.sh

# NB, the EPICS cross build requires the native build first!
./scripts/ci-build.sh x86_64-linux
popd

# These files are created by the NDS build, wheras Linux builds install to a system folder.
if [ "$WINE" == "64" ]; then
    pushd nds-core
    ./scripts/ci-build.sh x86_64-w64-mingw32
    popd
    mkdir -p ./include
    cp -r ./nds-core/include/nds3/ ./include/
    mkdir -p ./lib/windows-x64-mingw
    mkdir -p ./bin/windows-x64-mingw
    cp ./nds-core/build/x86_64-w64-mingw32/libnds3.dll.a ./lib/windows-x64-mingw/
    cp ./nds-core/build/x86_64-w64-mingw32/libnds3.dll ./bin/windows-x64-mingw/
    cp ./nds-core/doc/examples/build/x86_64-w64-mingw32/liboscilloscope.dll.a ./lib/windows-x64-mingw/
    cp ./nds-core/doc/examples/build/x86_64-w64-mingw32/liboscilloscope.dll ./bin/windows-x64-mingw/
elif [ "$WINE" == "32" ]; then
    pushd nds-core
    ./scripts/ci-build.sh i686-w64-mingw32
    popd
    mkdir -p ./include
    cp -r ./nds-core/include/nds3/ ./include/
    mkdir -p ./lib/win32-x86-mingw
    mkdir -p ./bin/win32-x86-mingw
    cp ./nds-core/build/i686-w64-mingw32/libnds3.dll.a ./lib/win32-x86-mingw/
    cp ./nds-core/build/i686-w64-mingw32/libnds3.dll ./bin/win32-x86-mingw/
    cp ./nds-core/doc/examples/build/i686-w64-mingw32/liboscilloscope.dll.a ./lib/win32-x86-mingw/
    cp ./nds-core/doc/examples/build/i686-w64-mingw32/liboscilloscope.dll ./bin/win32-x86-mingw/
fi


