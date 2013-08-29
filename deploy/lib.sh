#!/bin/bash

function get_distro {
    if [[ -f /etc/arch-release ]]; then
        echo "arch"
    elif [[ -f /etc/lsb-release ]]; then
        echo "ubuntu"
    fi
}

function confirm {
	local message="$1"
	if [[ -z "$all" ]]; then
		read -p "$message? [Y/n/a] " answer
		if [[ -z "$answer" || "$answer" =~ ^[yYaA] ]]; then
			if [[ "$answer" =~ ^[aA] ]]; then
				all=1
			fi
		else
			exit 1
		fi
	else
		echo "Executing $message..."
	fi
}

function require_python_packages {
    local necessary_packages="$@"
	pipfreeze=$(pip freeze)
    to_install=""
    for package in $necessary_packages; do
        if [ -z "`echo \"$pipfreeze\" | grep ^$package=`" ]; then
            to_install="$to_install $package"
        fi
    done
    if [ "$to_install" ]; then
        for package in $to_install; do
            install_command="pip install $package"
            confirm "$install_command"
            $install_command || exit 1
        done
    fi
}

function require {
	local command="$1"
	local toinstall="$2"

	type -P $command &>/dev/null || ls $command &>/dev/null || [ "$toinstall" == "" ] || {
		echo "$command missing" >&2
		confirm "$toinstall"
		$toinstall || exit 1
	}
}
