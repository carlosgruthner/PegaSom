import os
import customtkinter as ctk
from tkinter import filedialog
import yt_dlp
from tkinter import messagebox, Listbox, Scrollbar, END
import threading
import sys


# Determina o diretório base
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

icone_path = os.path.join(base_path, "music.ico")


class YouTubeToMP3App:
    def __init__(self, root):
        self.root = root
        self.root.title("PegaSom")
        self.root.geometry("600x500")
        self.root.iconbitmap(icone_path)
        ctk.set_appearance_mode("dark")  # Tema escuro
        ctk.set_default_color_theme("blue")  # Tema azul

        # Campo para URL do YouTube
        self.url_label = ctk.CTkLabel(root, text="URL do YouTube:", font=("Arial", 14))
        self.url_label.pack(pady=10)
        self.url_entry = ctk.CTkEntry(root, width=400, placeholder_text="Cole a URL aqui")
        self.url_entry.pack()

        # Seleção de qualidade do MP3
        self.quality_label = ctk.CTkLabel(root, text="Qualidade do MP3 (kbps):", font=("Arial", 14))
        self.quality_label.pack(pady=10)
        self.quality_var = ctk.StringVar(value="192")  # Valor padrão: 192 kbps
        self.quality_menu = ctk.CTkOptionMenu(root, values=["64", "128", "192", "256", "320"], 
                                             variable=self.quality_var)
        self.quality_menu.pack()

        # Campo para o diretório de saída
        self.output_label = ctk.CTkLabel(root, text="Diretório de Saída:", font=("Arial", 14))
        self.output_label.pack(pady=10)
        self.select_dir_button = ctk.CTkButton(
            root, 
            text="Escolher Diretório", 
            command=self.select_output_dir, 
            fg_color="#1f538d", 
            hover_color="#14375e"
        )
        self.select_dir_button.pack(pady=10)

        self.output_entry = ctk.CTkEntry(root, width=400)
        self.output_entry.pack()
        self.output_entry.insert(0, os.getcwd())  # Campo padrão

        # Botão para baixar
        self.download_button = ctk.CTkButton(root, text="Baixar MP3", command=self.download_mp3, 
                                            fg_color="#1f538d", hover_color="#14375e")
        self.download_button.pack(pady=(50, 20))

        # Frame para barra de progresso e porcentagem
        self.progress_frame = ctk.CTkFrame(root)
        self.progress_frame.pack(pady=10)

        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400)
        self.progress_bar.pack(side="left", padx=10)
        self.progress_bar.set(0)

        # Label para porcentagem
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="0%", font=("Arial", 14))
        self.progress_label.pack(side="left")

        # Variáveis para controle
        self.videos = []
        self.active_downloads = 0  # Contador de downloads ativos

    def is_playlist(self, url):
        """Verifica se a URL é de uma playlist."""
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return 'entries' in info
        
    def select_output_dir(self):
        """Abre uma caixa de diálogo para selecionar o diretório de saída."""
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.output_entry.delete(0, END)  # Limpa o campo
            self.output_entry.insert(0, selected_dir)  # Insere o diretório selecionado
        
    def download_mp3(self):
        """Inicia o download em uma thread separada."""
        url = self.url_entry.get()
        bitrate = self.quality_var.get()
        output_path = self.output_entry.get()

        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL.")
            return
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Desativa o botão de download
        self.download_button.configure(state="disabled")
        self.progress_label.configure(text="Preparando...")

        if self.is_playlist(url):
            try:
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    self.videos = list(info['entries'])
                selected_urls = [video['webpage_url'] for video in self.videos]
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao processar playlist: {str(e)}")
                self.download_button.configure(state="normal")
                return
        else:
            selected_urls = [url]

        # Reiniciar a barra de progresso
        self.progress_bar.set(0)
        self.active_downloads = len(selected_urls)  # Define o número de downloads ativos

        # Iniciar o download em uma thread separada para cada URL
        for video_url in selected_urls:
            thread = threading.Thread(target=self.download_to_mp3, args=(video_url, bitrate, output_path))
            thread.start()

    def download_to_mp3(self, url, bitrate, output_path):
        """Baixa o áudio de um vídeo e converte para MP3 com hook de progresso."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': bitrate,
            }],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],  # Hook de progresso
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao baixar {url}: {str(e)}"))
            self.root.after(0, self.download_finished)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if d.get('total_bytes') and d.get('downloaded_bytes'):
                progress = d['downloaded_bytes'] / d['total_bytes']
                percentage = int(progress * 100)
                self.root.after(0, self.update_progress, progress, percentage)
        elif d['status'] == 'finished':
            self.root.after(0, self.update_progress, 1.0, 100)
            self.root.after(0, self.download_finished)

    def update_progress(self, progress, percentage):
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"{percentage}%")

    def download_finished(self):
        """Atualiza o estado após cada download terminar."""
        self.active_downloads -= 1
        if self.active_downloads <= 0:
            self.progress_label.configure(text="Concluído")
            self.download_button.configure(state="normal")  # Reativa o botão quando todos terminarem
        else:
            self.progress_label.configure(text=f"Baixando ({self.active_downloads} restantes)")

if __name__ == "__main__":
    root = ctk.CTk()
    app = YouTubeToMP3App(root)
    root.mainloop()