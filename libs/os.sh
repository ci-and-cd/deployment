#!/usr/bin/env bash

function os_codename() {
    local codename="unknown"
    if [ "$(os_kernel_name)" == "linux" ] && type -p /usr/bin/lsb_release > /dev/null; then
        # i.e. xenial
        codename=$(lsb_release -cs)
    elif [ "$(os_kernel_name)" == "darwin" ]; then
        # no simple way to find out codename via shell command line, use version instead
        codename=$(sw_vers -productVersion)
    fi
    echo "${codename}"
}

function os_description() {
    local description="unknown"
    if [ "$(os_kernel_name)" == "linux" ] && type -p /usr/bin/lsb_release > /dev/null; then
        # i.e. Ubuntu
        description=$(lsb_release -is)
    elif [ "$(os_kernel_name)" == "darwin" ]; then
        description="OSX"
    fi
    echo "${description}"
}

function os_kernel_name() {
    uname -s | tr '[:upper:]' '[:lower:]'
}

function os_version() {
    local version=""
    if [ "$(os_kernel_name)" == "linux" ] && type -p /usr/bin/lsb_release > /dev/null; then
        # i.e. 16.04
        version=$(lsb_release -rs)
    elif [ "$(os_kernel_name)" == "darwin" ]; then
        # i.e. 10.13.5
        version=$(sw_vers -productVersion)
    else
        # linux kernel version
        version=$(uname -mrs | awk '{print $2}')
    fi
    echo "${version}"
}
