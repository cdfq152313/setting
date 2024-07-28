def pycharm [] {
    bash -c "
        export DISPLAY=$(ip route show | grep default | awk '{print $3}'):0.0
        export PULSE_SERVER=tcp:$(ip route show | grep default | awk '{print $3}')
        ~/.local/share/JetBrains/Toolbox/scripts/pycharm </dev/null >/dev/null 2>/dev/null & disown
    "
}