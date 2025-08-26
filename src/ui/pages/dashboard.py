"""
Dashboard page for the Outlook Automation Tool
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QGridLayout, QScrollArea, QPushButton,
                           QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

class MetricCard(QFrame):
    """Metric display card widget"""
    
    def __init__(self, title: str, value: str, subtitle: str = ""):
        super().__init__()
        self.setup_ui(title, value, subtitle)
    
    def setup_ui(self, title: str, value: str, subtitle: str):
        """Setup metric card UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        self.setFixedHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #605e5c; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet("color: #323130;")
        layout.addWidget(value_label)
        
        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #107c10; font-size: 12px;")
            layout.addWidget(subtitle_label)
        
        layout.addStretch()

class RecentActivityWidget(QFrame):
    """Recent activity display widget"""
    
    def __init__(self):
        super().__init__()
        self.activities = []
        self.setup_ui()
        self.load_activities()
    
    def setup_ui(self):
        """Setup recent activity UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                margin: 2px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Recent Activity")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #323130;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                color: #0078d4;
                border: 1px solid #0078d4;
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f3f9fd;
                color: #106ebe;
                border-color: #106ebe;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_activities)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Activity list
        self.activity_list = QListWidget()
        self.activity_list.setFrameShape(QFrame.Shape.NoFrame)
        self.activity_list.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px 0px;
                border-bottom: 1px solid #f3f2f1;
                color: #605e5c;
            }
            QListWidget::item:last {
                border-bottom: none;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        
        layout.addWidget(self.activity_list)
    
    def load_activities(self):
        """Load recent activities"""
        self.activities = [
            {"time": "2 minutes ago", "action": "📧 Sent 'Weekly Update' template to 12 recipients"},
            {"time": "15 minutes ago", "action": "⏰ Reminder sent for 'Project Meeting' to 8 people"}, 
            {"time": "1 hour ago", "action": "📎 Downloaded 5 attachments from Sales folder"},
            {"time": "2 hours ago", "action": "✅ RSVP tracking updated for 'Team Standup'"},
            {"time": "Yesterday", "action": "📝 Created new template 'Client Follow-up'"}
        ]
        self.refresh_activity_list()
    
    def refresh_activity_list(self):
        """Refresh the activity list display"""
        self.activity_list.clear()
        
        for activity in self.activities:
            item_text = f"{activity['action']}\n{activity['time']}"
            item = QListWidgetItem(item_text)
            self.activity_list.addItem(item)
    
    def add_activity(self, action: str):
        """Add a new activity to the list"""
        new_activity = {"time": "Just now", "action": action}
        self.activities.insert(0, new_activity)
        
        # Keep only last 10 activities
        if len(self.activities) > 10:
            self.activities = self.activities[:10]
        
        self.refresh_activity_list()
    
    def refresh_activities(self):
        """Refresh activities from data source"""
        # Update timestamps
        import datetime
        now = datetime.datetime.now()
        for i, activity in enumerate(self.activities):
            if activity['time'] == "Just now":
                self.activities[i]['time'] = "1 minute ago"
            elif activity['time'] == "1 minute ago":
                self.activities[i]['time'] = "2 minutes ago"
        
        self.refresh_activity_list()

class QuickActionsWidget(QFrame):
    """Quick actions widget for dashboard"""
    
    action_clicked = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup quick actions UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                margin: 2px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Header
        title = QLabel("Quick Actions")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #323130;")
        layout.addWidget(title)
        
        # Action buttons grid
        actions_layout = QGridLayout()
        actions_layout.setSpacing(12)
        
        actions = [
            ("📅 Zoom Invite", "zoom_invite", "#0078d4"),
            ("📝 Follow-up", "follow_up", "#107c10"),
            ("🙏 Thank You", "thank_you", "#ff8c00"),
            ("📎 Attachments", "attachments", "#5c2d91")
        ]
        
        for i, (text, action, color) in enumerate(actions):
            btn = QPushButton(text)
            btn.setFixedHeight(55)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.85);
                    transform: translateY(-1px);
                }}
                QPushButton:pressed {{
                    background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.95);
                    transform: translateY(0px);
                }}
            """)
            btn.clicked.connect(lambda checked, a=action: self.action_clicked.emit(a))
            actions_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(actions_layout)

class DashboardPage(QWidget):
    """Main dashboard page"""
    
    quick_action_triggered = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("contentPage")
        self.metric_cards = []
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        """Setup dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Metrics row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)
        
        # Create metric cards
        metrics = [
            ("Templates Created", "15", "+3 this week"),
            ("Emails Sent", "142", "+28 this week"),
            ("Responses Tracked", "89", "62.7% response rate"),
            ("Reminders Sent", "23", "+5 pending")
        ]
        
        for title, value, subtitle in metrics:
            card = MetricCard(title, value, subtitle)
            self.metric_cards.append(card)
            metrics_layout.addWidget(card)
        
        layout.addLayout(metrics_layout)
        
        # Content row
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Recent activity (left side)
        self.recent_activity = RecentActivityWidget()
        content_layout.addWidget(self.recent_activity, 2)
        
        # Quick actions (right side)
        self.quick_actions = QuickActionsWidget()
        self.quick_actions.action_clicked.connect(self.handle_quick_action)
        content_layout.addWidget(self.quick_actions, 1)
        
        layout.addLayout(content_layout)
        
        layout.addStretch()
    
    def load_initial_data(self):
        """Load initial dashboard data"""
        # This would typically load from database or API
        pass
    
    def handle_quick_action(self, action: str):
        """Handle quick action button click"""
        # Add activity to recent activities
        action_names = {
            "zoom_invite": "📅 Created Zoom meeting invitation",
            "follow_up": "📝 Created follow-up email",
            "thank_you": "🙏 Created thank you message",
            "attachments": "📎 Processed email attachments"
        }
        
        if action in action_names:
            self.recent_activity.add_activity(action_names[action])
        
        # Emit signal to main window to handle action
        self.quick_action_triggered.emit(action)
    
    def refresh(self):
        """Refresh dashboard data"""
        # Refresh activities
        self.recent_activity.refresh_activities()
        
        # Update metrics (in real app, this would fetch from database)
        self.update_metrics()
    
    def update_metrics(self):
        """Update metric card values"""
        # This would typically update with real data
        import random
        
        # Simulate metric updates
        for i, card in enumerate(self.metric_cards):
            # This is just a simulation - in real app would use actual data
            pass
    
    def add_activity(self, activity: str):
        """Add new activity to dashboard"""
        self.recent_activity.add_activity(activity)