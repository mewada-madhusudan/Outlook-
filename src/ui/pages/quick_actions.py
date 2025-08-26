"""
Quick Actions page for the Outlook Automation Tool
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QPushButton, QGridLayout, QTextEdit,
                           QLineEdit, QComboBox, QGroupBox, QFormLayout,
                           QDialog, QDialogButtonBox, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

class QuickActionCard(QFrame):
    """Quick action card widget"""
    
    action_triggered = pyqtSignal(str, dict)
    
    def __init__(self, title: str, description: str, action_type: str, color: str = "#0078d4"):
        super().__init__()
        self.action_type = action_type
        self.setup_ui(title, description, color)
    
    def setup_ui(self, title: str, description: str, color: str):
        """Setup quick action card UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 12px;
                padding: 20px;
            }}
            QFrame:hover {{
                background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.05);
            }}
        """)
        self.setFixedHeight(160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {color};")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #605e5c; font-size: 14px; line-height: 1.4;")
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Action button
        action_btn = QPushButton("Use This Action")
        action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.9);
            }}
        """)
        action_btn.clicked.connect(self.trigger_action)
        layout.addWidget(action_btn)
    
    def trigger_action(self):
        """Trigger the quick action"""
        self.action_triggered.emit(self.action_type, {})

class EmailComposerDialog(QDialog):
    """Email composer dialog for quick actions"""
    
    def __init__(self, action_type: str, parent=None):
        super().__init__(parent)
        self.action_type = action_type
        self.setup_ui()
    
    def setup_ui(self):
        """Setup composer dialog UI"""
        self.setWindowTitle(f"Quick Action: {self.action_type.replace('_', ' ').title()}")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Email form
        form_group = QGroupBox("Email Details")
        form_layout = QFormLayout(form_group)
        
        # Recipients
        self.recipients_edit = QLineEdit()
        self.recipients_edit.setPlaceholderText("Enter email addresses separated by commas")
        form_layout.addRow("To:", self.recipients_edit)
        
        # Subject
        self.subject_edit = QLineEdit()
        self.subject_edit.setText(self.get_default_subject())
        form_layout.addRow("Subject:", self.subject_edit)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Normal", "High", "Low"])
        form_layout.addRow("Priority:", self.priority_combo)
        
        layout.addWidget(form_group)
        
        # Message body
        body_group = QGroupBox("Message")
        body_layout = QVBoxLayout(body_group)
        
        self.body_edit = QTextEdit()
        self.body_edit.setPlainText(self.get_default_body())
        body_layout.addWidget(self.body_edit)
        
        layout.addWidget(body_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.include_signature_cb = QCheckBox("Include signature")
        self.include_signature_cb.setChecked(True)
        options_layout.addWidget(self.include_signature_cb)
        
        if self.action_type == "zoom_invite":
            self.create_zoom_cb = QCheckBox("Create Zoom meeting")
            self.create_zoom_cb.setChecked(True)
            options_layout.addWidget(self.create_zoom_cb)
        
        self.track_responses_cb = QCheckBox("Track responses")
        self.track_responses_cb.setChecked(True)
        options_layout.addWidget(self.track_responses_cb)
        
        layout.addWidget(options_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # Customize button text
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Create Draft")
        
        layout.addWidget(buttons)
    
    def get_default_subject(self) -> str:
        """Get default subject based on action type"""
        subjects = {
            "zoom_invite": "Zoom Meeting Invitation",
            "follow_up": "Following up on our conversation",
            "thank_you": "Thank you for your time",
            "meeting_notes": "Meeting Notes",
            "fyi_forward": "FYI: Important Information"
        }
        return subjects.get(self.action_type, "Email from Quick Action")
    
    def get_default_body(self) -> str:
        """Get default body based on action type"""
        bodies = {
            "zoom_invite": "Hi,\n\nI'd like to schedule a Zoom meeting with you.\n\nPlease let me know your availability.\n\nBest regards,",
            "follow_up": "Hi,\n\nI wanted to follow up on our previous conversation.\n\nPlease let me know if you have any updates.\n\nBest regards,",
            "thank_you": "Hi,\n\nThank you for your time and assistance.\n\nI appreciate your help.\n\nBest regards,",
            "meeting_notes": "Hi team,\n\nHere are the notes from our recent meeting:\n\n[Meeting notes will go here]\n\nBest regards,",
            "fyi_forward": "Hi,\n\nI'm forwarding this information for your reference.\n\nBest regards,"
        }
        return bodies.get(self.action_type, "")
    
    def get_email_data(self) -> dict:
        """Get email data from form"""
        return {
            "recipients": [email.strip() for email in self.recipients_edit.text().split(",") if email.strip()],
            "subject": self.subject_edit.text(),
            "body": self.body_edit.toPlainText(),
            "priority": self.priority_combo.currentText(),
            "include_signature": self.include_signature_cb.isChecked(),
            "create_zoom": getattr(self, "create_zoom_cb", None) and self.create_zoom_cb.isChecked(),
            "track_responses": self.track_responses_cb.isChecked()
        }

class QuickActionsPage(QWidget):
    """Quick Actions page"""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("contentPage")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup quick actions page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)
        
        # Page header
        header_layout = QVBoxLayout()
        
        title = QLabel("Quick Actions")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Quickly create common email types with pre-filled templates")
        subtitle.setStyleSheet("color: #605e5c; font-size: 16px;")
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # Quick actions grid
        actions_grid = QGridLayout()
        actions_grid.setSpacing(20)
        
        # Define quick actions
        actions = [
            {
                "title": "📅 Zoom Meeting Invite",
                "description": "Create a meeting invitation with Zoom link and calendar integration",
                "action_type": "zoom_invite",
                "color": "#0078d4"
            },
            {
                "title": "📝 Follow-up Email",
                "description": "Send a professional follow-up message to track progress or responses",
                "action_type": "follow_up",
                "color": "#107c10"
            },
            {
                "title": "🙏 Thank You Note",
                "description": "Express gratitude with a personalized thank you message",
                "action_type": "thank_you",
                "color": "#ff8c00"
            },
            {
                "title": "📋 Meeting Notes",
                "description": "Share meeting notes and action items with attendees",
                "action_type": "meeting_notes",
                "color": "#5c2d91"
            },
            {
                "title": "📬 FYI Forward",
                "description": "Forward information with context and professional formatting",
                "action_type": "fyi_forward",
                "color": "#d83b01"
            },
            {
                "title": "⏰ Reminder Email",
                "description": "Send friendly reminders for deadlines or upcoming events",
                "action_type": "reminder",
                "color": "#ca5010"
            }
        ]
        
        # Create action cards
        for i, action in enumerate(actions):
            card = QuickActionCard(
                action["title"],
                action["description"],
                action["action_type"],
                action["color"]
            )
            card.action_triggered.connect(self.handle_quick_action)
            
            row = i // 2
            col = i % 2
            actions_grid.addWidget(card, row, col)
        
        layout.addLayout(actions_grid)
        layout.addStretch()
    
    def handle_quick_action(self, action_type: str, params: dict):
        """Handle quick action trigger"""
        dialog = EmailComposerDialog(action_type, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            email_data = dialog.get_email_data()
            self.create_email_draft(action_type, email_data)
    
    def create_email_draft(self, action_type: str, email_data: dict):
        """Create email draft from quick action"""
        # TODO: Integrate with Microsoft Graph API to create actual draft
        
        # For now, show confirmation message
        recipients_text = ", ".join(email_data["recipients"][:3])
        if len(email_data["recipients"]) > 3:
            recipients_text += f" and {len(email_data['recipients']) - 3} more"
        
        message = f"Email draft created!\n\n"
        message += f"To: {recipients_text}\n"
        message += f"Subject: {email_data['subject']}\n"
        message += f"Action: {action_type.replace('_', ' ').title()}"
        
        QMessageBox.information(self, "Draft Created", message)
    
    def refresh(self):
        """Refresh quick actions page"""
        pass