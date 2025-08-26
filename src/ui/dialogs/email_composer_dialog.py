"""
Email composer dialog for creating drafts
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QTextEdit, QComboBox, QFormLayout,
                           QPushButton, QDialogButtonBox, QGroupBox, QCheckBox,
                           QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from typing import Dict, Optional, List
import re

class EmailCreationThread(QThread):
    """Thread for creating email drafts"""
    
    success = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, email_data: Dict, graph_client=None):
        super().__init__()
        self.email_data = email_data
        self.graph_client = graph_client
    
    def run(self):
        """Create email draft"""
        try:
            if self.graph_client and self.graph_client.is_authenticated():
                # Create actual draft via Microsoft Graph
                message_data = self._prepare_graph_message()
                draft = self.graph_client.create_draft(message_data)
                self.success.emit({"draft_id": draft.get("id"), "method": "graph"})
            else:
                # Simulate draft creation
                import time
                time.sleep(1)  # Simulate processing
                self.success.emit({"draft_id": "simulated_123", "method": "simulation"})
                
        except Exception as e:
            self.error.emit(str(e))
    
    def _prepare_graph_message(self) -> Dict:
        """Prepare message data for Microsoft Graph API"""
        recipients = []
        for email in self.email_data.get("recipients", []):
            recipients.append({
                "emailAddress": {
                    "address": email.strip(),
                    "name": email.strip()
                }
            })
        
        message = {
            "subject": self.email_data.get("subject", ""),
            "body": {
                "contentType": "Text",
                "content": self.email_data.get("body", "")
            },
            "toRecipients": recipients
        }
        
        if self.email_data.get("priority") == "High":
            message["importance"] = "high"
        elif self.email_data.get("priority") == "Low":
            message["importance"] = "low"
        
        return message

class EmailComposerDialog(QDialog):
    """Dialog for composing emails from templates"""
    
    email_created = pyqtSignal(dict)
    
    def __init__(self, template_data: Optional[Dict] = None, action_type: str = "", parent=None):
        super().__init__(parent)
        self.template_data = template_data
        self.action_type = action_type
        self.placeholder_inputs = {}
        self.setup_ui()
        
        if template_data:
            self.load_template_data(template_data)
        elif action_type:
            self.load_action_template(action_type)
    
    def setup_ui(self):
        """Setup email composer UI"""
        title = "Compose Email"
        if self.template_data:
            title = f"Compose Email - {self.template_data.get('name', 'Template')}"
        elif self.action_type:
            title = f"Quick Action - {self.action_type.replace('_', ' ').title()}"
        
        self.setWindowTitle(title)
        self.setMinimumSize(700, 600)
        self.resize(800, 700)
        
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
        self.subject_edit.setPlaceholderText("Email subject")
        form_layout.addRow("Subject:", self.subject_edit)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Normal", "High", "Low"])
        form_layout.addRow("Priority:", self.priority_combo)
        
        layout.addWidget(form_group)
        
        # Template placeholders (if using template)
        if self.template_data and self.template_data.get("placeholders"):
            placeholders_group = QGroupBox("Template Values")
            placeholders_layout = QFormLayout(placeholders_group)
            
            for name, config in self.template_data["placeholders"].items():
                if config["type"] == "multiline":
                    input_widget = QTextEdit()
                    input_widget.setMaximumHeight(100)
                else:
                    input_widget = QLineEdit()
                
                if config["type"] == "datetime":
                    from datetime import datetime
                    input_widget.setPlaceholderText("YYYY-MM-DD HH:MM or 'now'")
                elif config["type"] == "url":
                    input_widget.setPlaceholderText("https://example.com")
                elif config["type"] == "signature":
                    input_widget.setPlaceholderText("Your email signature")
                
                label = name
                if config.get("required"):
                    label += " *"
                
                placeholders_layout.addRow(label, input_widget)
                self.placeholder_inputs[name] = input_widget
            
            layout.addWidget(placeholders_group)
        
        # Message body
        body_group = QGroupBox("Message")
        body_layout = QVBoxLayout(body_group)
        
        self.body_edit = QTextEdit()
        self.body_edit.setMinimumHeight(300)
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
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self.preview_email)
        buttons_layout.addWidget(preview_btn)
        
        buttons_layout.addStretch()
        
        draft_btn = QPushButton("Create Draft")
        draft_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        draft_btn.clicked.connect(self.create_draft)
        buttons_layout.addWidget(draft_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_template_data(self, template_data: Dict):
        """Load template data into form"""
        self.subject_edit.setText(template_data.get("subject", ""))
        self.body_edit.setPlainText(template_data.get("body", ""))
    
    def load_action_template(self, action_type: str):
        """Load predefined action template""" 
        templates = {
            "zoom_invite": {
                "subject": "Zoom Meeting Invitation",
                "body": "Hi,\n\nI'd like to schedule a Zoom meeting with you.\n\nPlease let me know your availability.\n\nBest regards,"
            },
            "follow_up": {
                "subject": "Following up on our conversation", 
                "body": "Hi,\n\nI wanted to follow up on our previous conversation.\n\nPlease let me know if you have any updates.\n\nBest regards,"
            },
            "thank_you": {
                "subject": "Thank you for your time",
                "body": "Hi,\n\nThank you for your time and assistance.\n\nI appreciate your help.\n\nBest regards,"
            }
        }
        
        if action_type in templates:
            template = templates[action_type]
            self.subject_edit.setText(template["subject"])
            self.body_edit.setPlainText(template["body"])
    
    def preview_email(self):
        """Preview the email with placeholders filled"""
        try:
            preview_text = self._process_template()
            
            # Show preview dialog
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("Email Preview")
            preview_dialog.setMinimumSize(500, 400)
            
            layout = QVBoxLayout(preview_dialog)
            
            preview_edit = QTextEdit()
            preview_edit.setPlainText(preview_text)
            preview_edit.setReadOnly(True)
            layout.addWidget(preview_edit)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(preview_dialog.accept)
            layout.addWidget(close_btn)
            
            preview_dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Preview Error", f"Error generating preview: {str(e)}")
    
    def create_draft(self):
        """Create email draft"""
        if not self._validate_form():
            return
        
        try:
            email_data = self._get_email_data()
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Create draft in background thread
            self.creation_thread = EmailCreationThread(email_data, self._get_graph_client())
            self.creation_thread.success.connect(self._on_draft_created)
            self.creation_thread.error.connect(self._on_creation_error)
            self.creation_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create draft: {str(e)}")
    
    def _validate_form(self) -> bool:
        """Validate form data"""
        if not self.recipients_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter at least one recipient.")
            return False
        
        if not self.subject_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an email subject.")
            return False
        
        if not self.body_edit.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an email body.")
            return False
        
        return True
    
    def _get_email_data(self) -> Dict:
        """Get email data from form"""
        recipients = [email.strip() for email in self.recipients_edit.text().split(",") if email.strip()]
        
        body_text = self._process_template()
        
        return {
            "recipients": recipients,
            "subject": self.subject_edit.text().strip(),
            "body": body_text,
            "priority": self.priority_combo.currentText(),
            "include_signature": self.include_signature_cb.isChecked(),
            "create_zoom": getattr(self, "create_zoom_cb", None) and self.create_zoom_cb.isChecked(),
            "track_responses": self.track_responses_cb.isChecked()
        }
    
    def _process_template(self) -> str:
        """Process template with placeholder values"""
        body_text = self.body_edit.toPlainText()
        
        # Process template placeholders if available
        if self.placeholder_inputs:
            for name, input_widget in self.placeholder_inputs.items():
                value = input_widget.toPlainText() if hasattr(input_widget, 'toPlainText') else input_widget.text()
                body_text = body_text.replace(f"<{name}>", value)
        
        return body_text
    
    def _get_graph_client(self):
        """Get Graph client from main window"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'graph_client'):
                return parent.graph_client
            parent = parent.parent()
        return None
    
    def _on_draft_created(self, result: Dict):
        """Handle successful draft creation"""
        self.progress_bar.setVisible(False)
        
        method = result.get("method", "unknown")
        if method == "graph":
            message = "Email draft created successfully in Outlook!"
        else:
            message = "Email draft created successfully (simulated)!"
        
        QMessageBox.information(self, "Success", message)
        self.email_created.emit(result)
        self.accept()
    
    def _on_creation_error(self, error: str):
        """Handle draft creation error"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Failed to create draft:\n{error}")