"""
RSVP Tracker page for the Outlook Automation Tool
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QComboBox, QLineEdit, QProgressBar,
                           QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, timedelta

class RSVPSummaryWidget(QFrame):
    """RSVP summary statistics widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup RSVP summary UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
            }
        """)
        self.setFixedHeight(200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("RSVP Summary")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Stats grid
        stats_layout = QGridLayout()
        
        # Create stat items
        stats = [
            ("Total Events", "12", "#0078d4"),
            ("Responses", "89", "#107c10"),
            ("Pending", "23", "#ff8c00"),
            ("Response Rate", "79%", "#5c2d91")
        ]
        
        for i, (label, value, color) in enumerate(stats):
            stat_widget = self.create_stat_item(label, value, color)
            row = i // 2
            col = i % 2
            stats_layout.addWidget(stat_widget, row, col)
        
        layout.addLayout(stats_layout)
    
    def create_stat_item(self, label: str, value: str, color: str) -> QWidget:
        """Create a stat item widget"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Value
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet("color: white;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 12px;")
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_widget)
        
        return widget

class RSVPTableWidget(QTableWidget):
    """RSVP tracking table widget"""
    
    def __init__(self):
        super().__init__()
        self.events = []
        self.setup_ui()
        self.load_sample_events()
    
    def setup_ui(self):
        """Setup RSVP table UI"""
        # Set columns
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "Event", "Date", "Invited", "Accepted", "Declined", "Tentative", "No Response"
        ])
        
        # Configure table
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        
        # Set column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(2, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
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
    
    def load_sample_events(self):
        """Load sample RSVP events"""
        now = datetime.now()
        
        self.events = [
            {
                "id": 1,
                "name": "Team Weekly Standup",
                "date": now + timedelta(days=1),
                "invited": 8,
                "accepted": 6,
                "declined": 1,
                "tentative": 0,
                "no_response": 1
            },
            {
                "id": 2,
                "name": "Project Review Meeting",
                "date": now + timedelta(days=3),
                "invited": 12,
                "accepted": 8,
                "declined": 2,
                "tentative": 1,
                "no_response": 1
            },
            {
                "id": 3,
                "name": "Client Presentation",
                "date": now + timedelta(days=7),
                "invited": 15,
                "accepted": 10,
                "declined": 0,
                "tentative": 2,
                "no_response": 3
            }
        ]
        
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh table display"""
        self.setRowCount(len(self.events))
        
        for row, event in enumerate(self.events):
            # Event name
            self.setItem(row, 0, QTableWidgetItem(event["name"]))
            
            # Date
            date_text = event["date"].strftime("%Y-%m-%d %H:%M")
            self.setItem(row, 1, QTableWidgetItem(date_text))
            
            # Invited
            self.setItem(row, 2, QTableWidgetItem(str(event["invited"])))
            
            # Accepted
            accepted_item = QTableWidgetItem(str(event["accepted"]))
            accepted_item.setBackground(QColor("#d4edda"))
            self.setItem(row, 3, accepted_item)
            
            # Declined
            declined_item = QTableWidgetItem(str(event["declined"]))
            if event["declined"] > 0:
                declined_item.setBackground(QColor("#f8d7da"))
            self.setItem(row, 4, declined_item)
            
            # Tentative
            tentative_item = QTableWidgetItem(str(event["tentative"]))
            if event["tentative"] > 0:
                tentative_item.setBackground(QColor("#fff3cd"))
            self.setItem(row, 5, tentative_item)
            
            # No Response
            no_response_item = QTableWidgetItem(str(event["no_response"]))
            if event["no_response"] > 0:
                no_response_item.setBackground(QColor("#e2e3e5"))
            self.setItem(row, 6, no_response_item)

class RSVPTrackerPage(QWidget):
    """RSVP Tracker page"""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("contentPage")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup RSVP tracker page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("RSVP Tracker")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Send reminders button
        send_reminders_btn = QPushButton("Send Reminders")
        send_reminders_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff8c00;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e67c00;
            }
        """)
        header_layout.addWidget(send_reminders_btn)
        
        layout.addLayout(header_layout)
        
        # Summary and table layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Summary (left side)
        summary_widget = RSVPSummaryWidget()
        content_layout.addWidget(summary_widget, 1)
        
        # Events table (right side)
        table_frame = QFrame()
        table_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
            }
        """)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(20, 20, 20, 20)
        
        # Table header
        table_header_layout = QHBoxLayout()
        
        table_title = QLabel("Event Tracking")
        table_title_font = QFont()
        table_title_font.setPointSize(16)
        table_title_font.setBold(True)
        table_title.setFont(table_title_font)
        table_header_layout.addWidget(table_title)
        
        table_header_layout.addStretch()
        
        # Filter
        filter_combo = QComboBox()
        filter_combo.addItems(["All Events", "Upcoming", "This Week", "Past Events"])
        table_header_layout.addWidget(filter_combo)
        
        table_layout.addLayout(table_header_layout)
        
        # RSVP table
        self.rsvp_table = RSVPTableWidget()
        table_layout.addWidget(self.rsvp_table)
        
        content_layout.addWidget(table_frame, 2)
        
        layout.addLayout(content_layout)
    
    def refresh(self):
        """Refresh RSVP tracker page"""
        self.rsvp_table.refresh_table()