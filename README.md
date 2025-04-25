# Bionic Writing PDF Converter

Bionic Writing PDF Converter is a Python desktop application that applies bionic reading to PDF files while preserving the original images and formatting. The application is built using PyQt5 for the GUI and PyMuPDF for PDF processing.

## Features
- **Bionic Reading**: Enhances text readability by bolding parts of words.
- **Preserves Formatting**: Retains original images and layout of the PDF.
- **GIF Animations**: Displays fun GIFs during idle, processing, and completion states.
- **Output Directory Customization**: Allows users to specify the output directory for converted files.
- **PDF Shrinking**: Optionally optimizes the size of the converted PDF.

## Requirements
- Python 3.11 or later
- PyQt5
- PyMuPDF
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
   - Open a PDF file.
   - Specify an output directory (optional).
   - Convert the PDF with bionic reading.
   - Shrink the converted PDF (optional).

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

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.