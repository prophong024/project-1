from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import yt_dlp
import threading

Window.clearcolor = (0.95, 0.95, 0.95, 1)  # Đặt màu nền cho cửa sổ chính

class YoutubeDownloader(App):
    def build(self):
        self.main_layout = GridLayout(cols=1, padding=10, spacing=10)
        self.main_layout.background_color = (0.8, 0.8, 0.8, 1)  # Đặt màu nền cho layout chính

        self.url_input = TextInput(hint_text='Nhập URL YouTube', size_hint=(1, None), height=40)
        self.url_input.background_color = (1, 1, 1, 1)  # Đặt màu nền cho ô nhập URL
        self.url_input.font_size = 16

        self.format_button = Button(text='Hiển Thị Định Dạng', size_hint=(1, None), height=40)
        self.format_button.background_color = (0.2, 0.6, 0.8, 1)  # Đặt màu nền cho nút "Hiển Thị Định Dạng"
        self.format_button.color = (1, 1, 1, 1)  # Đặt màu chữ cho nút "Hiển Thị Định Dạng"
        self.format_button.font_size = 16

        self.download_button = Button(text='Tải Xuống', size_hint=(1, None), height=40)
        self.download_button.background_color = (0.2, 0.6, 0.8, 1)  # Đặt màu nền cho nút "Tải Xuống"
        self.download_button.color = (1, 1, 1, 1)  # Đặt màu chữ cho nút "Tải Xuống"
        self.download_button.font_size = 16

        self.progress_label = Label(text='', color=(0, 0.5, 0.7, 1))  # Đặt màu chữ cho thông báo tiến độ
        self.progress_label.font_size = 16

        self.main_layout.add_widget(self.url_input)
        self.main_layout.add_widget(self.format_button)
        self.main_layout.add_widget(self.download_button)
        self.main_layout.add_widget(self.progress_label)

        self.format_button.bind(on_press=self.show_formats)
        self.download_button.bind(on_press=self.download_video)

        return self.main_layout

    def show_formats(self, instance):
        url = self.url_input.text
        ydl_opts = {
            'listformats': True,
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            formats = ydl.extract_info(url, download=False)
            format_choices = []
            for f in formats['formats']:
                if f.get('acodec') is not None and f.get('vcodec') is not None:
                    format_label = f"{f['format_id']} - {f['resolution'] if 'resolution' in f else f['format_note']}"
                    if 'ext' in f:
                        format_label += f" ({f['ext']})"
                    format_choices.append(format_label)

        content = ScrollView()
        layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        for choice in format_choices:
            btn = Button(text=choice, size_hint_y=None, height=40)
            btn.background_color = (0.2, 0.6, 0.8, 1)  # Đặt màu nền cho từng nút chất lượng
            btn.color = (1, 1, 1, 1)  # Đặt màu chữ cho từng nút chất lượng
            btn.font_size = 16
            btn.bind(on_release=self.select_format)
            layout.add_widget(btn)

        content.add_widget(layout)
        popup = Popup(title='Chọn Định Dạng', content=content, size_hint=(None, None), size=(400, 400))
        popup.open()

    def select_format(self, instance):
        self.selected_format = instance.text
        Popup(title='Định Dạng Đã Chọn', content=Label(text=f"Bạn đã chọn: {self.selected_format}"), size_hint=(None, None), size=(300, 200)).open()

    def download_video(self, instance):
        url = self.url_input.text
        if not hasattr(self, 'selected_format') or not self.selected_format:
            return

        self.progress_label.text = 'Bắt đầu tải xuống...'
        download_thread = threading.Thread(target=self.perform_download, args=(url, self.selected_format))
        download_thread.start()

    def perform_download(self, url, selected_format):
        format_id = selected_format.split(' - ')[0]
        ydl_opts = {
            'format': f"{format_id}+bestaudio/best",
            'merge_output_format': 'mp4',
            'progress_hooks': [self.progress_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def progress_hook(self, d):
        if d['status'] == 'downloading' and d.get('total_bytes'):
            downloaded_bytes = d.get('downloaded_bytes')
            total_bytes = d.get('total_bytes')
            if downloaded_bytes is not None and total_bytes is not None:
                percent = 100 * downloaded_bytes / total_bytes
                self.progress_label.text = f"Tiến độ Tải Xuống: {int(percent)}%"

if __name__ == '__main__':
    YoutubeDownloader().run()
