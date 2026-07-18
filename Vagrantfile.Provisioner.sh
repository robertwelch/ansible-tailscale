#!/usr/bin/env bash

source /etc/os-release

timezone="America/Chicago"

majorversion=$(awk -F. '{print $1}' <<< "$(echo "$VERSION_ID")")

if command -v dnf &>/dev/null; then
    dnf --assumeyes remove --oldinstallonly --setopt installonly_limit=2 kernel
fi

if [[ -d /etc/ssh/sshd_config.d ]]; then
    if [[ $(find /etc/ssh/sshd_config.d -type f -name "*.conf" | wc -l) -gt 0 ]]; then
        echo "Remove sshd_config.d files..."
        find /etc/ssh/sshd_config.d -type f -name "*.conf" -exec rm '{}' \; -print
    fi
fi

if ! grep -q ^"PasswordAuthentication yes" /etc/ssh/sshd_config; then
    echo "Set PasswordAuthentication to yes..."
    if grep -q ^PasswordAuthentication /etc/ssh/sshd_config; then
        sed -i 's#PasswordAuthentication.*#PasswordAuthentication yes#g' /etc/ssh/sshd_config
    else
        echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
    fi
fi

if ! grep -q ^"UsePAM yes" /etc/ssh/sshd_config; then
    echo "Set UsePAM to yes..."
    if grep -q ^UsePAM /etc/ssh/sshd_config; then
        sed -i 's#UsePAM.*#UsePAM yes#g' /etc/ssh/sshd_config
    else
        echo "UsePAM yes" >> /etc/ssh/sshd_config
    fi
fi

[[ $majorversion -eq 8 ]] && python_version="python36 python3.9 python3.12"
[[ $majorversion -eq 9 ]] && python_version="python3.9 python3.12"
[[ $majorversion -gt 9 ]] && python_version="python3.12"
if command -v dnf &>/dev/null; then
    dnf --assumeyes --nogpgcheck install $python_version
fi

echo "Python version: $(python3 --version)"

echo "Set vagrant password..."
echo -e "vagrant\nvagrant" | passwd vagrant &>/dev/null

echo "Set root password..."
echo -e "vagrant\nvagrant" | passwd root &>/dev/null

if [[ "$(timedatectl show | awk -F= '$1=="Timezone" {print $NF}')" != "$timezone" ]]; then
    echo "Set timezone..."
    timedatectl set-timezone "$timezone"
fi

echo "Restart sshd..."
if [[ "$ID_LIKE" == "debian" ]]; then
    sshd -t && systemctl restart ssh
else
    sshd -t && systemctl restart sshd
fi
