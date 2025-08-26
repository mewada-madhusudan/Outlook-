"""
Templates page for the Outlook Automation Tool
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QPushButton, QListWidget, QListWidgetItem,
                           QTextEdit, QLineEdit, QComboBox, QSplitter,
                           QGroupBox, QFormLayout, QCheckBox, QScrollArea,
                           QDialog, QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCharFormat, QColor
import json

class TemplateListWidget(QFrame):
    """Template list widget"""
    
    template_selected = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.templates = []
        self.setup_ui()
        self.load_sample_templates()
    
    def setup_ui(self):
        """Setup template list UI"""
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
        
        title = QLabel("Template Library")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # New template button
        new_btn = QPushButton("+ New Template")
        new_btn.setStyleSheet("""
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
        new_btn.clicked.connect(self.create_new_template)
        header_layout.addWidget(new_btn)
        
        layout.addLayout(header_layout)
        
        # Category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category:"))
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All", "Meetings", "Follow-ups", "General", "Attachments"])
        self.category_filter.currentTextChanged.connect(self.filter_templates)
        filter_layout.addWidget(self.category_filter)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e1e5e9;
                border-radius: 4px;
                background-color: #fafafa;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f3f2f1;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        self.template_list.itemClicked.connect(self.on_template_selected)
        layout.addWidget(self.template_list)
    
    def load_sample_templates(self):
        """Load sample templates"""
        self.templates = [
            {
                "id": 1,
                "name": "Zoom Meeting Invite",
                "category": "Meetings",
                "subject": "Zoom Meeting with <RecipientName> — <ShortTopic>",
                "body": "Hi <RecipientName>\n\nPlease join the Zoom call at <ZoomLink> on <LocalDateTime>.\n\n<UserMessage>\n\nRegards,\n<Signature>",
                "placeholders": {
                    "ShortTopic": {"type": "string", "required": False},
                    "LocalDateTime": {"type": "datetime", "required": False},
                    "ZoomLink": {"type": "url", "required": True},
                    "UserMessage": {"type": "multiline", "required": False},
                    "Signature": {"type": "signature", "required": False}
                },
                "useSignature": True
            },
            {
                "id": 2,
                "name": "Follow-up Reminder",
                "category": "Follow-ups",
                "subject": "Following up on our previous conversation",
                "body": "Hi <RecipientName>\n\nI wanted to follow up regarding <UserMessage>. Please let me know your thoughts.\n\nBest Regards,\n<Signature>",
                "placeholders": {
                    "UserMessage": {"type": "multiline", "required": True},
                    "Signature": {"type": "signature", "required": False}
                },
                "useSignature": True
            },
            {
                "id": 3,
                "name": "Thank You Note",
                "category": "General",
                "subject": "Thank you for your time",
                "body": "Hi <RecipientName>\n\nThank you for <UserMessage>. It was a pleasure working with you.\n\nWarm Regards,\n<Signature>",
                "placeholders": {
                    "UserMessage": {"type": "string", "required": True},
                    "Signature": {"type": "signature", "required": False}
                },
                "useSignature": True
            }
        ]
        self.refresh_template_list()
    
    def on_template_saved(self, template_data: dict):
        """Handle saved template"""
        if template_data.get("id") is None:
            # New template
            template_data["id"] = len(self.templates) + 1
            self.templates.append(template_data)
        else:
            # Update existing template
            for i, template in enumerate(self.templates):
                if template["id"] == template_data["id"]:
                    self.templates[i] = template_data
                    break
        
        self.refresh_template_list()
        
        # Show success message
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self.parent(), "Template Saved", 
                              f"Template '{template_data['name']}' has been saved successfully.")
    
    def refresh_template_list(self):
        """Refresh template list display"""
        self.template_list.clear()
        
        current_filter = self.category_filter.currentText()
        
        for template in self.templates:
            if current_filter == "All" or template["category"] == current_filter:
                item_text = f"{template['name']}\n{template['category']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, template)
                self.template_list.addItem(item)
    
    def filter_templates(self):
        """Filter templates by category"""
        self.refresh_template_list()
    
    def on_template_selected(self, item):
        """Handle template selection"""
        template = item.data(Qt.ItemDataRole.UserRole)
        self.template_selected.emit(template)
    
    def create_new_template(self):
        """Create new template"""
        from ui.dialogs.template_dialog import TemplateDialog
        
        dialog = TemplateDialog(parent=self.parent())
        dialog.template_saved.connect(self.on_template_saved)
        dialog.exec()

class TemplateEditorWidget(QFrame):
    """Template editor widget"""
    
    def __init__(self):
        super().__init__()
        self.current_template = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup template editor UI"""
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
        
        self.title_label = QLabel("Select a Template")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Action buttons
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setEnabled(False)
        self.edit_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #c8c6c4;
            }
        """)
        header_layout.addWidget(self.edit_btn)
        
        self.use_btn = QPushButton("Use Template")
        self.use_btn.setEnabled(False)
        self.use_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #c8c6c4;
            }
        """)
        self.use_btn.clicked.connect(self.use_template)
        header_layout.addWidget(self.use_btn)
        
        layout.addLayout(header_layout)
        
        # Template details
        details_scroll = QScrollArea()
        details_scroll.setWidgetResizable(True)
        details_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        
        details_scroll.setWidget(self.details_widget)
        layout.addWidget(details_scroll)
    
    def set_template(self, template):
        """Set current template and update display"""
        self.current_template = template
        self.title_label.setText(template["name"])
        self.edit_btn.setEnabled(True)
        self.use_btn.setEnabled(True)
        
        # Clear previous details
        for i in reversed(range(self.details_layout.count())):
            self.details_layout.itemAt(i).widget().setParent(None)
        
        # Basic info
        info_group = QGroupBox("Template Information")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("Name:", QLabel(template["name"]))
        info_layout.addRow("Category:", QLabel(template["category"]))
        
        self.details_layout.addWidget(info_group)
        
        # Subject
        subject_group = QGroupBox("Subject")
        subject_layout = QVBoxLayout(subject_group)
        
        subject_text = QLineEdit(template["subject"])
        subject_text.setReadOnly(True)
        subject_layout.addWidget(subject_text)
        
        self.details_layout.addWidget(subject_group)
        
        # Body
        body_group = QGroupBox("Email Body")
        body_layout = QVBoxLayout(body_group)
        
        body_text = QTextEdit()
        body_text.setPlainText(template["body"])
        body_text.setReadOnly(True)
        body_text.setMaximumHeight(200)
        body_layout.addWidget(body_text)
        
        self.details_layout.addWidget(body_group)
        
        # Placeholders
        placeholders_group = QGroupBox("Placeholders")
        placeholders_layout = QVBoxLayout(placeholders_group)
        
        for name, config in template.get("placeholders", {}).items():
            placeholder_text = f"<{name}> - {config['type']}"
            if config.get("required"):
                placeholder_text += " (required)"
            
            placeholder_label = QLabel(placeholder_text)
            placeholders_layout.addWidget(placeholder_label)
        
        self.details_layout.addWidget(placeholders_group)
        
        self.details_layout.addStretch()
    
    def use_template(self):
        """Use the current template to create email"""
        if self.current_template:
            # TODO: Open email composer with template
            QMessageBox.information(self, "Template", f"Using template: {self.current_template['name']}")

class TemplatesPage(QWidget):
    """Templates page"""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("contentPage")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup templates page UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Template list (left side)
        self.template_list_widget = TemplateListWidget()
        splitter.addWidget(self.template_list_widget)
        
        # Template editor (right side)
        self.template_editor_widget = TemplateEditorWidget()
        splitter.addWidget(self.template_editor_widget)
        
        # Connect signals
        self.template_list_widget.template_selected.connect(
            self.template_editor_widget.set_template
        )
        
        # Set proportions
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
    
    def refresh(self):
        """Refresh templates page"""
        self.template_list_widget.refresh_template_list()