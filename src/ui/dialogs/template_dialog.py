"""
Template creation and editing dialog
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QTextEdit, QComboBox, QFormLayout,
                           QPushButton, QDialogButtonBox, QGroupBox, QCheckBox,
                           QScrollArea, QWidget, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Optional

class PlaceholderWidget(QWidget):
    """Widget for managing template placeholders"""
    
    def __init__(self, placeholder_name: str = "", placeholder_type: str = "string", required: bool = False):
        super().__init__()
        self.setup_ui(placeholder_name, placeholder_type, required)
    
    def setup_ui(self, name: str, ptype: str, required: bool):
        """Setup placeholder widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Placeholder name
        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("Placeholder name")
        layout.addWidget(self.name_edit)
        
        # Placeholder type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["string", "multiline", "datetime", "url", "signature"])
        self.type_combo.setCurrentText(ptype)
        layout.addWidget(self.type_combo)
        
        # Required checkbox
        self.required_cb = QCheckBox("Required")
        self.required_cb.setChecked(required)
        layout.addWidget(self.required_cb)
        
        # Remove button
        self.remove_btn = QPushButton("❌")
        self.remove_btn.setFixedSize(30, 30)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #a52b2f;
            }
        """)
        self.remove_btn.clicked.connect(self.remove_placeholder)
        layout.addWidget(self.remove_btn)
    
    def remove_placeholder(self):
        """Remove this placeholder widget"""
        self.setParent(None)
        self.deleteLater()
    
    def get_placeholder_data(self) -> Dict:
        """Get placeholder configuration data"""
        return {
            "name": self.name_edit.text().strip(),
            "type": self.type_combo.currentText(),
            "required": self.required_cb.isChecked()
        }

class TemplateDialog(QDialog):
    """Dialog for creating/editing email templates"""
    
    template_saved = pyqtSignal(dict)
    
    def __init__(self, template_data: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.template_data = template_data
        self.placeholder_widgets = []
        self.setup_ui()
        
        if template_data:
            self.load_template_data(template_data)
    
    def setup_ui(self):
        """Setup template dialog UI"""
        self.setWindowTitle("Create New Template" if not self.template_data else "Edit Template")
        self.setMinimumSize(600, 700)
        self.resize(700, 800)
        
        layout = QVBoxLayout(self)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Basic template info
        basic_group = QGroupBox("Template Information")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter template name")
        basic_layout.addRow("Template Name:", self.name_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(["General", "Meetings", "Follow-ups", "Attachments", "Reminders"])
        basic_layout.addRow("Category:", self.category_combo)
        
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Email subject with placeholders like <RecipientName>")
        basic_layout.addRow("Subject:", self.subject_edit)
        
        content_layout.addWidget(basic_group)
        
        # Email body
        body_group = QGroupBox("Email Body")
        body_layout = QVBoxLayout(body_group)
        
        self.body_edit = QTextEdit()
        self.body_edit.setPlaceholderText("Enter email body with placeholders like <UserMessage>, <Signature>, etc.")
        self.body_edit.setMinimumHeight(200)
        body_layout.addWidget(self.body_edit)
        
        content_layout.addWidget(body_group)
        
        # Placeholders
        placeholders_group = QGroupBox("Placeholders")
        placeholders_layout = QVBoxLayout(placeholders_group)
        
        # Placeholder controls
        controls_layout = QHBoxLayout()
        
        add_placeholder_btn = QPushButton("+ Add Placeholder")
        add_placeholder_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        add_placeholder_btn.clicked.connect(self.add_placeholder)
        controls_layout.addWidget(add_placeholder_btn)
        
        controls_layout.addStretch()
        
        placeholders_layout.addLayout(controls_layout)
        
        # Placeholders container
        self.placeholders_container = QWidget()
        self.placeholders_layout = QVBoxLayout(self.placeholders_container)
        self.placeholders_layout.setContentsMargins(0, 0, 0, 0)
        
        placeholders_scroll = QScrollArea()
        placeholders_scroll.setWidget(self.placeholders_container)
        placeholders_scroll.setWidgetResizable(True)
        placeholders_scroll.setMaximumHeight(200)
        placeholders_layout.addWidget(placeholders_scroll)
        
        content_layout.addWidget(placeholders_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.use_signature_cb = QCheckBox("Include email signature")
        self.use_signature_cb.setChecked(True)
        options_layout.addWidget(self.use_signature_cb)
        
        self.track_responses_cb = QCheckBox("Track email responses")
        self.track_responses_cb.setChecked(True)
        options_layout.addWidget(self.track_responses_cb)
        
        content_layout.addWidget(options_group)
        
        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_template)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def add_placeholder(self):
        """Add a new placeholder widget"""
        placeholder_widget = PlaceholderWidget()
        self.placeholder_widgets.append(placeholder_widget)
        self.placeholders_layout.addWidget(placeholder_widget)
    
    def load_template_data(self, template_data: Dict):
        """Load existing template data into form"""
        self.name_edit.setText(template_data.get("name", ""))
        self.category_combo.setCurrentText(template_data.get("category", "General"))
        self.subject_edit.setText(template_data.get("subject", ""))
        self.body_edit.setPlainText(template_data.get("body", ""))
        
        # Load placeholders
        placeholders = template_data.get("placeholders", {})
        for name, config in placeholders.items():
            placeholder_widget = PlaceholderWidget(
                name, 
                config.get("type", "string"), 
                config.get("required", False)
            )
            self.placeholder_widgets.append(placeholder_widget)
            self.placeholders_layout.addWidget(placeholder_widget)
        
        # Load options
        self.use_signature_cb.setChecked(template_data.get("useSignature", True))
        self.track_responses_cb.setChecked(template_data.get("trackResponses", True))
    
    def save_template(self):
        """Save template data"""
        # Validate required fields
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a template name.")
            return
        
        if not self.subject_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an email subject.")
            return
        
        if not self.body_edit.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an email body.")
            return
        
        # Collect placeholder data
        placeholders = {}
        for widget in self.placeholder_widgets:
            if widget.parent():  # Check if widget hasn't been removed
                placeholder_data = widget.get_placeholder_data()
                if placeholder_data["name"]:
                    placeholders[placeholder_data["name"]] = {
                        "type": placeholder_data["type"],
                        "required": placeholder_data["required"]
                    }
        
        # Create template data
        template_data = {
            "id": self.template_data.get("id") if self.template_data else None,
            "name": self.name_edit.text().strip(),
            "category": self.category_combo.currentText(),
            "subject": self.subject_edit.text().strip(),
            "body": self.body_edit.toPlainText().strip(),
            "placeholders": placeholders,
            "useSignature": self.use_signature_cb.isChecked(),
            "trackResponses": self.track_responses_cb.isChecked()
        }
        
        # Emit signal with template data
        self.template_saved.emit(template_data)
        self.accept()