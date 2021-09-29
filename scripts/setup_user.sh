#!/usr/bin/env bash

existing_user=$(id -nu 1000 2>/dev/null)
if [[ -z "${existing_user}" ]]; then
    # Add an application user
    useradd --uid 1000 --system --gid 0 --create-home --shell /bin/bash appuser
else
    # Change user name to appuser
    usermod -l appuser "${existing_user}"

    # Add user to root group
    gpasswd -a appuser root
fi
