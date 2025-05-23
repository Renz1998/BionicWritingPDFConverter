import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

import time 
# Add QLineEdit, QHBoxLayout
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                             QLabel, QVBoxLayout, QWidget, QProgressBar, QDialog, 
                             QLineEdit, QHBoxLayout, QMessageBox, QInputDialog, QComboBox) # Added QLineEdit, QHBoxLayout, QInputDialog, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal, QUrl, QTimer, Qt  # Updated import for Qt
from PyQt5.QtGui import QIcon, QDesktopServices, QMovie  # Import QIcon for setting the window icon, QDesktopServices for opening URLs, QMovie for GIFs
import fitz  # PyMuPDF
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="ebooklib")
warnings.filterwarnings("ignore", category=FutureWarning, module="ebooklib")

import json

SETTINGS_FILE = 'settings.json'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except Exception:
        pass

# Modify PDFConverterThread to accept output directory
class PDFConverterThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    saving = pyqtSignal()
    # Add output_dir parameter
    def __init__(self, file_path, bionic_reading_func, output_dir): 
        super().__init__()
        self.file_path = file_path
        self.bionic_reading = bionic_reading_func
        self.output_dir = output_dir # Store output directory

    def int_to_rgb_tuple(self, color_int):
        r = (color_int >> 16) & 0xFF
        g = (color_int >> 8) & 0xFF
        b = color_int & 0xFF
        return (r / 255.0, g / 255.0, b / 255.0)

    def map_font(self, font_name):
        # Map any font to a standard PyMuPDF font
        # Common options: "helv" (Helvetica), "times", "courier"
        return "helv"

    def run(self):
        import fitz, os, traceback
        try:
            print('PDF conversion started')
            doc = fitz.open(self.file_path)
            # Use the provided output directory
            out_dir = self.output_dir 
            os.makedirs(out_dir, exist_ok=True) # Ensure it exists
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            out_path = os.path.join(out_dir, f'{base_name}_bionic.pdf')
            new_doc = fitz.open()
            total = len(doc)
            for i, page in enumerate(doc):
                text_dict = page.get_text('dict')
                has_text = any(block['type'] == 0 and any(line['spans'] for line in block['lines']) for block in text_dict['blocks'])
                has_images = bool(page.get_images(full=True))
                if has_text and has_images:
                    new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                    pix = page.get_pixmap()
                    img_rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
                    new_page.insert_image(img_rect, pixmap=pix)
                    for block in text_dict['blocks']:
                        if block['type'] != 0:
                            continue
                        for line in block['lines']:
                            y0 = min(span['bbox'][1] for span in line['spans'])
                            y1 = max(span['bbox'][3] for span in line['spans'])
                            x0 = min(span['bbox'][0] for span in line['spans'])
                            x1 = max(span['bbox'][2] for span in line['spans'])
                            line_text = ''.join(span['text'] for span in line['spans'])
                            bionic_html = f'<span style="font-size:12pt">{self.bionic_reading(line_text)}</span>'
                            try:
                                new_page.insert_htmlbox(fitz.Rect(x0, y0, x1, y1), bionic_html)
                            except Exception as e:
                                print(f"Error inserting htmlbox on page {i}: {e}")
                elif has_images:
                    new_doc.insert_pdf(doc, from_page=i, to_page=i)
                elif has_text:
                    new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                    for block in text_dict['blocks']:
                        if block['type'] != 0:
                            continue
                        for line in block['lines']:
                            y0 = min(span['bbox'][1] for span in line['spans'])
                            y1 = max(span['bbox'][3] for span in line['spans'])
                            x0 = min(span['bbox'][0] for span in line['spans'])
                            x1 = max(span['bbox'][2] for span in line['spans'])
                            line_text = ''.join(span['text'] for span in line['spans'])
                            bionic_html = f'<span style="font-size:12pt">{self.bionic_reading(line_text)}</span>'
                            try:
                                new_page.insert_htmlbox(fitz.Rect(x0, y0, x1, y1), bionic_html)
                            except Exception as e:
                                print(f"Error inserting htmlbox on page {i}: {e}")
                else:
                    new_doc.new_page(width=page.rect.width, height=page.rect.height)
                # Only emit progress up to 99% during processing
                self.progress.emit(int((i+1)/total*99))
            # Signal that saving is about to start before the potentially long operation
            self.saving.emit()
            print('Saving PDF...')
            try:
                # Save with default options (faster, larger file)
                new_doc.save(out_path, garbage=0) 
                print('PDF saved successfully')
            except Exception as e:
                print(f"Error saving PDF: {e}")
                self.finished.emit(f"Error saving PDF: {e}")
                return
            finally:
                new_doc.close()
                doc.close()
            self.finished.emit(out_path)
        except Exception as e:
            print(f"Exception in PDF conversion: {e}\n{traceback.format_exc()}")
            self.finished.emit(f"Exception in PDF conversion: {e}")

# Modify PDFShrinkThread to accept output directory (though it uses input file's dir)
class PDFShrinkThread(QThread):
    finished = pyqtSignal(str) 
    # Add output_dir parameter (used to determine where the shrunk file goes)
    def __init__(self, input_path, output_dir): 
        super().__init__()
        self.input_path = input_path
        self.output_dir = output_dir # Store output directory for shrunk file

    def run(self):
        import fitz, os, traceback
        try:
            print(f"Shrinking PDF: {self.input_path}")
            base_name = os.path.splitext(os.path.basename(self.input_path))[0]
            if base_name.endswith('_bionic'):
                 base_name = base_name[:-len('_bionic')]
            # Use the provided output directory for the shrunk file
            out_dir = self.output_dir 
            os.makedirs(out_dir, exist_ok=True) # Ensure it exists
            shrunk_out_path = os.path.join(out_dir, f'{base_name}_bionic_shrunk.pdf') 

            doc = fitz.open(self.input_path)
            doc.save(shrunk_out_path, deflate=True, garbage=4, clean=True) 
            doc.close()
            print(f"PDF shrunk successfully: {shrunk_out_path}")
            self.finished.emit(shrunk_out_path)
        except Exception as e:
            error_msg = f"Error shrinking PDF: {e}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            self.finished.emit(error_msg)

class EpubConverterThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    saving = pyqtSignal()
    def __init__(self, file_path, bionic_reading_func, output_dir, output_format):
        super().__init__()
        self.file_path = file_path
        self.bionic_reading = bionic_reading_func
        self.output_dir = output_dir
        self.output_format = output_format  # 'EPUB' or 'PDF'

    def run(self):
        import os, traceback
        try:
            book = epub.read_epub(self.file_path)
            total_items = len([item for item in book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT])
            processed = 0
            def bionic_html(text):
                def style_word(word):
                    if len(word) < 3:
                        return '<span style="font-weight:bold">{}</span>'.format(word)
                    split = (len(word) + 1) // 2
                    return '<span style="font-weight:bold">{}</span>{word[split:]}'
                words = text.split(' ')
                return ' '.join([style_word(w) if w.isalpha() else w for w in words])
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    for tag in soup.find_all(['p', 'span', 'li']):
                        if tag.string and tag.string.strip():
                            tag.string.replace_with(BeautifulSoup(bionic_html(tag.string), 'html.parser'))
                    item.set_content(str(soup).encode('utf-8'))
                    processed += 1
                    self.progress.emit(int(processed / total_items * 90))
            # Save as EPUB
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            os.makedirs(self.output_dir, exist_ok=True)
            if self.output_format == 'EPUB':
                out_path = os.path.join(self.output_dir, f'{base_name}_bionic.epub')
                self.saving.emit()
                epub.write_epub(out_path, book)
                self.finished.emit(out_path)
            else:
                # Convert to PDF: extract all text, apply bionic reading, and save as PDF
                from PyQt5.QtGui import QTextDocument
                from PyQt5.QtPrintSupport import QPrinter
                from PyQt5.QtCore import QBuffer, QByteArray
                from PyQt5.QtWidgets import QApplication
                # Concatenate all text content
                all_html = ''
                for item in book.get_items():
                    if item.get_type() == ebooklib.ITEM_DOCUMENT:
                        all_html += item.get_content().decode('utf-8') + '<br/>'
                # Use QTextDocument to render HTML to PDF
                doc = QTextDocument()
                doc.setHtml(all_html)
                out_path = os.path.join(self.output_dir, f'{base_name}_bionic.pdf')
                self.saving.emit()
                printer = QPrinter()
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(out_path)
                doc.print_(printer)
                self.finished.emit(out_path)
        except Exception as e:
            self.finished.emit(f'Error: {e}\n{traceback.format_exc()}')

class ExperimentalPDFToEPUBThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    saving = pyqtSignal()
    def __init__(self, file_path, bionic_reading_func, output_dir):
        super().__init__()
        self.file_path = file_path
        self.bionic_reading = bionic_reading_func
        self.output_dir = output_dir

    def run(self):
        import fitz, os, traceback, base64
        from ebooklib import epub
        from bs4 import BeautifulSoup
        try:
            doc = fitz.open(self.file_path)
            book = epub.EpubBook()
            book.set_identifier(os.path.basename(self.file_path))
            book.set_title(os.path.splitext(os.path.basename(self.file_path))[0] + ' (Bionic)')
            book.set_language('en')
            chapters = []
            image_items = []
            total = len(doc)
            for i, page in enumerate(doc):
                html = '<html><body>'
                # Extract images
                img_tags = []
                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    img_bytes = base_image['image']
                    img_ext = base_image['ext']
                    img_id = f"img_{i}_{img_index}.{img_ext}"
                    img_path = os.path.join(self.output_dir, img_id)
                    with open(img_path, 'wb') as f:
                        f.write(img_bytes)
                    # Add image to EPUB
                    epub_img = epub.EpubImage()
                    epub_img.file_name = img_id
                    epub_img.media_type = f"image/{img_ext}"
                    epub_img.content = img_bytes
                    book.add_item(epub_img)
                    img_tags.append(f'<img src="{img_id}" style="max-width:100%;max-height:400px;display:block;margin:auto;"/>')
                # Extract text
                text = page.get_text("text")
                bionic_html = self.bionic_reading(text).replace("\n", "<br>")
                html += ''.join(img_tags)
                html += f'<div style="margin-top:10px">{bionic_html}</div>'
                html += '</body></html>'
                chapter = epub.EpubHtml(title=f'Page {i+1}', file_name=f'page_{i+1}.xhtml', lang='en')
                chapter.set_content(html)
                book.add_item(chapter)
                chapters.append(chapter)
                self.progress.emit(int((i+1)/total*90))
            # Assemble spine and TOC
            book.toc = tuple(chapters)
            book.spine = ['nav'] + chapters
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            # Save EPUB
            os.makedirs(self.output_dir, exist_ok=True)
            out_path = os.path.join(self.output_dir, os.path.splitext(os.path.basename(self.file_path))[0] + '_bionic_images.epub')
            self.saving.emit()
            epub.write_epub(out_path, book)
            # Clean up temporary image files
            for img_file in os.listdir(self.output_dir):
                if img_file.startswith("img_") and img_file.split(".")[-1].lower() in ["png", "jpg", "jpeg"]:
                    try:
                        os.remove(os.path.join(self.output_dir, img_file))
                    except Exception:
                        pass
            self.finished.emit(out_path)
        except Exception as e:
            self.finished.emit(f'Error: {e}\n{traceback.format_exc()}')

class BionicPreserveApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.dark_mode = self.settings.get('dark_mode', False)
        self.setWindowTitle('Bionic Writing PDF Converter')
        # --- Add Icon ---
        # Make sure 'icon.png' or 'icon.ico' exists in the same directory
        icon_path = resource_path('icon.png')
        if not os.path.exists(icon_path):
            icon_path = resource_path('icon.ico')  # Fallback for .ico
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("Warning: icon.png or icon.ico not found. No application icon set.")
        # --- End Add Icon ---
        self.setGeometry(100, 100, 450, 380) # Increased height for output path widgets
        self.last_converted_path = None
        self.last_output_dir = None 
        
        # --- Timer Setup ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer_label)
        self.start_time = None
        # --- End Timer Setup ---

        # Apply a modern style
        QApplication.setStyle("Fusion")

        # Customize the palette for a modern look
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        palette.setColor(self.foregroundRole(), Qt.black)
        self.setPalette(palette)

        # Apply a custom stylesheet for a modern appearance
        self.setStyleSheet(
            "QWidget { font-family: Arial; font-size: 12pt; } "
            "QPushButton { background-color: #0078D7; color: white; border-radius: 5px; padding: 5px; } "
            "QPushButton:disabled { background-color: #A9A9A9; color: #D3D3D3; } "
            "QPushButton:hover:!disabled { background-color: #005A9E; } "
            "QLineEdit { border: 1px solid #ccc; border-radius: 5px; padding: 5px; } "
            "QProgressBar { border: 1px solid #ccc; border-radius: 5px; text-align: center; } "
            "QProgressBar::chunk { background-color: #0078D7; } "
        )

        self.init_ui()
        self.apply_theme(self.dark_mode)

    def init_ui(self):
        main_layout = QVBoxLayout() # Renamed layout to main_layout
        self.label = QLabel('Select a PDF to apply bionic reading style.')
        self.open_btn = QPushButton('Open PDF')
        self.open_btn.clicked.connect(self.open_pdf)
        
        # --- Output Directory Widgets ---
        output_label = QLabel("Output Directory:")
        output_layout = QHBoxLayout() # Horizontal layout for path and browse button
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Default: 'converted' folder next to input PDF")
        self.output_dir_edit.setReadOnly(False) # Allow editing, but browsing is safer
        self.browse_output_btn = QPushButton("Browse...")
        self.browse_output_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(self.browse_output_btn)
        # Restore last output directory if available
        last_browse_dir = self.settings.get('last_browse_output_dir', '')
        if last_browse_dir:
            self.output_dir_edit.setText(last_browse_dir)
        # --- End Output Directory Widgets ---

        self.convert_btn = QPushButton('Convert')
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self.start_conversion)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False) 

        self.timer_label = QLabel('') 
        self.shrink_label = QLabel('') 
        self.shrink_btn = QPushButton('Shrink Last Converted PDF')
        self.shrink_btn.setEnabled(False) 
        self.shrink_btn.setToolTip("Optimize the last converted PDF for smaller size (can be slow).")
        self.shrink_btn.clicked.connect(self.start_shrinking)

        self.open_folder_btn = QPushButton('Open Output Folder')
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.setToolTip("Open the folder containing the converted files.")
        self.open_folder_btn.clicked.connect(self.open_output_folder)

        # Add QLabel for GIF display
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)  # Center align the GIF
        main_layout.addWidget(self.gif_label)  # Add the GIF label under the progress bar

        # Set initial GIF to hacker-man-hacker.gif
        self.loading_gif = QMovie(resource_path('hacker-man-hacker.gif'))
        self.finished_gif = QMovie(resource_path('finished-elijah-wood.gif'))
        self.idle_gif = QMovie(resource_path('patrick-star-to-do-list.gif'))
        self.gif_label.setMovie(self.idle_gif)
        self.idle_gif.start()

        # Add dark mode toggle as a small icon-only button
        self.dark_mode_btn = QPushButton()
        self.dark_mode_btn.setCheckable(True)
        self.dark_mode_btn.setChecked(self.dark_mode)
        self.dark_mode_btn.setFixedSize(32, 32)
        self.dark_mode_btn.setStyleSheet("QPushButton { border: none; background: transparent; font-size: 20px; } QPushButton:checked { background: transparent; }")
        self.dark_mode_btn.setToolTip('Toggle dark mode')
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        # Place the button at the top right
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(self.dark_mode_btn)
        main_layout.addLayout(top_bar)

        # Add experimental dropdown
        self.experimental_combo = QComboBox()
        self.experimental_combo.addItem("Standard PDF/EPUB conversion")
        self.experimental_combo.addItem("PDF to EPUB (preserve images, experimental)")
        self.experimental_combo.setToolTip("Experimental: Try PDF to EPUB with images preserved per page.")
        main_layout.addWidget(self.experimental_combo)

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.open_btn)
        main_layout.addWidget(output_label) # Add output label
        main_layout.addLayout(output_layout) # Add output HBox layout
        main_layout.addWidget(self.convert_btn)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.timer_label) 
        main_layout.addWidget(self.shrink_label) 
        main_layout.addWidget(self.shrink_btn)   
        main_layout.addWidget(self.open_folder_btn) 

        # Add disclaimer label for shrinking
        self.disclaimer_label = QLabel("Note: The app might be unresponsive during shrinking.")
        self.disclaimer_label.setStyleSheet("color: gray; font-size: 10pt;")
        main_layout.addWidget(self.disclaimer_label)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.selected_file = None

        # Add icons to buttons
        self.open_btn.setIcon(QIcon("icon.png"))
        self.convert_btn.setIcon(QIcon("icon.png"))
        self.shrink_btn.setIcon(QIcon("icon.png"))
        self.open_folder_btn.setIcon(QIcon("icon.png"))

        # Call update_button_states at the end to set initial state
        self.update_button_states()

    # --- New Method to Browse Output Directory ---
    def browse_output_dir(self):
        # Use last browsed dir if available, else current field, else home
        start_dir = self.settings.get('last_browse_output_dir') or self.output_dir_edit.text() or os.path.expanduser("~")
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", start_dir)
        if directory:
            normalized_dir = os.path.normpath(directory)
            self.output_dir_edit.setText(normalized_dir)
            self.last_output_dir = normalized_dir
            # Save last browsed dir to settings
            self.settings['last_browse_output_dir'] = normalized_dir
            save_settings(self.settings)
            self.update_button_states()
    # --- End New Method ---

    def open_pdf(self):
        # Remember last directory (optional, basic implementation)
        start_dir = os.path.dirname(self.selected_file) if self.selected_file else ''
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', start_dir, 'PDF or EPUB Files (*.pdf *.epub)')
        if file_path:
            if file_path.lower().endswith('.epub'):
                output_format, ok = QInputDialog.getItem(self, "EPUB Output Format", "Save EPUB as:", ["EPUB", "PDF"], 0, False)
                if not ok:
                    return  # User cancelled
                self.selected_epub_output_format = output_format
            else:
                self.selected_epub_output_format = None
            self.selected_file = file_path
            self.label.setText(f'Loaded: {os.path.basename(file_path)}') 
            # Set default output directory and normalize it
            default_output_dir = os.path.normpath(os.path.join(os.path.dirname(self.selected_file), 'converted'))
            self.output_dir_edit.setText(default_output_dir) 
            self.output_dir_edit.setPlaceholderText('')
            # ... reset other UI elements ...
            self.progress_bar.setValue(0)
            self.progress_bar.setRange(0, 100) 
            self.progress_bar.setTextVisible(False)
            self.shrink_label.setText('')     
            self.last_converted_path = None   
            self.last_output_dir = None # Reset until conversion/browse
            self.timer_label.setText('') 
            self.show_idle_gif() # Show idle GIF when a new PDF is opened
            self.update_button_states()  # Update button states using the central method

    # Get the chosen output directory, defaulting if necessary
    def get_output_directory(self):
        chosen_dir_raw = self.output_dir_edit.text().strip()
        if not chosen_dir_raw: # If empty, use default
             if self.selected_file:
                 default_dir = os.path.normpath(os.path.join(os.path.dirname(self.selected_file), 'converted'))
                 try: # Ensure default can be created
                     os.makedirs(default_dir, exist_ok=True)
                     return default_dir
                 except OSError as e:
                     print(f"Error creating default output directory: {e}")
                     QMessageBox.warning(self, "Output Directory Error", 
                                     f"Could not create the default output directory:\n{default_dir}\n\nUsing home directory as fallback.")
                     return os.path.normpath(os.path.expanduser("~")) # Fallback to home
             else:
                 return os.path.normpath(os.path.expanduser("~")) # Failsafe

        chosen_dir = os.path.normpath(chosen_dir_raw) # Normalize the chosen path

        # Check if the chosen directory exists or can be created
        try:
            # Attempt to create if it doesn't exist
            os.makedirs(chosen_dir, exist_ok=True) 
            # Double-check if it's actually a directory after attempting creation
            if os.path.isdir(chosen_dir):
                return chosen_dir
            else: 
                # Path exists but is not a directory, or creation failed silently
                raise OSError(f"Path exists but is not a directory: {chosen_dir}")
        except OSError as e:
            print(f"Error accessing or creating specified output directory: {e}")
            QMessageBox.warning(self, "Output Directory Error", 
                                f"Could not create or access the specified output directory:\n{chosen_dir}\n\nUsing default.")
            # Fall back to default
            if self.selected_file:
                default_dir = os.path.normpath(os.path.join(os.path.dirname(self.selected_file), 'converted'))
                try: # Ensure default can be created
                    os.makedirs(default_dir, exist_ok=True)
                    return default_dir
                except OSError as e_def:
                    print(f"Error creating default output directory: {e_def}")
                    QMessageBox.warning(self, "Output Directory Error", 
                                     f"Could not create the default output directory:\n{default_dir}\n\nUsing home directory as fallback.")
                    return os.path.normpath(os.path.expanduser("~")) # Fallback to home
            else:
                return os.path.normpath(os.path.expanduser("~")) # Failsafe

    def start_conversion(self):
        if not self.selected_file:
            return
        
        output_dir = self.get_output_directory() # Get chosen/default directory
        self.last_output_dir = output_dir # Store the actual directory being used

        self.label.setText(f'Converting: {os.path.basename(self.selected_file)}...')
        # ... disable buttons, start timer ...
        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, 100) 
        self.progress_bar.setTextVisible(True) 
        self.open_btn.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.shrink_btn.setEnabled(False) 
        self.shrink_label.setText('')     
        self.open_folder_btn.setEnabled(False)
        self.browse_output_btn.setEnabled(False) # Disable browse during conversion
        self.output_dir_edit.setEnabled(False) # Disable editing during conversion
        self.timer_label.setText('Elapsed: 00:00') 
        self.start_time = time.time() 
        self.timer.start(1000) 
        
        # Experimental PDF to EPUB (preserve images)
        if self.selected_file.lower().endswith('.pdf') and self.is_experimental_pdf2epub():
            self.converter_thread = ExperimentalPDFToEPUBThread(
                self.selected_file,
                self.bionic_reading,
                output_dir
            )
        elif self.selected_file.lower().endswith('.epub'):
            self.converter_thread = EpubConverterThread(
                self.selected_file,
                self.bionic_reading,
                output_dir,
                getattr(self, 'selected_epub_output_format', 'EPUB')
            )
        else:
            self.converter_thread = PDFConverterThread(self.selected_file, self.bionic_reading, output_dir)
        self.converter_thread.progress.connect(self.on_progress_update)
        self.converter_thread.finished.connect(self.on_conversion_finished)
        self.converter_thread.saving.connect(self.on_saving_started)
        self.converter_thread.started.connect(self.show_loading_gif)  # Update GIF during conversion
        self.converter_thread.finished.connect(self.show_finished_gif)  # Update GIF when conversion is complete
        self.converter_thread.start()

    def on_progress_update(self, value):
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{value}%")
        self.progress_bar.setTextVisible(True)

    def on_saving_started(self):
        self.label.setText('Saving PDF... This may take a moment.')
        self.progress_bar.setValue(99)

    def on_conversion_finished(self, out_path):
        self.timer.stop() 
        self.selected_file = None # Reset selected file after conversion
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("100%")
        
        if out_path.lower().startswith('error') or out_path.lower().startswith('exception'):
            # ... error handling ...
            self.label.setText("Conversion Failed.") 
            self.shrink_label.setText(out_path) 
            QMessageBox.warning(self, "Conversion Error", f"An error occurred during conversion:\n{out_path}")
            self.progress_bar.setValue(0)
            self.last_converted_path = None
            # Don't reset last_output_dir here, keep what was attempted
            self.timer_label.setText('Elapsed: --:--') 
        else:
            # ... success handling ...
            self.progress_bar.setValue(100)
            actual_output_dir = os.path.normpath(os.path.dirname(out_path)) # Normalize actual output dir
            self.label.setText(f'Converted: {os.path.basename(out_path)}')
            self.last_converted_path = out_path # Keep original out_path with correct slashes for file ops
            self.last_output_dir = actual_output_dir # Store normalized dir
            self.output_dir_edit.setText(actual_output_dir) # Update edit field with normalized dir
            self.shrink_label.setText('Ready to shrink (optional).') 
            if self.start_time:
                elapsed = time.time() - self.start_time
                minutes, seconds = divmod(int(elapsed), 60)
                self.timer_label.setText(f'Elapsed: {minutes:02d}:{seconds:02d}')
        self.update_button_states()  # Update button states using the central method

    def start_shrinking(self):
        if not self.last_converted_path or not os.path.exists(self.last_converted_path):
             self.shrink_label.setText('Error: Last converted file not found.')
             self.shrink_btn.setEnabled(False)
             return

        # Use the currently set output directory for the shrunk file
        output_dir = self.get_output_directory() 
        self.last_output_dir = output_dir # Store the actual directory being used

        # Update label and set wait cursor BEFORE starting thread
        self.shrink_label.setText('Shrinking PDF... App may be unresponsive. Please wait.')
        QApplication.setOverrideCursor(Qt.WaitCursor) # Set wait cursor

        # ... disable buttons, set progress bar indeterminate, start timer ...
        self.progress_bar.setRange(0, 0) 
        self.progress_bar.setTextVisible(False)
        self.shrink_btn.setEnabled(False) 
        self.open_btn.setEnabled(False)   
        self.convert_btn.setEnabled(False)
        self.open_folder_btn.setEnabled(False) 
        self.browse_output_btn.setEnabled(False) # Disable browse during shrinking
        self.output_dir_edit.setEnabled(False) # Disable editing during shrinking
        self.timer_label.setText('Elapsed: 00:00') 
        self.start_time = time.time() 
        self.timer.start(1000) 

        # Pass the output directory to the shrink thread
        self.shrinker_thread = PDFShrinkThread(self.last_converted_path, output_dir) 
        self.shrinker_thread.finished.connect(self.on_shrinking_finished)
        self.shrinker_thread.start()

    def on_shrinking_finished(self, result_path):
        self.timer.stop() 
        QApplication.restoreOverrideCursor() 

        self.progress_bar.setRange(0, 100) 
        self.progress_bar.setValue(100) 
        
        if result_path.lower().startswith('error'):
            # ... error handling ...
            self.shrink_label.setText(f"Shrinking Failed: {result_path}")
            QMessageBox.warning(self, "Shrinking Error", f"An error occurred during shrinking:\n{result_path}")
            self.progress_bar.setValue(0)
            self.timer_label.setText('Elapsed: --:--') 
        else:
            # ... success handling ...
            actual_output_dir = os.path.normpath(os.path.dirname(result_path)) # Normalize actual output dir
            self.shrink_label.setText(f'Shrunk PDF saved as: {os.path.basename(result_path)}')
            self.last_output_dir = actual_output_dir # Store normalized dir
            self.output_dir_edit.setText(actual_output_dir) # Update edit field with normalized dir
            if self.start_time:
                elapsed = time.time() - self.start_time
                minutes, seconds = divmod(int(elapsed), 60)
                self.timer_label.setText(f'Elapsed: {minutes:02d}:{seconds:02d}')
        self.update_button_states()  # Update button states using the central method

    # --- New Timer Update Method ---
    def update_timer_label(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed), 60)
            self.timer_label.setText(f'Elapsed: {minutes:02d}:{seconds:02d}')
    # --- End New Timer Update Method ---

    # --- New Method to Open Folder ---
    def open_output_folder(self):
        if self.last_output_dir and os.path.isdir(self.last_output_dir):
            # Use QDesktopServices for cross-platform compatibility (preferred)
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.last_output_dir))
        else:
             QMessageBox.warning(self, "Open Folder", "Output directory not found or not set.")
             self.open_folder_btn.setEnabled(False)
    # --- End New Method ---

    # Add methods to handle GIF changes
    def show_loading_gif(self):
        self.gif_label.setMovie(self.loading_gif)
        self.loading_gif.start()

    def show_finished_gif(self):
        self.gif_label.setMovie(self.finished_gif)
        self.finished_gif.start()

    def show_idle_gif(self):
        self.gif_label.setMovie(self.idle_gif)
        self.idle_gif.start()

    def bionic_reading(self, text):
        # Apply bionic reading: bold the first part of each word, preserving line breaks and spacing, using HTML <b> tags
        def style_word(word):
            if len(word) < 3:
                return f"<b>{word}</b>"
            split = (len(word) + 1) // 2
            return f"<b>{word[:split]}</b>{word[split:]}"
        lines = text.splitlines(keepends=True)
        styled_lines = []
        for line in lines:
            words = line.split(' ')
            styled_words = [style_word(w) if w.isalpha() else w for w in words]
            styled_lines.append(' '.join(styled_words))
        return ''.join(styled_lines)

    # Modify method to update button states comprehensively
    def update_button_states(self):
        # Determine current state
        file_selected = bool(self.selected_file)
        conversion_done = bool(self.last_converted_path and os.path.exists(self.last_converted_path))
        output_dir_valid = bool(self.last_output_dir and os.path.isdir(self.last_output_dir))
        is_processing = (hasattr(self, 'converter_thread') and self.converter_thread and self.converter_thread.isRunning()) or \
                        (hasattr(self, 'shrinker_thread') and self.shrinker_thread and self.shrinker_thread.isRunning())

        # Enable/Disable buttons based on state and processing status
        self.open_btn.setEnabled(not is_processing)
        self.convert_btn.setEnabled(file_selected and not is_processing)
        self.browse_output_btn.setEnabled(not is_processing) # Always enabled unless processing
        # Only enable shrink if last converted file is a PDF
        is_pdf = self.last_converted_path and self.last_converted_path.lower().endswith('.pdf')
        self.shrink_btn.setEnabled(conversion_done and is_pdf and not is_processing)
        self.open_folder_btn.setEnabled(output_dir_valid and not is_processing)

        # Enable/Disable output directory editing
        self.output_dir_edit.setEnabled(not is_processing)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme(self.dark_mode)
        self.settings['dark_mode'] = self.dark_mode
        save_settings(self.settings)

    def apply_theme(self, dark):
        if dark:
            self.setStyleSheet(
                "QWidget { font-family: Arial; font-size: 12pt; background-color: #232629; color: #f0f0f0; } "
                "QPushButton { background-color: #444; color: #f0f0f0; border-radius: 5px; padding: 5px; } "
                "QPushButton:disabled { background-color: #333; color: #888; } "
                "QPushButton:hover:!disabled { background-color: #666; } "
                "QLineEdit { border: 1px solid #555; border-radius: 5px; padding: 5px; background: #181a1b; color: #f0f0f0; } "
                "QProgressBar { border: 1px solid #555; border-radius: 5px; text-align: center; background: #181a1b; color: #f0f0f0; } "
                "QProgressBar::chunk { background-color: #4CAF50; } "
            )
            self.dark_mode_btn.setText('☀️')
        else:
            self.setStyleSheet(
                "QWidget { font-family: Arial; font-size: 12pt; background-color: #ffffff; color: #222; } "
                "QPushButton { background-color: #0078D7; color: white; border-radius: 5px; padding: 5px; } "
                "QPushButton:disabled { background-color: #A9A9A9; color: #D3D3D3; } "
                "QPushButton:hover:!disabled { background-color: #005A9E; } "
                "QLineEdit { border: 1px solid #ccc; border-radius: 5px; padding: 5px; background: #fff; color: #222; } "
                "QProgressBar { border: 1px solid #ccc; border-radius: 5px; text-align: center; background: #fff; color: #222; } "
                "QProgressBar::chunk { background-color: #4CAF50; } "
            )
            self.dark_mode_btn.setText('🌙')
        # Always show percentage text in the progress bar
        self.progress_bar.setTextVisible(True)

    def is_experimental_pdf2epub(self):
        return self.experimental_combo.currentIndex() == 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BionicPreserveApp()
    window.show()
    sys.exit(app.exec_())

# Determine if running as a PyInstaller bundle
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Update icon path
icon_path = resource_path('icon.png')
if not os.path.exists(icon_path):
    icon_path = resource_path('icon.ico')  # Fallback for .ico
if os.path.exists(icon_path):
    self.setWindowIcon(QIcon(icon_path))
else:
    print("Warning: icon.png or icon.ico not found. No application icon set.")
