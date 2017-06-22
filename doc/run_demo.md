Install EPICS

    sudo apt-get install build-essential libreadline-dev
    wget -q https://www.aps.anl.gov/epics/download/base/base-3.15.5.tar.gz
    tar xf base-3.15.5.tar.gz && cd base-3.15.5 && make -s

Install Asyn

    wget -q https://www.aps.anl.gov/epics/download/modules/asyn4-31.tar.gz
    tar xf asyn4-31.tar.gz && cd asyn4-31 && echo EPICS_BASE=$HOME/base-3.15.5 > configure/RELEASE && make -s

Pre-step for RHEL users that don't override the default install location

    echo "/usr/local/lib" > /etc/ld.so.conf.d/local.conf

Install NDS3

    git clone https://github.com/cosylab/nds3
    cd nds3
    mkdir build
    cd build
    cmake ../CMake
    make install
    ldconfig

Install NDS3 Demo Drivers

    cd nds3/doc/examples
    mkdir build
    cd build
    cmake ../CMake
    make install

Build Demo IOC.

    git clone https://github.com/cosylab/nds3_epics
    cd nds3_epics
    echo -e "EPICS_BASE=$HOME/base-3.15.5\nASYN=$HOME/asyn4-31" > configure/RELEASE.local
    make

Run Demo IOC

    cd iocBoot/iocdemo
    ../../bin/linux-x86_64/demo st.cmd

    cd iocBoot/iocdemo2
    ../../bin/linux-x86_64/demo2 st.cmd
