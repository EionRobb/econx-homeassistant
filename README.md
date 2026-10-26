# Econx Home Assistant Custom Component

A Home Assistant custom component for use with the [Econx](https://www.econx.co.nz/) system.

Connect your Econx account to read device status and control lights, switches,
garage doors, and compatible infrared heat pumps. This integration uses the
Econx cloud API and requires an internet connection and an existing Econx account.
It is intended for Econx installations in New Zealand.

## Installation

### Install using HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eionrobb&repository=econx-homeassistant&category=integration)

Until this repository is included in the default HACS catalogue, add
`https://github.com/EionRobb/econx-homeassistant` under **HACS → Custom repositories**
with the category **Integration**.

1. Click the link above or open the added Econx repository in HACS.
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

## Supported devices

- Lights and pendants exposed through Econx relays or miscellaneous devices (on/off).
- Other relays and miscellaneous devices exposed as switches.
- Devices with "door" in their name exposed as garage door covers.
- Infrared devices identified as heat pumps, with power, mode, and target temperature control.

Device names determine whether relays and miscellaneous devices appear as lights,
switches, or covers. Device status is polled every 30 seconds.

## Troubleshooting

Check that your credentials work with the Econx service and that the service is
available. Commands rejected by Econx report a PIN or security restriction error;
entering a device PIN in Home Assistant is not currently supported.

For bugs, [open an issue](https://github.com/EionRobb/econx-homeassistant/issues)
with your Home Assistant and integration versions, the affected device type, and
relevant logs. Remove account details, passwords, tokens, and PINs before sharing logs.
