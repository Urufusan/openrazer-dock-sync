# Razer Mouse Dock Chroma battery level indicator

This daemon uses OpenRazer to make the dock reflect the current battery level of your mouse

This is supposed to be a POC, because my end-goal is to have this feature implemented into Polychromatic!

# HOWTO

Just run the main script, and change the ``MOUSE_NAME`` const string to that of your mouse's name (if it's not a Naga Pro)

# NOTES

You can change the color gradient that maps different battery levels by changing ``GRADIENT``

Polling time can be changed by the ``RZR_SLEEPFOR`` env var;

e.g. ``[user@machine $ ~] RZR_SLEEPFOR=100 python3 razrdocksync.py`` to poll every 100 seconds
