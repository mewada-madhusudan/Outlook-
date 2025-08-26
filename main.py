#!/usr/bin/env python3
"""
Outlook Email Automation Desktop Tool
Main application entry point
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from ui.main_window import MainWindow
from core.database import DatabaseManager
from core.config import Config

def main():
    """Main application entry point"""
    # Set high DPI scaling
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Outlook Email Automation Tool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("EmailAutomation")
    
    # Set application icon
    if os.path.exists("assets/icon.png"):
        app.setWindowIcon(QIcon("assets/icon.png"))
    
    # Initialize configuration
    config = Config()
    
    # Initialize database
    db_manager = DatabaseManager(config.database_url)
    db_manager.initialize()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()