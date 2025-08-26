"""
Reminders page for the Outlook Automation Tool
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QComboBox, QLineEdit, QDateTimeEdit,
                           QDialog, QDialogButtonBox, QMessageBox, QTextEdit,
                           QGroupBox, QFormLayout, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime, QTimer
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, timedelta

class ReminderTableWidget(QTableWidget):
    """Custom table widget for reminders"""
    
    reminder_selected = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.reminders = []
        self.setup_ui()
        self.load_sample_reminders()
    
    def setup_ui(self):
        """Setup reminder table UI"""
        # Set columns
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels([
            "Subject", "Recipients", "Scheduled", "Status", "Type", "Actions"
        ])
        
        # Configure table
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        
        # Set column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Subject
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Recipients
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Scheduled
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        
        # Style
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e1e5e9;
                border-radius: 6px;
                background-color: white;
                gridline-color: #f3f2f1;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f3f2f1;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e1e5e9;
                font-weight: bold;
            }
        """)
    
    def load_sample_reminders(self):
        """Load sample reminders"""
        now = datetime.now()
        
        self.reminders = [
            {
                "id": 1,
                "subject": "Project Status Update - Please Respond",
                "recipients": ["john@company.com", "mary@company.com"],
                "scheduled": now + timedelta(hours=2),
                "status": "Pending",
                "type": "Follow-up",
                "original_sent": now - timedelta(days=3),
                "message": "Hi,\n\nI sent you a project update request 3 days ago and haven't received a response yet. Could you please provide an update on the current status?\n\nThanks!"
            },
            {
                "id": 2,
                "subject": "Meeting Confirmation Required",
                "recipients": ["team@company.com"],
                "scheduled": now + timedelta(days=1),
                "status": "Scheduled",
                "type": "RSVP Reminder",
                "original_sent": now - timedelta(days=1),
                "message": "Hi team,\n\nI need confirmation for tomorrow's meeting. Please respond if you'll be attending.\n\nBest regards"
            },
            {
                "id": 3,
                "subject": "Document Review Deadline",
                "recipients": ["legal@company.com"],
                "scheduled": now + timedelta(hours=6),
                "status": "Pending",
                "type": "Deadline Reminder",
                "original_sent": now - timedelta(days=5),
                "message": "Hi,\n\nThe document review deadline is approaching. Please let me know the status of your review.\n\nThanks!"
            }
        ]
        
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh table display"""
        self.setRowCount(len(self.reminders))
        
        for row, reminder in enumerate(self.reminders):
            # Subject
            self.setItem(row, 0, QTableWidgetItem(reminder["subject"]))
            
            # Recipients
            recipients_text = f"{len(reminder['recipients'])} recipients"
            if len(reminder['recipients']) == 1:
                recipients_text = reminder['recipients'][0]
            self.setItem(row, 1, QTableWidgetItem(recipients_text))
            
            # Scheduled
            scheduled_text = reminder["scheduled"].strftime("%Y-%m-%d %H:%M")
            self.setItem(row, 2, QTableWidgetItem(scheduled_text))
            
            # Status
            status_item = QTableWidgetItem(reminder["status"])
            if reminder["status"] == "Pending":
                status_item.setBackground(QColor("#fff3cd"))
            elif reminder["status"] == "Sent":
                status_item.setBackground(QColor("#d4edda"))
            elif reminder["status"] == "Failed":
                status_item.setBackground(QColor("#f8d7da"))
            self.setItem(row, 3, status_item)
            
            # Type
            self.setItem(row, 4, QTableWidgetItem(reminder["type"]))
            
            # Actions (placeholder)
            self.setItem(row, 5, QTableWidgetItem("Edit | Cancel"))

class RemindersPage(QWidget):
    """Reminders page"""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("contentPage")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup reminders page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Reminders")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # New reminder button
        new_btn = QPushButton("+ New Reminder")
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        header_layout.addWidget(new_btn)
        
        layout.addLayout(header_layout)
        
        # Filters
        filters_frame = QFrame()
        filters_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        filters_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        filters_layout = QHBoxLayout(filters_frame)
        
        # Status filter
        filters_layout.addWidget(QLabel("Status:"))
        status_combo = QComboBox()
        status_combo.addItems(["All", "Pending", "Scheduled", "Sent", "Failed"])
        filters_layout.addWidget(status_combo)
        
        # Type filter
        filters_layout.addWidget(QLabel("Type:"))
        type_combo = QComboBox()
        type_combo.addItems(["All", "Follow-up", "RSVP Reminder", "Deadline Reminder"])
        filters_layout.addWidget(type_combo)
        
        filters_layout.addStretch()
        
        # Search
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Search reminders...")
        search_edit.setFixedWidth(250)
        filters_layout.addWidget(search_edit)
        
        layout.addWidget(filters_frame)
        
        # Reminders table
        self.reminders_table = ReminderTableWidget()
        layout.addWidget(self.reminders_table)
    
    def refresh(self):
        """Refresh reminders page"""
        self.reminders_table.refresh_table()