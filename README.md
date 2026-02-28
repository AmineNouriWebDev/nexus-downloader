# ⬡ NEXUS Downloader

**Application desktop portable avec interface graphique futuriste (Tkinter) pour télécharger des vidéos et audios depuis YouTube et plus de 1000 plateformes.**

Développé par **[MaxSolving](https://maxsolving.com)**

---

## ✨ Fonctionnalités

- 🎨 **Interface futuriste Neon Cyber** — Thème sombre avec accents néon (cyan, violet, rose, vert)
- 📋 **File de téléchargement** — Ajoutez plusieurs URLs en une seule fois
- 🎬 **Formats variés** — Meilleure qualité vidéo (MP4), 1080p, 720p, 480p, et audio (MP3 320k, MP3 128k, M4A, OPUS)
- ⚡ **Téléchargements simultanés** — Chaque vidéo tourne dans son propre thread, indépendamment
- 📊 **Progression en temps réel** — Barre de progression animée avec vitesse et ETA
- ✅ **Historique** — Consultez tout ce que vous avez téléchargé
- 🔔 **Notification sonore Windows** — Ping quand un téléchargement est terminé
- 🔑 **FFmpeg facultatif** — Fonctionne même sans FFmpeg (via formats pré-fusionnés)
- 📦 **Un seul fichier** — `downloader.py` est entièrement autonome

---

## 🚀 Installation (mode développeur)

### Prérequis
- [Python 3.10+](https://python.org)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

```bash
pip install yt-dlp
```

### Lancement
```bash
python downloader.py
```

---

## 📦 Compiler en .exe portable (Windows)

```bash
pip install pyinstaller

pyinstaller --noconfirm --onedir --windowed \
    --icon "icone.ico" \
    --add-data "icone.ico;." \
    --name "NEXUS_Downloader" \
    --version-file "version.txt" \
    downloader.py
```

Le dossier `dist/NEXUS_Downloader/` contiendra le `.exe` prêt à distribuer, **sans Python requis**.

---

## 📁 Structure du projet

```
youtube-downloader/
├── downloader.py      # Application principale (fichier unique)
├── icone.ico          # Icône du logiciel
├── version.txt        # Métadonnées PyInstaller (société MaxSolving)
├── README.md
└── .gitignore
```

---

## ⚠️ Avertissement légal

Ce logiciel utilise [yt-dlp](https://github.com/yt-dlp/yt-dlp), un outil open-source légal.  
Veuillez respecter les **conditions d'utilisation** des plateformes et les **droits d'auteur** des contenus que vous téléchargez.  
Ce logiciel est destiné à un usage personnel uniquement.

---

## 📄 Licence

© 2026 MaxSolving — Tous droits réservés.  
[https://maxsolving.com](https://maxsolving.com)
