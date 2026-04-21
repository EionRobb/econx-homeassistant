# Econx Home Assistant Custom Component

A Home Assistant custom component for use with the [Econx](https://www.econx.co.nz/) system.

## Installation

### Install using HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eionrobb&repository=econx-homeassistant&category=integration)

1. Click the link above or look up 'Econx' in HACS integrations
2. Click 'Download', leave the version be and click 'Download' again.
3. Restart Home Assistant

### Install manually

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `econx`.
4. Download all the files from the `custom_components/econx/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant and clear your browser cache

### Next Steps

Navigate to `Settings` -> `Devices & Services` -> `Add Integration` -> `Econx` and follow the prompts to sign in with your email and password.
