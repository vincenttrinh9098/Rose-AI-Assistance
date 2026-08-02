# Installing Rose

## 1. Download and Install

- Download `Rose.dmg` and open it
- Drag the Rose icon into your **Applications** folder
- Eject the Rose disk image

## 2. First Launch — Bypass the Security Warning

macOS will likely show a warning saying it can't verify Rose is free of malware. This is expected for apps distributed outside the App Store — Rose isn't malicious, it just isn't registered with Apple.

Open **Terminal** (search for it in Spotlight, Cmd+Space) and run these three commands, one at a time:

```bash
chmod -R u+w /Applications/Rose.app
xattr -cr /Applications/Rose.app
open /Applications/Rose.app
```

This should open Rose normally. (If double-clicking the Rose icon works fine without a warning, you can skip this step entirely.)

## 3. Complete Setup

Rose will walk you through:

- Entering your Anthropic API key
- Granting Microphone, Input Monitoring, and Accessibility permissions when prompted

## 4. You're Ready

Click **"ROSE"** on the Home screen to start, and try your hotkey or the Speak button.

---

## Troubleshooting

### If something looks wrong or out of date

If Rose seems to be missing apps/settings you'd expect, or something feels stuck from an older version, reset its configuration:

```bash
rm -rf ~/Library/Application\ Support/Rose/config
```

Then quit and reopen Rose — it will recreate its config files fresh.

### If Rose says "damaged and can't be opened"

Run the same three commands from Step 2 again:

```bash
chmod -R u+w /Applications/Rose.app
xattr -cr /Applications/Rose.app
open /Applications/Rose.app
```

### If the hotkey doesn't respond

1. Open **System Settings → Privacy & Security → Input Monitoring**
2. Check that Rose (or RoseMain) is listed and enabled
3. If it's not listed, click **+**, press **Cmd+Shift+G**, and paste this path:
   ```
   /Applications/Rose.app/Contents/Resources/RoseMain/RoseMain
   ```
4. Restart Rose (click "ROSE" to stop, then click again to start)

### If calendar, messages, or reminders features don't work

Same process as above, but under **System Settings → Privacy & Security → Accessibility**.
