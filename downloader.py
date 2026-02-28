"""
╔══════════════════════════════════════════════════════════════════╗
║          NEXUS DOWNLOADER  —  Interface Futuriste               ║
║          Un seul fichier Python · Basé sur yt-dlp               ║
║                                                                  ║
║  Dépendances :                                                   ║
║    pip install yt-dlp                                            ║
║                                                                  ║
║  yt-dlp est un outil open-source légal permettant de            ║
║  télécharger des vidéos depuis des milliers de plateformes.     ║
║  Respectez toujours les conditions d'utilisation des sites      ║
║  et les droits d'auteur des contenus téléchargés.               ║
╚══════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import os
import re
import json
import datetime
import time
import ctypes
import sys

# ─────────────────────────────────────────────────────────────────
#  VÉRIFICATION DÉPENDANCES
# ─────────────────────────────────────────────────────────────────
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────
#  PALETTE FUTURISTE — Thème Neon Cyber
# ─────────────────────────────────────────────────────────────────
COLORS = {
    "bg_dark":      "#0A0E1A",   # Fond principal très sombre
    "bg_panel":     "#0F1526",   # Fond des panneaux
    "bg_card":      "#141B30",   # Fond des cartes/items
    "bg_hover":     "#1C2540",   # Survol
    "accent_cyan":  "#00E5FF",   # Cyan neon (actions principales)
    "accent_violet":"#7B2FBE",   # Violet (secondaire)
    "accent_pink":  "#FF2D78",   # Rose neon (erreurs/alertes)
    "accent_green": "#00FF88",   # Vert neon (succès)
    "accent_orange":"#FF8C00",   # Orange (avertissements)
    "text_primary": "#E8EAFB",   # Texte principal
    "text_secondary":"#6B7A9F",  # Texte secondaire
    "text_muted":   "#3A4466",   # Texte désactivé
    "border":       "#1E2A4A",   # Bordures
    "border_accent":"#00E5FF33", # Bordure avec accent (semi-transparent simulé)
    "progress_bg":  "#0F1A30",   # Fond barre progression
    "progress_fg":  "#00E5FF",   # Couleur barre progression
    "btn_primary":  "#00E5FF",   # Bouton principal
    "btn_danger":   "#FF2D78",   # Bouton danger
    "btn_text_dark":"#0A0E1A",   # Texte sur boutons colorés
}

FONTS = {
    "title":    ("Consolas", 18, "bold"),
    "subtitle": ("Consolas", 11),
    "label":    ("Segoe UI", 10),
    "label_bold":("Segoe UI", 10, "bold"),
    "small":    ("Segoe UI", 8),
    "code":     ("Consolas", 9),
    "btn":      ("Segoe UI", 10, "bold"),
    "tag":      ("Consolas", 8),
}


# ─────────────────────────────────────────────────────────────────
#  MODÈLE DE DONNÉES
# ─────────────────────────────────────────────────────────────────
class DownloadItem:
    """Représente un élément de la file de téléchargement."""
    STATUS_PENDING   = "En attente"
    STATUS_FETCHING  = "Récupération info..."
    STATUS_DOWNLOADING = "Téléchargement"
    STATUS_DONE      = "Terminé"
    STATUS_ERROR     = "Erreur"
    STATUS_CANCELLED = "Annulé"

    def __init__(self, url, fmt="video_best", output_dir=""):
        self.url        = url
        self.fmt        = fmt
        self.output_dir = output_dir
        self.status     = self.STATUS_PENDING
        self.title      = url[:55] + "…" if len(url) > 55 else url
        self.progress   = 0.0        # 0.0 à 100.0
        self.speed      = ""
        self.eta        = ""
        self.error_msg  = ""
        self.filepath   = ""
        self.added_at   = datetime.datetime.now().strftime("%H:%M:%S")
        # Référence vers les widgets canvas pour mise à jour
        self._widgets   = {}


# ─────────────────────────────────────────────────────────────────
#  FORMATS DISPONIBLES
# ─────────────────────────────────────────────────────────────────
FORMATS = {
    "🎬  Vidéo Meilleure qualité":  "video_best",
    "🎬  Vidéo 1080p (MP4)":        "video_1080",
    "🎬  Vidéo 720p (MP4)":         "video_720",
    "🎬  Vidéo 480p (MP4)":         "video_480",
    "🎵  Audio MP3 (320 kbps)":     "audio_mp3",
    "🎵  Audio MP3 (128 kbps)":     "audio_mp3_128",
    "🎵  Audio M4A Meilleur":       "audio_m4a",
    "🎵  Audio OPUS Meilleur":      "audio_opus",
}

import shutil

def fmt_key_to_ytdlp(fmt_key: str) -> dict:
    """Convertit la clé de format interne en options yt-dlp."""
    opts = {}
    has_ffmpeg = shutil.which("ffmpeg") is not None

    if fmt_key == "video_best":
        if has_ffmpeg:
            opts["format"] = "bestvideo+bestaudio/best"
            opts["merge_output_format"] = "mp4"
        else:
            opts["format"] = "best[ext=mp4]/best"
    elif fmt_key == "video_1080":
        if has_ffmpeg:
            opts["format"] = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
            opts["merge_output_format"] = "mp4"
        else:
            opts["format"] = "best[height<=1080][ext=mp4]/best"
    elif fmt_key == "video_720":
        if has_ffmpeg:
            opts["format"] = "bestvideo[height<=720]+bestaudio/best[height<=720]"
            opts["merge_output_format"] = "mp4"
        else:
            opts["format"] = "b[height<=720][ext=mp4]/best"
    elif fmt_key == "video_480":
        if has_ffmpeg:
            opts["format"] = "bestvideo[height<=480]+bestaudio/best[height<=480]"
            opts["merge_output_format"] = "mp4"
        else:
            opts["format"] = "b[height<=480][ext=mp4]/best"
    elif fmt_key == "audio_mp3":
        opts["format"] = "bestaudio/best"
        if has_ffmpeg:
            opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}]
    elif fmt_key == "audio_mp3_128":
        opts["format"] = "bestaudio/best"
        if has_ffmpeg:
            opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "128"}]
    elif fmt_key == "audio_m4a":
        opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
    elif fmt_key == "audio_opus":
        opts["format"] = "bestaudio[ext=opus]/bestaudio/best"
    else:
        opts["format"] = "best"
    return opts


# ─────────────────────────────────────────────────────────────────
#  MOTEUR DE TÉLÉCHARGEMENT (Thread séparé)
# ─────────────────────────────────────────────────────────────────
class DownloadEngine:
    """Gère les téléchargements en arrière-plan via yt-dlp. Multi-threads."""

    def __init__(self, ui_queue: queue.Queue):
        self._ui_queue   = ui_queue  # Communication vers l'UI
        self._active     = True
        self._cancel_flags = {}  # item -> threading.Event()

    def enqueue(self, item: DownloadItem):
        self._cancel_flags[item] = threading.Event()
        worker = threading.Thread(target=self._process, args=(item,), daemon=True)
        worker.start()
        self._notify("enqueued", item)

    def cancel_item(self, item: DownloadItem):
        if item in self._cancel_flags:
            self._cancel_flags[item].set()

    def cancel_all(self):
        for flag in self._cancel_flags.values():
            flag.set()

    def stop(self):
        self.cancel_all()
        self._active = False

    def stop(self):
        self._active = False
        self._work_queue.put(None)  # signal de fin

    def _notify(self, event: str, item: DownloadItem, **kwargs):
        self._ui_queue.put({"event": event, "item": item, **kwargs})

    def _clean_ansi(self, text: str) -> str:
        """Supprime les codes couleurs ANSI du terminal renvoyés par yt-dlp."""
        if not text: return ""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def _process(self, item: DownloadItem):
        if not self._active: return
        cancel_flag = self._cancel_flags.get(item)
        if not YT_DLP_AVAILABLE:
            item.status    = DownloadItem.STATUS_ERROR
            item.error_msg = "yt-dlp non installé. Lancez : pip install yt-dlp"
            self._notify("error", item)
            return

        item.status = DownloadItem.STATUS_FETCHING
        self._notify("status_change", item)

        fmt_opts = fmt_key_to_ytdlp(item.fmt)

        def progress_hook(d):
            if cancel_flag and cancel_flag.is_set():
                raise yt_dlp.utils.DownloadError("Téléchargement annulé par l'utilisateur.")
            if d["status"] == "downloading":
                item.status = DownloadItem.STATUS_DOWNLOADING
                # Calcul de la progression
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes", 0)
                if total > 0:
                    item.progress = (downloaded / total) * 100
                else:
                    item.progress = 0
                # Nettoyage des chaînes de vitesse et ETA
                item.speed = self._clean_ansi(d.get("_speed_str", "").strip())
                item.eta   = self._clean_ansi(d.get("_eta_str", "").strip())
                self._notify("progress", item)
            elif d["status"] == "finished":
                item.progress  = 100.0
                item.filepath  = d.get("filename", "")
                self._notify("progress", item)

        ydl_opts = {
            "outtmpl":        os.path.join(item.output_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "quiet":          True,
            "no_warnings":    True,
            **fmt_opts,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Récupération des infos (titre)
                info = ydl.extract_info(item.url, download=False)
                item.title = info.get("title", item.url)[:60]
                self._notify("info_fetched", item)
                # Téléchargement réel
                ydl.download([item.url])

            if cancel_flag and cancel_flag.is_set():
                item.status = DownloadItem.STATUS_CANCELLED
                self._notify("cancelled", item)
            else:
                item.status   = DownloadItem.STATUS_DONE
                item.progress = 100.0
                self._notify("done", item)

        except Exception as exc:
            if cancel_flag and cancel_flag.is_set():
                item.status = DownloadItem.STATUS_CANCELLED
                self._notify("cancelled", item)
            else:
                item.status    = DownloadItem.STATUS_ERROR
                item.error_msg = self._clean_ansi(str(exc))[:120]
                self._notify("error", item)
        finally:
            if item in self._cancel_flags:
                del self._cancel_flags[item]


# ─────────────────────────────────────────────────────────────────
#  WIDGETS PERSONNALISÉS
# ─────────────────────────────────────────────────────────────────
class NeonButton(tk.Frame):
    """Bouton neon compatible Python 3.13+ (Frame + Label, pas de sous-classe Canvas)."""

    def __init__(self, parent, text, command=None, color=None,
                 width=140, height=38, **kw):
        self._btn_color = color or COLORS["accent_cyan"]
        self._btn_text  = text
        self._command   = command
        self._btn_w     = width
        self._btn_h     = height
        self._hover     = False

        bg_normal = self._dim(self._btn_color, -0.85)
        super().__init__(parent,
                         width=width, height=height,
                         bg=bg_normal,
                         highlightbackground=self._btn_color,
                         highlightthickness=1,
                         cursor="hand2", **kw)
        self.pack_propagate(False)

        self._label = tk.Label(self, text=text,
                               bg=bg_normal,
                               fg=self._btn_color,
                               font=FONTS["btn"],
                               cursor="hand2")
        self._label.pack(expand=True, fill="both")

        for w in (self, self._label):
            w.bind("<Enter>",           self._on_enter)
            w.bind("<Leave>",           self._on_leave)
            w.bind("<ButtonPress-1>",   self._on_press)
            w.bind("<ButtonRelease-1>", self._on_release)

    # ── Gestion états ──
    def _on_enter(self, _):
        self._hover = True
        bright = self._dim(self._btn_color, -0.70)
        self.config(bg=bright, highlightbackground=self._btn_color)
        self._label.config(bg=bright, fg="#FFFFFF")

    def _on_leave(self, _):
        self._hover = False
        bg = self._dim(self._btn_color, -0.85)
        self.config(bg=bg, highlightbackground=self._btn_color)
        self._label.config(bg=bg, fg=self._btn_color)

    def _on_press(self, _):
        bright = self._dim(self._btn_color, -0.55)
        self.config(bg=bright)
        self._label.config(bg=bright, fg=COLORS["text_primary"])

    def _on_release(self, _):
        self._on_enter(_)  # revenir à l'état hover
        if self._command:
            self._command()

    def configure_text(self, text):
        self._btn_text = text
        self._label.config(text=text)

    @staticmethod
    def _dim(hex_color: str, factor: float) -> str:
        """Assombrit / éclaircit une couleur hex."""
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
        except (ValueError, IndexError):
            return hex_color
        r = max(0, min(255, int(r * (1 + factor))))
        g = max(0, min(255, int(g * (1 + factor))))
        b = max(0, min(255, int(b * (1 + factor))))
        return f"#{r:02x}{g:02x}{b:02x}"


class AnimatedProgressBar(tk.Frame):
    """Barre de progression neon compatible Python 3.13+.
    Utilise un Canvas interne (pas de sous-classage direct)."""

    def __init__(self, parent, width=400, height=8, **kw):
        super().__init__(parent,
                         width=width, height=height,
                         bg=COLORS["bg_card"],
                         highlightthickness=0, **kw)
        self.pack_propagate(False)
        self._value     = 0.0
        self._animating = False
        self._canvas    = tk.Canvas(self,
                                    width=width, height=height,
                                    bg=COLORS["progress_bg"],
                                    highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)
        self._pw = width
        self._ph = height
        self._draw()

    def set_value(self, value: float):
        self._value = max(0.0, min(100.0, value))
        self._draw()

    def start_shimmer(self):
        if not self._animating:
            self._animating = True
            self._shimmer()

    def stop_shimmer(self):
        self._animating = False

    def _shimmer(self):
        if not self._animating:
            return
        self._draw()
        self._canvas.after(50, self._shimmer)

    def _draw(self):
        c = self._canvas
        c.delete("all")
        w, h = self._pw, self._ph
        c.create_rectangle(0, 0, w, h, fill=COLORS["progress_bg"], outline="")
        fill_w = max(0, int((self._value / 100) * w))
        if fill_w > 0:
            if self._value < 30:
                color = COLORS["accent_violet"]
            elif self._value < 70:
                color = COLORS["accent_cyan"]
            else:
                color = COLORS["accent_green"]
            c.create_rectangle(0, 0, fill_w, h, fill=color, outline="")
            # Reflet haut
            if h > 2:
                c.create_rectangle(0, 0, fill_w, max(1, h // 3),
                                   fill="#FFFFFF33", outline="")
        c.create_rectangle(0, 0, w - 1, h - 1, fill="", outline=COLORS["border"])


class URLCard(tk.Frame):
    """Carte affichant un élément de téléchargement dans la file."""

    def __init__(self, parent, item: DownloadItem, on_remove=None, **kw):
        super().__init__(parent, bg=COLORS["bg_card"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1, **kw)
        self.item      = item
        self.on_remove = on_remove
        self._build()
        self._pulse_phase = 0

    def _build(self):
        # ── Ligne 1 : statut badge + titre + bouton supprimer
        row1 = tk.Frame(self, bg=COLORS["bg_card"])
        row1.pack(fill="x", padx=10, pady=(8, 3))

        # Badge statut
        self.badge = tk.Label(row1, text=" ● ",
                              bg=COLORS["bg_card"],
                              fg=COLORS["text_secondary"],
                              font=FONTS["tag"])
        self.badge.pack(side="left")

        # Titre
        self.title_lbl = tk.Label(row1, text=self.item.title,
                                  bg=COLORS["bg_card"],
                                  fg=COLORS["text_primary"],
                                  font=FONTS["label_bold"],
                                  anchor="w")
        self.title_lbl.pack(side="left", fill="x", expand=True)

        # Bouton supprimer (×)
        if self.on_remove:
            btn_rm = tk.Label(row1, text="✕", bg=COLORS["bg_card"],
                              fg=COLORS["text_muted"], font=FONTS["label"],
                              cursor="hand2")
            btn_rm.pack(side="right", padx=(5, 0))
            btn_rm.bind("<Enter>", lambda e: btn_rm.config(fg=COLORS["accent_pink"]))
            btn_rm.bind("<Leave>", lambda e: btn_rm.config(fg=COLORS["text_muted"]))
            btn_rm.bind("<Button-1>", lambda e: self.on_remove(self))

        # ── Ligne 2 : URL courte
        row2 = tk.Frame(self, bg=COLORS["bg_card"])
        row2.pack(fill="x", padx=10, pady=(0, 3))
        url_short = self.item.url[:70] + ("…" if len(self.item.url) > 70 else "")
        tk.Label(row2, text=url_short, bg=COLORS["bg_card"],
                 fg=COLORS["text_secondary"], font=FONTS["code"],
                 anchor="w").pack(side="left")

        # ── Ligne 3 : barre de progression + stats
        row3 = tk.Frame(self, bg=COLORS["bg_card"])
        row3.pack(fill="x", padx=10, pady=(2, 2))
        self.progress_bar = AnimatedProgressBar(row3, width=330, height=6)
        self.progress_bar.pack(side="left", padx=(0, 8))

        self.stats_lbl = tk.Label(row3, text="", bg=COLORS["bg_card"],
                                  fg=COLORS["text_secondary"],
                                  font=FONTS["small"])
        self.stats_lbl.pack(side="left")

        # ── Ligne 4 : info status
        row4 = tk.Frame(self, bg=COLORS["bg_card"])
        row4.pack(fill="x", padx=10, pady=(0, 8))
        self.status_lbl = tk.Label(row4, text=self.item.status,
                                   bg=COLORS["bg_card"],
                                   fg=COLORS["text_secondary"],
                                   font=FONTS["small"], anchor="w")
        self.status_lbl.pack(side="left")
        self.time_lbl = tk.Label(row4, text=f"Ajouté à {self.item.added_at}",
                                 bg=COLORS["bg_card"],
                                 fg=COLORS["text_muted"],
                                 font=FONTS["small"])
        self.time_lbl.pack(side="right")

    def refresh(self):
        """Met à jour l'affichage depuis self.item."""
        self.title_lbl.config(text=self.item.title)
        self.progress_bar.set_value(self.item.progress)
        # Couleur et texte du badge selon le statut
        status_styles = {
            DownloadItem.STATUS_PENDING:     (COLORS["text_muted"],    "●"),
            DownloadItem.STATUS_FETCHING:    (COLORS["accent_orange"],  "◌"),
            DownloadItem.STATUS_DOWNLOADING: (COLORS["accent_cyan"],    "▶"),
            DownloadItem.STATUS_DONE:        (COLORS["accent_green"],   "✔"),
            DownloadItem.STATUS_ERROR:       (COLORS["accent_pink"],    "✗"),
            DownloadItem.STATUS_CANCELLED:   (COLORS["text_secondary"], "⊘"),
        }
        color, icon = status_styles.get(self.item.status,
                                        (COLORS["text_muted"], "●"))
        self.badge.config(fg=color, text=f" {icon} ")
        self.status_lbl.config(
            fg=color,
            text=self.item.status if not self.item.error_msg
                 else f"Erreur : {self.item.error_msg}"
        )
        if self.item.speed or self.item.eta:
            self.stats_lbl.config(
                text=f"{self.item.speed}  ETA {self.item.eta}"
            )
        elif self.item.status == DownloadItem.STATUS_DONE:
            self.stats_lbl.config(text="100%")
        # Animation shimmer pendant le téléchargement
        if self.item.status == DownloadItem.STATUS_DOWNLOADING:
            self.progress_bar.start_shimmer()
        else:
            self.progress_bar.stop_shimmer()


# ─────────────────────────────────────────────────────────────────
#  APPLICATION PRINCIPALE
# ─────────────────────────────────────────────────────────────────
class NexusDownloaderApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self._items: list[DownloadItem] = []
        self._cards: list[URLCard]      = []
        self._history: list[dict]       = []
        self._ui_queue  = queue.Queue()
        self._engine    = DownloadEngine(self._ui_queue)
        self._output_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self._running   = True  # Contrôle la boucle de polling UI
        self._setup_window()
        self._build_ui()
        self._poll_ui_queue()

        if not YT_DLP_AVAILABLE:
            self.root.after(500, self._warn_no_ytdlp)

    # ── Configuration de la fenêtre ──────────────────────────────
    def _setup_window(self):
        self.root.title("NEXUS DOWNLOADER")
        self.root.geometry("820x700")
        self.root.minsize(700, 560)
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.resizable(True, True)

        # Fix de l'icône de la fenêtre (compatible PyInstaller sys._MEIPASS)
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        icon_path = os.path.join(base_path, "icone.ico")
        if os.path.exists(icon_path):
            try:
                self.root.wm_iconbitmap(icon_path)
            except Exception:
                pass
            try:
                self.root.iconbitmap(default=icon_path)
            except Exception:
                pass

    # ── Construction de l'UI ─────────────────────────────────────
    def _build_ui(self):
        # ── HEADER ──────────────────────────────────────────────
        self._build_header()
        # ── CORPS principal (notebook / onglets) ─────────────────
        self._build_body()
        # ── FOOTER ───────────────────────────────────────────────
        self._build_footer()

    def _build_header(self):
        header = tk.Frame(self.root, bg=COLORS["bg_panel"],
                          height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo / titre
        logo_frame = tk.Frame(header, bg=COLORS["bg_panel"])
        logo_frame.pack(side="left", padx=20, pady=10)

        tk.Label(logo_frame,
                 text="⬡  NEXUS",
                 bg=COLORS["bg_panel"],
                 fg=COLORS["accent_cyan"],
                 font=FONTS["title"]).pack(side="left")
        tk.Label(logo_frame,
                 text=" DOWNLOADER",
                 bg=COLORS["bg_panel"],
                 fg=COLORS["text_primary"],
                 font=FONTS["title"]).pack(side="left")

        # Statut yt-dlp
        status_color = COLORS["accent_green"] if YT_DLP_AVAILABLE else COLORS["accent_pink"]
        status_text  = "● yt-dlp OK" if YT_DLP_AVAILABLE else "● yt-dlp MANQUANT"
        tk.Label(header, text=status_text,
                 bg=COLORS["bg_panel"],
                 fg=status_color,
                 font=FONTS["small"]).pack(side="right", padx=20)

        # Séparateur lumineux
        sep = tk.Frame(self.root, bg=COLORS["accent_cyan"], height=1)
        sep.pack(fill="x")

    def _build_body(self):
        # Notebook personnalisé (onglets manuels)
        self._tab_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        self._tab_frame.pack(fill="both", expand=True)

        # Barre d'onglets
        tab_bar = tk.Frame(self._tab_frame, bg=COLORS["bg_panel"], height=40)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)

        self._tab_pages = {}
        self._active_tab = tk.StringVar(value="download")

        tabs = [
            ("download", "⬇  Télécharger"),
            ("queue",    "≡  File d'attente"),
            ("history",  "◷  Historique"),
        ]
        self._tab_btns = {}
        for key, label in tabs:
            btn = tk.Label(tab_bar, text=label,
                           bg=COLORS["bg_panel"],
                           fg=COLORS["text_secondary"],
                           font=FONTS["label"],
                           padx=18, pady=0, cursor="hand2")
            btn.pack(side="left", fill="y")
            btn.bind("<Button-1>", lambda e, k=key: self._switch_tab(k))
            btn.bind("<Enter>",
                     lambda e, b=btn: b.config(fg=COLORS["accent_cyan"])
                     if b != self._tab_btns.get(self._active_tab.get()) else None)
            btn.bind("<Leave>",
                     lambda e, b=btn, k=key: b.config(
                         fg=COLORS["text_primary"]
                         if k == self._active_tab.get()
                         else COLORS["text_secondary"])
                     )
            self._tab_btns[key] = btn

        # Container des pages
        pages_container = tk.Frame(self._tab_frame, bg=COLORS["bg_dark"])
        pages_container.pack(fill="both", expand=True)

        # Pages
        self._tab_pages["download"] = self._build_download_tab(pages_container)
        self._tab_pages["queue"]    = self._build_queue_tab(pages_container)
        self._tab_pages["history"]  = self._build_history_tab(pages_container)

        # Activation onglet initial
        self._switch_tab("download")

    def _switch_tab(self, key: str):
        # Cacher toutes les pages
        for page in self._tab_pages.values():
            page.pack_forget()
        # Afficher la page active
        self._tab_pages[key].pack(fill="both", expand=True,
                                  padx=12, pady=12)
        # Mise à jour des styles des onglets
        prev = self._active_tab.get()
        self._active_tab.set(key)
        for k, btn in self._tab_btns.items():
            if k == key:
                btn.config(fg=COLORS["accent_cyan"],
                           bg=COLORS["bg_dark"])
            else:
                btn.config(fg=COLORS["text_secondary"],
                           bg=COLORS["bg_panel"])
        # Rafraîchir historique si nécessaire
        if key == "history":
            self._refresh_history_view()

    # ── Onglet Télécharger ───────────────────────────────────────
    def _build_download_tab(self, parent) -> tk.Frame:
        page = tk.Frame(parent, bg=COLORS["bg_dark"])

        # Panneau URL
        url_panel = tk.LabelFrame(page,
                                  text="  🔗  URLs à télécharger  ",
                                  bg=COLORS["bg_panel"],
                                  fg=COLORS["accent_cyan"],
                                  font=FONTS["label_bold"],
                                  bd=1, relief="flat",
                                  labelanchor="nw",
                                  highlightbackground=COLORS["border"],
                                  highlightthickness=1)
        url_panel.pack(fill="x", pady=(0, 10))

        # Instruction
        tk.Label(url_panel,
                 text="Collez une ou plusieurs URLs (une par ligne) :",
                 bg=COLORS["bg_panel"],
                 fg=COLORS["text_secondary"],
                 font=FONTS["small"]).pack(anchor="w", padx=12, pady=(8, 2))

        # Zone de texte multi-lignes
        txt_frame = tk.Frame(url_panel, bg=COLORS["border"])
        txt_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.url_text = tk.Text(txt_frame, height=5,
                                bg=COLORS["bg_card"],
                                fg=COLORS["text_primary"],
                                insertbackground=COLORS["accent_cyan"],
                                selectbackground=COLORS["accent_violet"],
                                font=FONTS["code"],
                                relief="flat",
                                wrap="word",
                                padx=8, pady=6,
                                bd=0)
        self.url_text.pack(fill="x")
        self.url_text.insert("1.0",
            "https://www.youtube.com/watch?v=...\nhttps://...")
        self.url_text.bind("<FocusIn>",  self._clear_placeholder)
        self.url_text.bind("<FocusOut>", self._restore_placeholder)

        # Scroll de la zone de texte
        txt_scroll = tk.Scrollbar(txt_frame, orient="vertical",
                                  command=self.url_text.yview)
        self.url_text.config(yscrollcommand=txt_scroll.set)
        txt_scroll.pack(side="right", fill="y")

        # ── Options de téléchargement ────────────────────────────
        opts_frame = tk.Frame(page, bg=COLORS["bg_dark"])
        opts_frame.pack(fill="x", pady=(0, 10))

        # Sélection du format
        fmt_panel = tk.LabelFrame(opts_frame,
                                  text="  🎛  Format  ",
                                  bg=COLORS["bg_panel"],
                                  fg=COLORS["accent_cyan"],
                                  font=FONTS["label_bold"],
                                  bd=1, relief="flat",
                                  highlightbackground=COLORS["border"],
                                  highlightthickness=1)
        fmt_panel.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.format_var = tk.StringVar(value=list(FORMATS.keys())[0])
        fmt_menu = ttk.Combobox(fmt_panel,
                                textvariable=self.format_var,
                                values=list(FORMATS.keys()),
                                state="readonly",
                                font=FONTS["label"])
        fmt_menu.pack(padx=12, pady=10, fill="x")
        self._style_combobox(fmt_menu)

        # Dossier de sortie
        dir_panel = tk.LabelFrame(opts_frame,
                                  text="  📁  Dossier de sortie  ",
                                  bg=COLORS["bg_panel"],
                                  fg=COLORS["accent_cyan"],
                                  font=FONTS["label_bold"],
                                  bd=1, relief="flat",
                                  highlightbackground=COLORS["border"],
                                  highlightthickness=1)
        dir_panel.pack(side="left", fill="both", expand=True)

        dir_inner = tk.Frame(dir_panel, bg=COLORS["bg_panel"])
        dir_inner.pack(fill="x", padx=12, pady=10)

        self.dir_var = tk.StringVar(value=self._output_dir)
        dir_entry = tk.Entry(dir_inner,
                             textvariable=self.dir_var,
                             bg=COLORS["bg_card"],
                             fg=COLORS["text_primary"],
                             insertbackground=COLORS["accent_cyan"],
                             font=FONTS["code"],
                             relief="flat",
                             bd=4)
        dir_entry.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Label(dir_inner, text=" 📂 ",
                              bg=COLORS["accent_violet"],
                              fg=COLORS["text_primary"],
                              font=FONTS["label"],
                              cursor="hand2", padx=4, pady=2)
        browse_btn.pack(side="right", padx=(6, 0))
        browse_btn.bind("<Button-1>", self._browse_dir)

        # ── Boutons d'action ─────────────────────────────────────
        btn_row = tk.Frame(page, bg=COLORS["bg_dark"])
        btn_row.pack(fill="x", pady=(4, 0))

        NeonButton(btn_row, "⬇  AJOUTER À LA FILE",
                   command=self._add_urls,
                   color=COLORS["accent_cyan"],
                   width=200, height=40).pack(side="left", padx=(0, 8))

        NeonButton(btn_row, "▶  LANCER TOUT",
                   command=self._start_all,
                   color=COLORS["accent_green"],
                   width=160, height=40).pack(side="left", padx=(0, 8))

        NeonButton(btn_row, "✕  ANNULER TOUT",
                   command=self._cancel_all,
                   color=COLORS["accent_pink"],
                   width=160, height=40).pack(side="left")

        NeonButton(btn_row, "🗑  VIDER",
                   command=self._clear_all,
                   color=COLORS["accent_violet"],
                   width=110, height=40).pack(side="right")

        # ── Tip/note ─────────────────────────────────────────────
        tk.Label(page,
                 text="ℹ  Respectez les droits d'auteur et les CGU des plateformes. "
                      "N'utilisez cet outil que pour des contenus autorisés.",
                 bg=COLORS["bg_dark"],
                 fg=COLORS["text_muted"],
                 font=FONTS["small"],
                 wraplength=760,
                 justify="left").pack(anchor="w", pady=(8, 0))

        return page

    # ── Onglet File d'attente ────────────────────────────────────
    def _build_queue_tab(self, parent) -> tk.Frame:
        page = tk.Frame(parent, bg=COLORS["bg_dark"])

        header = tk.Frame(page, bg=COLORS["bg_dark"])
        header.pack(fill="x", pady=(0, 8))
        self.queue_count_lbl = tk.Label(
            header,
            text="File d'attente — 0 élément(s)",
            bg=COLORS["bg_dark"],
            fg=COLORS["accent_cyan"],
            font=FONTS["label_bold"]
        )
        self.queue_count_lbl.pack(side="left")

        # Canvas scrollable pour les cartes
        canvas_container = tk.Frame(page, bg=COLORS["bg_dark"])
        canvas_container.pack(fill="both", expand=True)

        self.queue_canvas = tk.Canvas(canvas_container,
                                      bg=COLORS["bg_dark"],
                                      highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_container, orient="vertical",
                                 command=self.queue_canvas.yview)
        self.queue_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.queue_canvas.pack(side="left", fill="both", expand=True)

        self.queue_inner = tk.Frame(self.queue_canvas, bg=COLORS["bg_dark"])
        self._queue_window = self.queue_canvas.create_window(
            (0, 0), window=self.queue_inner, anchor="nw"
        )
        self.queue_inner.bind("<Configure>", self._on_queue_configure)
        self.queue_canvas.bind("<Configure>", self._on_canvas_configure)
        # Scroll molette
        self.queue_canvas.bind("<MouseWheel>",
            lambda e: self.queue_canvas.yview_scroll(-1*(e.delta//120), "units"))

        return page

    def _on_queue_configure(self, _):
        self.queue_canvas.configure(
            scrollregion=self.queue_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.queue_canvas.itemconfig(self._queue_window, width=event.width)

    # ── Onglet Historique ────────────────────────────────────────
    def _build_history_tab(self, parent) -> tk.Frame:
        page = tk.Frame(parent, bg=COLORS["bg_dark"])

        hdr = tk.Frame(page, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", pady=(0, 8))
        tk.Label(hdr, text="Téléchargements terminés",
                 bg=COLORS["bg_dark"],
                 fg=COLORS["accent_cyan"],
                 font=FONTS["label_bold"]).pack(side="left")
        NeonButton(hdr, "🗑  Effacer",
                   command=self._clear_history,
                   color=COLORS["accent_pink"],
                   width=100, height=30).pack(side="right")

        # Liste historique
        list_frame = tk.Frame(page, bg=COLORS["bg_dark"])
        list_frame.pack(fill="both", expand=True)

        self.history_canvas = tk.Canvas(list_frame,
                                        bg=COLORS["bg_dark"],
                                        highlightthickness=0)
        hist_scroll = tk.Scrollbar(list_frame, orient="vertical",
                                   command=self.history_canvas.yview)
        self.history_canvas.configure(yscrollcommand=hist_scroll.set)
        hist_scroll.pack(side="right", fill="y")
        self.history_canvas.pack(side="left", fill="both", expand=True)

        self.history_inner = tk.Frame(self.history_canvas, bg=COLORS["bg_dark"])
        self._hist_window = self.history_canvas.create_window(
            (0, 0), window=self.history_inner, anchor="nw"
        )
        self.history_inner.bind("<Configure>",
            lambda _: self.history_canvas.configure(
                scrollregion=self.history_canvas.bbox("all")))
        self.history_canvas.bind("<Configure>",
            lambda e: self.history_canvas.itemconfig(
                self._hist_window, width=e.width))
        self.history_canvas.bind("<MouseWheel>",
            lambda e: self.history_canvas.yview_scroll(
                -1*(e.delta//120), "units"))
        return page

    def _refresh_history_view(self):
        for w in self.history_inner.winfo_children():
            w.destroy()
        if not self._history:
            tk.Label(self.history_inner,
                     text="Aucun téléchargement terminé pour l'instant.",
                     bg=COLORS["bg_dark"],
                     fg=COLORS["text_muted"],
                     font=FONTS["label"]).pack(pady=20)
            return
        for entry in reversed(self._history):
            row = tk.Frame(self.history_inner,
                           bg=COLORS["bg_card"],
                           highlightbackground=COLORS["border"],
                           highlightthickness=1)
            row.pack(fill="x", pady=3, padx=2)
            icon = "✔" if entry["status"] == DownloadItem.STATUS_DONE else "✗"
            color = (COLORS["accent_green"]
                     if entry["status"] == DownloadItem.STATUS_DONE
                     else COLORS["accent_pink"])
            tk.Label(row, text=f" {icon} ", bg=COLORS["bg_card"],
                     fg=color, font=FONTS["label_bold"]).pack(side="left",
                                                               padx=(8, 0))
            tk.Label(row, text=entry["title"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text_primary"],
                     font=FONTS["label"]).pack(side="left", padx=4)
            tk.Label(row, text=entry["time"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"],
                     font=FONTS["small"]).pack(side="right", padx=8)

    # ── Footer ───────────────────────────────────────────────────
    def _build_footer(self):
        sep = tk.Frame(self.root, bg=COLORS["border"], height=1)
        sep.pack(fill="x")
        footer = tk.Frame(self.root, bg=COLORS["bg_panel"], height=26)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        self.status_bar = tk.Label(footer,
                                   text="Prêt.",
                                   bg=COLORS["bg_panel"],
                                   fg=COLORS["text_secondary"],
                                   font=FONTS["small"],
                                   anchor="w")
        self.status_bar.pack(side="left", padx=12)
        tk.Label(footer,
                 text="NEXUS v1.0  |  yt-dlp",
                 bg=COLORS["bg_panel"],
                 fg=COLORS["text_muted"],
                 font=FONTS["small"]).pack(side="right", padx=12)

    # ── Helpers UI ───────────────────────────────────────────────
    def _style_combobox(self, combo: ttk.Combobox):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=COLORS["bg_card"],
                        background=COLORS["bg_card"],
                        foreground=COLORS["text_primary"],
                        selectbackground=COLORS["accent_violet"],
                        selectforeground=COLORS["text_primary"],
                        arrowcolor=COLORS["accent_cyan"])
        style.map("TCombobox",
                  fieldbackground=[("readonly", COLORS["bg_card"])],
                  foreground=[("readonly", COLORS["text_primary"])],
                  background=[("readonly", COLORS["bg_panel"])])

    def _clear_placeholder(self, _):
        content = self.url_text.get("1.0", "end").strip()
        if content.startswith("https://www.youtube.com/watch?v=..."):
            self.url_text.delete("1.0", "end")

    def _restore_placeholder(self, _):
        content = self.url_text.get("1.0", "end").strip()
        if not content:
            self.url_text.insert("1.0",
                "https://www.youtube.com/watch?v=...\nhttps://...")

    def _browse_dir(self, _):
        d = filedialog.askdirectory(initialdir=self._output_dir,
                                    title="Choisir le dossier de sortie")
        if d:
            self._output_dir = d
            self.dir_var.set(d)

    def _set_status(self, msg: str):
        self.status_bar.config(text=msg)

    def _warn_no_ytdlp(self):
        messagebox.showwarning(
            "yt-dlp manquant",
            "Le module yt-dlp n'est pas installé.\n\n"
            "Installez-le avec la commande :\n\n"
            "    pip install yt-dlp\n\n"
            "Puis relancez l'application."
        )

    # ── Logique métier ───────────────────────────────────────────
    def _parse_urls(self) -> list[str]:
        """Extrait et valide les URLs depuis la zone de texte."""
        raw = self.url_text.get("1.0", "end").strip()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        valid = []
        url_re = re.compile(r"^https?://", re.I)
        for line in lines:
            if line.startswith("https://www.youtube.com/watch?v=..."):
                continue
            if url_re.match(line):
                valid.append(line)
            else:
                self._set_status(f"URL ignorée (format invalide) : {line[:60]}")
        return list(dict.fromkeys(valid))  # dédoublonnage

    def _add_urls(self):
        """Ajoute les URLs à la file d'attente sans les lancer."""
        urls = self._parse_urls()
        if not urls:
            messagebox.showinfo("Aucune URL",
                                "Aucune URL valide détectée.\n"
                                "Collez des URLs commençant par http:// ou https://")
            return
        fmt_label = self.format_var.get()
        fmt_key   = FORMATS[fmt_label]
        output_dir = self.dir_var.get().strip() or self._output_dir

        added = 0
        for url in urls:
            # Éviter les doublons dans la file
            existing = [i.url for i in self._items]
            if url in existing:
                continue
            item = DownloadItem(url, fmt=fmt_key, output_dir=output_dir)
            self._items.append(item)
            self._add_card(item)
            added += 1

        if added:
            self._set_status(f"{added} URL(s) ajoutée(s) à la file.")
            self._switch_tab("queue")
            self._update_queue_count()
        else:
            self._set_status("Ces URLs sont déjà dans la file.")

    def _add_card(self, item: DownloadItem):
        card = URLCard(self.queue_inner, item,
                       on_remove=self._remove_card)
        card.pack(fill="x", pady=3, padx=2)
        self._cards.append(card)

    def _remove_card(self, card: URLCard):
        # Si le téléchargement est en cours, on l'annule
        if card.item.status in (DownloadItem.STATUS_DOWNLOADING, DownloadItem.STATUS_FETCHING):
            self._engine.cancel_item(card.item)
            # On ne le supprime pas immédiatement de la liste pour laisser
            # l'événement d'erreur ou d'annulation remonter
        else:
            self._items.remove(card.item)
            self._cards.remove(card)
            card.destroy()
            self._update_queue_count()

    def _start_all(self):
        """Envoie tous les éléments en attente au moteur."""
        pending = [i for i in self._items
                   if i.status == DownloadItem.STATUS_PENDING]
        if not pending:
            messagebox.showinfo("Rien à faire",
                                "Aucun élément en attente dans la file.\n"
                                "Ajoutez des URLs d'abord.")
            return
        if not YT_DLP_AVAILABLE:
            self._warn_no_ytdlp()
            return
        for item in pending:
            self._engine.enqueue(item)
        self._set_status(f"▶  {len(pending)} téléchargement(s) lancé(s)…")
        self._switch_tab("queue")

    def _cancel_all(self):
        self._engine.cancel_all()
        self._set_status("⊘  Annulation de tous les téléchargements en cours…")

    def _clear_all(self):
        removable = [c for c in self._cards
                     if c.item.status in (
                         DownloadItem.STATUS_PENDING,
                         DownloadItem.STATUS_DONE,
                         DownloadItem.STATUS_ERROR,
                         DownloadItem.STATUS_CANCELLED)]
        for card in removable:
            self._items.remove(card.item)
            self._cards.remove(card)
            card.destroy()
        self._update_queue_count()
        self._set_status("File partiellement vidée (téléchargements actifs conservés).")

    def _clear_history(self):
        self._history.clear()
        self._refresh_history_view()

    def _update_queue_count(self):
        count = len(self._items)
        self.queue_count_lbl.config(
            text=f"File d'attente — {count} élément(s)")

    # ── Polling des événements du moteur ─────────────────────────
    def _poll_ui_queue(self):
        try:
            while True:
                msg = self._ui_queue.get_nowait()
                self._handle_engine_event(msg)
        except queue.Empty:
            pass
        finally:
            # Ne relancer la boucle que si l'application est toujours active
            if self._running:
                self.root.after(80, self._poll_ui_queue)

    def _handle_engine_event(self, msg: dict):
        item:  DownloadItem = msg["item"]
        event: str          = msg["event"]
        # Trouver la carte correspondante
        card = next((c for c in self._cards if c.item is item), None)

        if event in ("status_change", "info_fetched", "progress"):
            if card:
                card.refresh()

        elif event == "done":
            if card:
                card.refresh()
            self._history.append({
                "title":  item.title,
                "status": item.status,
                "time":   datetime.datetime.now().strftime("%d/%m %H:%M"),
                "url":    item.url,
            })
            self._set_status(f"✔  Terminé : {item.title}")
            
            # Joue un son Windows de notification
            try:
                threading.Thread(target=lambda: ctypes.windll.user32.MessageBeep(0), daemon=True).start()
            except Exception:
                pass

        elif event == "error":
            if card:
                card.refresh()
            self._history.append({
                "title":  item.title,
                "status": item.status,
                "time":   datetime.datetime.now().strftime("%d/%m %H:%M"),
                "url":    item.url,
            })
            self._set_status(f"✗  Erreur : {item.error_msg[:80]}")

        elif event == "cancelled":
            if card:
                card.refresh()
            self._set_status(f"⊘  Annulé : {item.title}")

    # ── Fermeture propre ─────────────────────────────────────────
    def on_close(self):
        if messagebox.askyesno("Quitter",
                               "Quitter NEXUS Downloader ?\n"
                               "Les téléchargements en cours seront interrompus."):
            self._running = False
            # os._exit() est un appel système direct. Impossible à bloquer.
            os._exit(0)


# ─────────────────────────────────────────────────────────────────
#  POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Le AppUserModelID DOIT être défini AVANT la création de la fenêtre tk.Tk()
    # pour que l'icône Windows correcte apparaisse dans la barre des tâches
    try:
        myappid = 'maxsolving.nexus.downloader.1_0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    root = tk.Tk()
    app = NexusDownloaderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
