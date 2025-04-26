# Bionic Writing PDF Converter

Bionic Writing PDF Converter is a Python desktop application that applies bionic reading to PDF and EPUB (ebook) files while preserving the original images and formatting. The application is built using PyQt5 for the GUI, PyMuPDF for PDF processing, and ebooklib for EPUB processing.

## 🚀 Highlights
- **NEW: Fast Experimental PDF to EPUB (Preserve Images)**: Convert PDFs to EPUBs with images and bionic reading applied per page—much faster than PDF-to-PDF conversion!
- **Bionic Reading**: Enhances text readability by bolding parts of words.
- **Supports PDF and EPUB**: Works with both PDF and EPUB (ebook) files.
- **Preserves Formatting**: Retains original images and layout of the PDF or EPUB.
- **GIF Animations**: Displays fun GIFs during idle, processing, and completion states.
- **Output Directory Customization**: Allows users to specify the output directory for converted files.
- **PDF Shrinking**: Optionally optimizes the size of the converted PDF.
- **EPUB Output Choice**: When converting an EPUB, choose to save as EPUB (with bionic reading) or as a PDF.

## Quick Start
**Recommended for regular users:** Double-click `run_silent.bat` to launch the app without a terminal window.

**For developers or debugging:** Use `start.bat` to launch the app with a terminal window (to see output and errors).

## Requirements
- Python 3.11 or later
- PyQt5
- PyMuPDF
- ebooklib
- beautifulsoup4
- Git LFS (for handling large files like `.pkg`)

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
3. (Optional) Set up a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

## Usage
1. **Recommended for regular users:** Double-click `run_silent.bat` to launch the app without a terminal window.
2. **For developers:** Double-click `start.bat` to launch the app with a terminal window for debugging.
3. Alternatively, you can run the app manually:
   ```bash
   python main.py
   ```
4. Use the GUI to:
   - Open a PDF or EPUB file.
   - **To use the fast experimental PDF to EPUB (preserve images) feature:**
     - Select "PDF to EPUB (preserve images, experimental)" from the dropdown before converting a PDF.
     - The output EPUB will have images and bionic reading applied per page, and is much faster than PDF-to-PDF conversion!
   - If you open an EPUB, choose whether to save as EPUB or PDF.
   - Specify an output directory (optional).
   - Convert the file with bionic reading.
   - Shrink the converted PDF (optional, only for PDF output).

## Notes
- The application may become unresponsive during PDF shrinking due to the intensive processing required.
- Ensure that the required GIF files (`patrick-star-to-do-list.gif`, `hacker-man-hacker.gif`, `finished-elijah-wood.gif`) are in the same directory as the application.
- EPUB shrinking is not supported; the shrink feature is only available for PDF output.
- The experimental PDF to EPUB feature is fast and preserves images per page, but may not perfectly match complex PDF layouts.

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.