# ulauncher-zoom

> 📹 Join a Zoom meeting quickly.

Quickly connect to a Zoom meeting using the meeting ID, and `xdg-open`.

## Install

### Requirements

- [Ulauncher 5](https://ulauncher.io/)
- Python >= 3

### Steps

1. Ulauncher > Preferences > Extensions > Add extension

2. Paste the following URL:

```
https://github.com/plibither8/ulauncher-zoom
```

3. Navigate to the `meetings.json` file and populate the JSON list with the meeting name, ID and password. Example:

```json
[
  {
    "name": "Personal Meeting",
    "id": "1234567890",
    "pwd": "ABC123"
  },
  {
    "name": "Engineering all-hands",
    "id": "3141592651",
    "pwd": "DEF456"
  }
]
```

You will find the `meetings.json` file where the Ulauncher extension has been downloaded. In most cases, look for it in: `~/.local/share/ulauncher/extensions/com.github.plibither8.ulauncher-zoom`.

## Usage

Default keyword to trigger this extension is **`zm`**. This can be changed in the preferences.

## License

[MIT](LICENSE)
