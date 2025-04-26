# Bionic Writing PDF Converter

Bionic Writing PDF Converter is a Python desktop application that applies bionic reading to PDF and EPUB (ebook) files while preserving the original images and formatting. The application is built using PyQt5 for the GUI, PyMuPDF for PDF processing, and ebooklib for EPUB processing.

## Features
- **Bionic Reading**: Enhances text readability by bolding parts of words.
- **Supports PDF and EPUB**: Works with both PDF and EPUB (ebook) files.
- **Preserves Formatting**: Retains original images and layout of the PDF or EPUB.
- **GIF Animations**: Displays fun GIFs during idle, processing, and completion states.
- **Output Directory Customization**: Allows users to specify the output directory for converted files.
- **PDF Shrinking**: Optionally optimizes the size of the converted PDF.
- **EPUB Output Choice**: When converting an EPUB, choose to save as EPUB (with bionic reading) or as a PDF.

## Requirements
- Python 3.11 or later
- PyQt5
- PyMuPDF
- ebooklib
- beautifulsoup4
- Git LFS (for handling large files like `.exe` and `.pkg`)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Renz1998/BionicWritingPDFConverter.git
   cd BionicWritingPDFConverter
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   pip install beautifulsoup4
   ```
3. Install Git LFS (if not already installed):
   ```bash
   git lfs install
   ```

## Usage
1. Run the application:
   ```bash
   python main.py
   ```
2. Use the GUI to:
   - Open a PDF or EPUB file.
   - If you open an EPUB, choose whether to save as EPUB or PDF.
   - Specify an output directory (optional).
   - Convert the file with bionic reading.
   - Shrink the converted PDF (optional, only for PDF output).

## Building the Executable
To create a standalone `.exe` file:
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Run the following command:
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon.png;." --add-data "patrick-star-to-do-list.gif;." --add-data "hacker-man-hacker.gif;." --add-data "finished-elijah-wood.gif;." main.py
   ```
3. The `.exe` file will be located in the `dist` folder.

## Notes
- The application may become unresponsive during PDF shrinking due to the intensive processing required.
- Ensure that the required GIF files (`patrick-star-to-do-list.gif`, `hacker-man-hacker.gif`, `finished-elijah-wood.gif`) are in the same directory as the application.
- EPUB shrinking is not supported; the shrink feature is only available for PDF output.

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.