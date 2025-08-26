"""
Attachments page for the Outlook Automation Tool
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QComboBox, QLineEdit, QProgressBar,
                           QGroupBox, QFormLayout, QCheckBox, QSpinBox,
                           QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class AttachmentRulesWidget(QFrame):
    """Attachment rules management widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup attachment rules UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Download Rules")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_rule_btn = QPushButton("+ Add Rule")
        add_rule_btn.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0e5a0e;
            }
        """)
        header_layout.addWidget(add_rule_btn)
        
        layout.addLayout(header_layout)
        
        # Rules configuration
        rules_group = QGroupBox("Auto-Download Settings")
        rules_layout = QFormLayout(rules_group)
        
        # Enable auto-download
        self.auto_download_cb = QCheckBox("Enable automatic downloads")
        self.auto_download_cb.setChecked(True)
        rules_layout.addRow(self.auto_download_cb)
        
        # File types
        self.file_types_edit = QLineEdit("pdf,docx,xlsx,pptx,zip")
        rules_layout.addRow("File types:", self.file_types_edit)
        
        # Max file size
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setSuffix(" MB")
        self.max_size_spin.setRange(1, 100)
        self.max_size_spin.setValue(10)
        rules_layout.addRow("Max file size:", self.max_size_spin)
        
        # Download location
        download_layout = QHBoxLayout()
        self.download_path_edit = QLineEdit("C:/Downloads/Outlook_Attachments")
        download_layout.addWidget(self.download_path_edit)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_download_folder)
        download_layout.addWidget(browse_btn)
        
        rules_layout.addRow("Download to:", download_layout)
        
        # Organize by
        self.organize_combo = QComboBox()
        self.organize_combo.addItems(["Date", "Sender", "File Type", "Subject"])
        rules_layout.addRow("Organize by:", self.organize_combo)
        
        layout.addWidget(rules_group)
    
    def browse_download_folder(self):
        """Browse for download folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.download_path_edit.setText(folder)

class AttachmentHistoryWidget(QFrame):
    """Attachment download history widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_sample_history()
    
    def setup_ui(self):
        """Setup attachment history UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Download History")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Actions
        export_btn = QPushButton("Export List")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c2d91;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a1f6b;
            }
        """)
        header_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("Clear History")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a52b2f;
            }
        """)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "File Name", "Size", "From", "Downloaded", "Location"
        ])
        
        # Configure table
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        self.history_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e1e5e9;
                border-radius: 6px;
                gridline-color: #f3f2f1;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e1e5e9;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.history_table)
    
    def load_sample_history(self):
        """Load sample download history"""
        history = [
            ["Project_Proposal.pdf", "2.3 MB", "john@company.com", "2024-08-24 10:30", "C:/Downloads/Outlook_Attachments/2024-08-24/"],
            ["Budget_Spreadsheet.xlsx", "1.1 MB", "finance@company.com", "2024-08-24 09:15", "C:/Downloads/Outlook_Attachments/2024-08-24/"],
            ["Meeting_Notes.docx", "0.8 MB", "team@company.com", "2024-08-23 16:45", "C:/Downloads/Outlook_Attachments/2024-08-23/"],
            ["Presentation.pptx", "5.2 MB", "mary@company.com", "2024-08-23 14:20", "C:/Downloads/Outlook_Attachments/2024-08-23/"],
            ["Contract_Draft.pdf", "1.8 MB", "legal@company.com", "2024-08-22 11:30", "C:/Downloads/Outlook_Attachments/2024-08-22/"]
        ]
        
        self.history_table.setRowCount(len(history))
        
        for row, item in enumerate(history):
            for col, value in enumerate(item):
                self.history_table.setItem(row, col, QTableWidgetItem(str(value)))

class AttachmentsPage(QWidget):
    """Attachments page"""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("contentPage")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup attachments page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        title = QLabel("Attachment Management")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Content layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Rules (left side)
        rules_widget = AttachmentRulesWidget()
        content_layout.addWidget(rules_widget, 1)
        
        # History (right side)
        history_widget = AttachmentHistoryWidget()
        content_layout.addWidget(history_widget, 2)
        
        layout.addLayout(content_layout)
    
    def refresh(self):
        """Refresh attachments page"""
        pass