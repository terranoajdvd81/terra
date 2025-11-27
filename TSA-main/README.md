
---

# TSA – Tmodloader Server Administrator

A CLI tool to manage **tModLoader servers** with an easy way to switch between different tModLoader versions while keeping the same configuration of mods, worlds, and plugins across multiple machines.

---

## Why

This project started as a simple way to use **GitHub Codespaces** with different proxy/VPN providers (since Codespaces doesn’t support port forwarding). Over time, additional functionalities were added to simplify server administration and mod handling.

---

## Usage

TSA is written in **Python 3.12.0**. There are two ways to use it:

### 1. SoloRun Version

A combined script that executes all steps in order automatically.

### 2. Compiled Version

A single executable compiled with **PyArmor**, available in the **Releases** tab.
This version runs everything in one binary without leaving residual files in the directory.

---

## Notes (2025 Update)

* **Direct links**: MediaFire and similar services may change their URL formats. Always use the **direct download link** (e.g., copy the link from the green/blue download button).
* **Mods not appearing?**

  * Mods must be in the root of the `.rar` file (same for worlds).
  * The program respects tModLoader **modpacks**. If you’ve never created one, check the *Mod Packs* section inside tModLoader.
  * tModLoader generates an `enable.json` file next to your mods, listing active mods. This file **must be included**. If not, you can enable mods manually from the program (`M: modlist → E: enable all → R: reload and return`).
  * If you imported a world, you cannot modify mod activation before server startup.

---

## Troubleshooting

1. **Incompatible Mods**

   * Some mods (e.g., *Calamity Music*, translation packs) are not updated at the same pace as the main mod. You may need to remove conflicting ones.
   * Note: A mod may work on the client but still fail on the server.

2. **Wrong Version of Mods**

   * Supported tModLoader versions match Steam releases:

     * `1.3.5.3 – tModLoader v0.11.8.9`
     * `1.4.3 – tModLoader v2022.9.47.87`
     * `1.4.x – Latest available version of tModLoader` (auto-updates, which may be newer than Steam’s version—be cautious when updating).

---



