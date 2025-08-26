"""
Theme management for the Outlook Automation Tool
"""

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from typing import Dict, Any

class ThemeManager(QObject):
    """Manages application themes and styling"""
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.themes = {
            "light": self.get_light_theme(),
            "dark": self.get_dark_theme()
        }
        self.current_theme = "light"
    
    def get_light_theme(self) -> Dict[str, Any]:
        """Get light theme configuration"""
        return {
            "name": "Light",
            "colors": {
                "primary": "#0078d4",
                "primary_hover": "#106ebe",
                "background": "#ffffff",
                "surface": "#f8f9fa",
                "text": "#323130",
                "text_secondary": "#605e5c",
                "border": "#e1e5e9",
                "accent": "#0078d4",
                "success": "#107c10",
                "warning": "#ff8c00",
                "error": "#d13438"
            },
            "stylesheet": """
                QMainWindow {
                    background-color: #ffffff;
                    color: #323130;
                }
                
                QFrame#header {
                    background-color: #ffffff;
                    border-bottom: 1px solid #e1e5e9;
                }
                
                QLabel#pageTitle {
                    color: #323130;
                }
                
                QLabel#authStatus {
                    color: #605e5c;
                    font-size: 14px;
                }
                
                QPushButton#connectButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                }
                
                QPushButton#connectButton:hover {
                    background-color: #106ebe;
                }
                
                QPushButton#connectButton:pressed {
                    background-color: #005a9e;
                }
                
                QWidget#contentPage {
                    background-color: #ffffff;
                }
                
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                
                QScrollBar:vertical {
                    background-color: #f3f2f1;
                    width: 12px;
                    border-radius: 6px;
                }
                
                QScrollBar::handle:vertical {
                    background-color: #c8c6c4;
                    border-radius: 6px;
                    min-height: 20px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background-color: #a19f9d;
                }
            """
        }
    
    def get_dark_theme(self) -> Dict[str, Any]:
        """Get dark theme configuration"""
        return {
            "name": "Dark",
            "colors": {
                "primary": "#4cc2ff",
                "primary_hover": "#0078d4",
                "background": "#1f1f1f",
                "surface": "#2d2d30",
                "text": "#ffffff",
                "text_secondary": "#cccccc",
                "border": "#3e3e42",
                "accent": "#4cc2ff",
                "success": "#4ac94a",
                "warning": "#ffb900",
                "error": "#f85149"
            },
            "stylesheet": """
                QMainWindow {
                    background-color: #1f1f1f;
                    color: #ffffff;
                }
                
                QWidget#sidebar {
                    background-color: #2d2d30;
                    border-right: 1px solid #3e3e42;
                }
                
                QFrame#sidebarHeader {
                    background-color: #0e639c;
                    border-bottom: 1px solid #1b6ec2;
                }
                
                QPushButton#sidebarButton {
                    color: #cccccc;
                }
                
                QPushButton#sidebarButton:hover {
                    background-color: rgba(76, 194, 255, 0.1);
                }
                
                QPushButton#sidebarButton:checked {
                    background-color: #4cc2ff;
                    color: #1f1f1f;
                }
                
                QLabel#sectionLabel {
                    color: #999999;
                }
                
                QFrame#header {
                    background-color: #2d2d30;
                    border-bottom: 1px solid #3e3e42;
                }
                
                QLabel#pageTitle {
                    color: #ffffff;
                }
                
                QLabel#authStatus {
                    color: #cccccc;
                }
                
                QPushButton#connectButton {
                    background-color: #4cc2ff;
                    color: #1f1f1f;
                }
                
                QPushButton#connectButton:hover {
                    background-color: #0078d4;
                    color: #ffffff;
                }
                
                QWidget#contentPage {
                    background-color: #1f1f1f;
                }
                
                QScrollBar:vertical {
                    background-color: #3e3e42;
                }
                
                QScrollBar::handle:vertical {
                    background-color: #54545c;
                }
                
                QScrollBar::handle:vertical:hover {
                    background-color: #6e6e78;
                }
            """
        }
    
    def apply_theme(self, widget: QWidget, theme_name: str):
        """Apply theme to widget"""
        if theme_name not in self.themes:
            return
        
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        # Apply stylesheet
        widget.setStyleSheet(theme["stylesheet"])
        
        # Emit theme changed signal
        self.theme_changed.emit(theme_name)
    
    def get_color(self, color_name: str) -> str:
        """Get color value from current theme"""
        theme = self.themes.get(self.current_theme, self.themes["light"])
        return theme["colors"].get(color_name, "#000000")
    
    def get_available_themes(self) -> list:
        """Get list of available themes"""
        return list(self.themes.keys())