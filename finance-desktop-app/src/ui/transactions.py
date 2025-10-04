"""
Transaction management UI components for Finance Desktop Application
Add, edit, delete, and view transactions with AI categorization
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLineEdit, QPushButton, QLabel, QTableWidget, 
                           QTableWidgetItem, QMessageBox, QComboBox, QDateEdit,
                           QDoubleSpinBox, QHeaderView, QAbstractItemView, QMenu, QAction,
                           QDialog, QShortcut, QCalendarWidget)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer, QEvent
from PyQt5.QtGui import QFont, QColor, QKeySequence, QTextCharFormat
import sys
import os
from datetime import datetime, date
from typing import Dict, List, Any, Optional


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.client import APIClient
from utils.logger import log_user_action, log_window_event, log_validation_error

class TransactionWorker(QThread):
    """Worker thread for transaction operations"""
    
    success = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, api_client, operation, **kwargs):
        super().__init__()
        self.api_client = api_client
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        """Run transaction operation in background"""
        try:
            if self.operation == 'create':
                result = self.api_client.create_transaction(self.kwargs['data'])
                self.success.emit(result)
            elif self.operation == 'update':
                result = self.api_client.update_transaction(
                    self.kwargs['id'], 
                    self.kwargs['data']
                )
                self.success.emit(result)
            elif self.operation == 'delete':
                result = self.api_client.delete_transaction(self.kwargs['id'])
                self.success.emit(result)
            elif self.operation == 'load':
                result = self.api_client.get_transactions()
                self.success.emit(result)
            elif self.operation == 'recategorize':
                result = self.api_client.recategorize_transaction(self.kwargs['id'])
                self.success.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class AddTransactionDialog(QDialog):
    """Dialog for adding new transaction"""
    
    transaction_added = pyqtSignal(dict)
    
    def __init__(self, api_client: APIClient, categories: List[Dict], parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.categories = categories
        self.worker = None
        
        self.ai_timer = QTimer()
        self.ai_timer.setSingleShot(True)
        self.ai_timer.timeout.connect(self.get_ai_suggestion)
        
        self.initUI()
    
    def initUI(self):
        """Initialize add transaction dialog UI"""
        self.setWindowTitle('Add New Transaction')
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 35, 40, 35)
        layout.setSpacing(20)
        
        # Header section
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel('Add New Transaction')
        title.setFont(QFont('Segoe UI', 20, QFont.Bold))
        title.setStyleSheet("color: #1a202c;")
        
        subtitle = QLabel('Enter transaction details below')
        subtitle.setFont(QFont('Segoe UI', 11))
        subtitle.setStyleSheet("color: #64748b;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_widget)
        layout.addSpacing(10)
        
        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        # Description field
        desc_container = QWidget()
        desc_layout = QVBoxLayout(desc_container)
        desc_layout.setSpacing(8)
        desc_layout.setContentsMargins(0, 0, 0, 0)
        
        desc_label = QLabel('Description')
        desc_label.setFont(QFont('Segoe UI', 11, QFont.Medium))
        desc_label.setStyleSheet("color: #2d3748;")
        
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText('e.g., Lunch at restaurant')
        self.description_edit.setFont(QFont('Segoe UI', 12))
        self.description_edit.setFixedHeight(45)
        self.description_edit.textChanged.connect(self.on_description_changed)
        
        self.ai_suggestion_label = QLabel()
        self.ai_suggestion_label.setFont(QFont('Segoe UI', 10))
        self.ai_suggestion_label.setStyleSheet("color: #3498db; padding: 4px 0;")
        self.ai_suggestion_label.setWordWrap(True)
        self.ai_suggestion_label.hide()
        
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.description_edit)
        desc_layout.addWidget(self.ai_suggestion_label)
        
        form_layout.addWidget(desc_container)
        
        # Amount field
        amount_container = QWidget()
        amount_layout = QVBoxLayout(amount_container)
        amount_layout.setSpacing(8)
        amount_layout.setContentsMargins(0, 0, 0, 0)
        
        amount_label = QLabel('Amount (IDR)')
        amount_label.setFont(QFont('Segoe UI', 11, QFont.Medium))
        amount_label.setStyleSheet("color: #2d3748;")
        
        self.amount_spinbox = QDoubleSpinBox()
        self.amount_spinbox.setRange(-999999.99, 999999.99)
        self.amount_spinbox.setDecimals(2)
        self.amount_spinbox.setPrefix('Rp ')
        self.amount_spinbox.setFont(QFont('Segoe UI', 12))
        self.amount_spinbox.setFixedHeight(45)
        self.amount_spinbox.setGroupSeparatorShown(True)
        
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_spinbox)
        
        form_layout.addWidget(amount_container)
        
        # Date field
        date_container = QWidget()
        date_layout = QVBoxLayout(date_container)
        date_layout.setSpacing(8)
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        date_label = QLabel('Date')
        date_label.setFont(QFont('Segoe UI', 11, QFont.Medium))
        date_label.setStyleSheet("color: #2d3748;")
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFont(QFont('Segoe UI', 12))
        self.date_edit.setFixedHeight(45)
        self.date_edit.setDisplayFormat('dd MMMM yyyy')
        # Prepare calendar styling flag (for popup QCalendarWidget styling)
        self._calendar_styled = False
        self.date_edit.installEventFilter(self)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        
        form_layout.addWidget(date_container)
        
        # Category field
        category_container = QWidget()
        category_layout = QVBoxLayout(category_container)
        category_layout.setSpacing(8)
        category_layout.setContentsMargins(0, 0, 0, 0)
        
        category_label = QLabel('Category')
        category_label.setFont(QFont('Segoe UI', 11, QFont.Medium))
        category_label.setStyleSheet("color: #2d3748;")
        
        self.category_combo = QComboBox()
        self.category_combo.addItem('-- Select Category --', None)
        for category in self.categories:
            self.category_combo.addItem(category['name'], category['id'])
        self.category_combo.setFont(QFont('Segoe UI', 12))
        self.category_combo.setFixedHeight(45)
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        
        form_layout.addWidget(category_container)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.setFixedHeight(48)
        self.cancel_btn.setFont(QFont('Segoe UI', 12, QFont.Medium))
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setObjectName('cancel_btn')
        
        self.save_btn = QPushButton('Save Transaction')
        self.save_btn.setFixedHeight(48)
        self.save_btn.setFont(QFont('Segoe UI', 12, QFont.Bold))
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self.save_transaction)
        self.save_btn.setObjectName('save_btn')
        
        button_layout.addWidget(self.cancel_btn, 1)
        button_layout.addWidget(self.save_btn, 2)
        
        layout.addLayout(button_layout)
        
        # Set layout
        self.setLayout(layout)
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            
            QLineEdit, QDoubleSpinBox, QDateEdit, QComboBox {
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                color: #2d3748;
            }
            
            QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
                border-color: #667eea;
                outline: none;
            }
            
            QLineEdit:hover, QDoubleSpinBox:hover, QDateEdit:hover, QComboBox:hover {
                border-color: #cbd5e0;
            }
            
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
                margin-right: 8px;
            }
            
            QPushButton {
                border: none;
                border-radius: 8px;
                font-weight: 600;
            }
            
            QPushButton#save_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
            }
            
            QPushButton#save_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
            
            QPushButton#save_btn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4c51bf, stop:1 #553c9a);
            }
            
            QPushButton#save_btn:disabled {
                background-color: #cbd5e0;
            }
            
            QPushButton#cancel_btn {
                background-color: #f1f5f9;
                color: #475569;
                border: 2px solid #e2e8f0;
            }
            
            QPushButton#cancel_btn:hover {
                background-color: #e2e8f0;
                color: #334155;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar { background: #ffffff; }
            QCalendarWidget QToolButton { color: #1a202c; font-weight:600; background: transparent; }
            QCalendarWidget QToolButton:hover { background:#edf2f7; border-radius:4px; }
            QCalendarWidget QToolButton::menu-indicator { image: none; width:0; }
            QMenu { 
                background: #ffffff; 
                border: 1px solid #e2e8f0; 
                padding: 6px 0; 
                border-radius: 8px; 
            }
            QMenu::item { 
                background: transparent; 
                padding: 6px 18px; 
                color: #1a202c; 
                font-family: 'Segoe UI'; 
                font-size: 13px; 
            }
            QMenu::item:selected { 
                background: #edf2f7; 
                color: #1a202c; 
            }
            QMenu::separator { height:1px; background:#e2e8f0; margin:4px 0; }
            QCalendarWidget QAbstractItemView { 
                background: #ffffff; 
                selection-background-color: #3182ce; 
                selection-color: #ffffff; 
                outline: none; 
                gridline-color: #e2e8f0; 
            }
            /* Week headers */
            QCalendarWidget QTableView { alternate-background-color:#ffffff; }
        """)

    def eventFilter(self, obj, event):
        if obj is self.date_edit and event.type() == QEvent.Show and not self._calendar_styled:
            popup = self.date_edit.findChild(QWidget, "qt_calendar_popup")
            if popup:
                cal_widget = popup.findChild(QCalendarWidget)
                if cal_widget:
                    cal_widget.setStyleSheet(
                        """
                        QCalendarWidget QWidget#qt_calendar_navigationbar { background: #ffffff; }
                        QCalendarWidget QToolButton { color: #1a202c; font-weight:600; background: transparent; }
                        QCalendarWidget QToolButton:hover { background:#edf2f7; border-radius:4px; }
                        QCalendarWidget QToolButton::menu-indicator { image: none; width:0; }
                        QMenu { background:#ffffff; border:1px solid #e2e8f0; padding:6px 0; border-radius:8px; }
                        QMenu::item { background:transparent; padding:6px 18px; color:#1a202c; font-family:'Segoe UI'; font-size:13px; }
                        QMenu::item:selected { background:#edf2f7; color:#1a202c; }
                        QMenu::separator { height:1px; background:#e2e8f0; margin:4px 0; }
                        QCalendarWidget QAbstractItemView { background:#ffffff; selection-background-color:#3182ce; selection-color:#ffffff; outline:none; }
                        QCalendarWidget QTableView { alternate-background-color:#ffffff; }
                        """
                    )

                    fmt_weekend = QTextCharFormat()
                    fmt_weekend.setForeground(QColor('#dc2626'))
                    cal_widget.setWeekdayTextFormat(Qt.Saturday, fmt_weekend)
                    cal_widget.setWeekdayTextFormat(Qt.Sunday, fmt_weekend)
            self._calendar_styled = True
        return super().eventFilter(obj, event)
        
    
    def save_transaction(self):
        """Save new transaction"""
        log_user_action("save_transaction", "AddTransactionDialog")
        
        # Validate inputs
        description = self.description_edit.text().strip()
        if not description:
            log_validation_error("AddTransactionDialog", "description", "empty description")
            QMessageBox.warning(self, 'Validation Error', 'Please enter a description')
            self.description_edit.setFocus()
            return
        
        amount = self.amount_spinbox.value()
        if amount == 0:
            log_validation_error("AddTransactionDialog", "amount", "zero amount")
            QMessageBox.warning(self, 'Validation Error', 'Please enter a non-zero amount')
            self.amount_spinbox.setFocus()
            return
        
        # Prepare transaction data
        transaction_date = self.date_edit.date().toPyDate()
        
        transaction_data = {
            'description': description,
            'amount': amount,
            'transaction_date': transaction_date.isoformat() + 'T00:00:00Z'
        }
        
        # Disable form during save
        self.set_loading(True)
        
        # Start save operation in background
        self.worker = TransactionWorker(self.api_client, 'create', data=transaction_data)
        self.worker.success.connect(self.on_save_success)
        self.worker.error.connect(self.on_save_error)
        self.worker.start()
    
    def on_save_success(self, result):
        """Handle successful save"""
        self.set_loading(False)
        log_user_action("transaction_saved", "AddTransactionDialog", {"transaction_id": result.get('id')})
        self.transaction_added.emit(result)
        QMessageBox.information(self, 'Success', 'Transaction saved successfully!')
        self.accept()
    
    def on_save_error(self, error_message):
        """Handle save error"""
        self.set_loading(False)
        QMessageBox.critical(self, 'Error', f'Failed to save transaction: {error_message}')
    
    def on_description_changed(self):
        # Stop previous timer
        self.ai_timer.stop()
        
        description = self.description_edit.text().strip()
        if len(description) >= 3:
            # Start timer for debounced AI suggestion
            self.ai_timer.start(1000)
            self.ai_suggestion_label.setText("🤖 Getting AI suggestion...")
            self.ai_suggestion_label.show()
        else:
            self.ai_suggestion_label.hide()
    
    def get_ai_suggestion(self):
        description = self.description_edit.text().strip()
        if not description:
            self.ai_suggestion_label.hide()
            return
        
        try:
            # Get AI suggestion from backend
            suggestion_data = self.api_client.suggest_categories(description)
            log_user_action("ai_suggestion_response", "AddTransactionDialog", suggestion_data)

            category = None
            confidence = 0

            if suggestion_data and suggestion_data.get('suggestions'):
                suggestions = suggestion_data['suggestions']
                if isinstance(suggestions, list) and len(suggestions) > 0:
                    first_suggestion = suggestions[0]
                    category = first_suggestion.get('category') or first_suggestion.get('name')
                    confidence = first_suggestion.get('confidence', 0)

            elif suggestion_data and 'predicted_category' in suggestion_data:
                category = suggestion_data['predicted_category']
                confidence = suggestion_data.get('confidence', 0)

            elif suggestion_data and 'category' in suggestion_data:
                category = suggestion_data['category']
                confidence = suggestion_data.get('confidence', 0)
            
            if category and category != "Unknown":
                if confidence > 0:
                    self.ai_suggestion_label.setText(
                        f"🤖 AI suggests: {category} ({confidence:.0%} confidence)"
                    )
                else:
                    self.ai_suggestion_label.setText(f"🤖 AI suggests: {category}")
                
                # Auto-select the suggested category if confidence is high
                if confidence >= 0.8:
                    self.auto_select_category(category)
                    
            else:
                if suggestion_data and suggestion_data.get('count', 0) == 0:
                    self.ai_suggestion_label.setText("🤖 New transaction type - please select category manually")
                else:
                    self.ai_suggestion_label.setText("🤖 No AI suggestion available")
                
        except Exception as e:
            log_user_action("ai_suggestion_error", "AddTransactionDialog", {"error": str(e)})
            self.ai_suggestion_label.setText("🤖 AI service temporarily unavailable")
    
    def auto_select_category(self, category_name: str):
        for i in range(self.category_combo.count()):
            if self.category_combo.itemText(i) == category_name:
                self.category_combo.setCurrentIndex(i)
                return
        
        # If category doesn't exist, create it and add to dropdown
        self.create_and_select_category(category_name)
    
    def create_and_select_category(self, category_name: str):
        """Create a new category and add it to the dropdown"""
        sanitized_name = category_name.replace('&', 'dan').replace('/', ' ').strip()
        for category in self.categories:
            if category['name'].lower() == sanitized_name.lower():
                # Found existing category, select it
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemData(i) == category['id']:
                        self.category_combo.setCurrentIndex(i)
                        self.ai_suggestion_label.setText(
                            f"🤖 Selected existing category: {category['name']}"
                        )
                        return
        
        # Category doesn't exist locally, try to create it
        try:
            result = self.api_client.create_category(sanitized_name)
            
            if result and 'category' in result:
                new_category = result['category']
                # Add to the local categories list
                self.categories.append({
                    'id': new_category['id'], 
                    'name': new_category['name']
                })
                
                # Add to dropdown and select it
                self.category_combo.addItem(new_category['name'], new_category['id'])
                self.category_combo.setCurrentIndex(self.category_combo.count() - 1)
                
                # Update the AI suggestion to show it was created
                self.ai_suggestion_label.setText(
                    f"🤖 Created and selected category: {new_category['name']}"
                )
                
        except Exception as e:
            self.refresh_categories_and_select(sanitized_name)
    
    def refresh_categories_and_select(self, category_name: str):
        """Refresh categories from API and try to select the given category"""
        try:
            # Refresh categories from backend
            result = self.api_client.get_categories()
            if result and 'categories' in result:
                self.categories = result['categories']
                
                # Rebuild dropdown
                self.category_combo.clear()
                self.category_combo.addItem('-- Select Category --', None)
                for category in self.categories:
                    self.category_combo.addItem(category['name'], category['id'])
                
                # Try to select the desired category
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemText(i).lower() == category_name.lower():
                        self.category_combo.setCurrentIndex(i)
                        self.ai_suggestion_label.setText(
                            f"🤖 Found and selected category: {self.category_combo.itemText(i)}"
                        )
                        return
            
            self.ai_suggestion_label.setText(
                f"🤖 AI suggests: {category_name} (will be created when you save)"
            )
            
        except Exception as e:
            self.ai_suggestion_label.setText(
                f"🤖 AI suggests: {category_name} (category will be auto-created)"
            )
    
    def set_loading(self, loading: bool):
        """Set loading state"""
        self.description_edit.setEnabled(not loading)
        self.amount_spinbox.setEnabled(not loading)
        self.date_edit.setEnabled(not loading)
        self.category_combo.setEnabled(not loading)
        self.save_btn.setEnabled(not loading)
        self.cancel_btn.setEnabled(not loading)
        
        if loading:
            self.save_btn.setText('Saving...')
        else:
            self.save_btn.setText('Save Transaction')

class TransactionListWidget(QWidget):
    """Widget for displaying and managing transactions"""
    
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.transactions = []
        self.filtered_transactions = []
        self.categories = []
        self.worker = None
        self.search_bar = None
        self.search_visible = False
        # Refresh debounce/cooldown
        self.refresh_cooldown_ms = 800
        self._refresh_cooldown_timer = QTimer(self)
        self._refresh_cooldown_timer.setSingleShot(True)
        self._refresh_cooldown_timer.timeout.connect(self._end_refresh_cooldown)
        self.initUI()
        self.load_categories()
        self.load_transactions()
    
    def initUI(self):
        """Initialize transaction list UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        title = QLabel('Transaction List')
        title.setFont(QFont('Segoe UI', 26, QFont.Bold))
        title.setStyleSheet("color: #1a202c;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton('Refresh')
        self.refresh_btn.setFixedHeight(44)
        self.refresh_btn.setFont(QFont('Segoe UI', 11, QFont.Medium))
        self.refresh_btn.clicked.connect(self.load_transactions)
        self.refresh_btn.setObjectName('refresh_btn')
        
        self.add_btn = QPushButton('+ Add Transaction')
        self.add_btn.setFixedHeight(44)
        self.add_btn.setFont(QFont('Segoe UI', 11, QFont.Bold))
        self.add_btn.clicked.connect(self.show_add_dialog)
        self.add_btn.setObjectName('add_btn')
        
        header_layout.addWidget(self.refresh_btn)
        header_layout.addWidget(self.add_btn)
        layout.addLayout(header_layout)

        # Search bar (hidden initially)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search (description or category) – Ctrl+F to toggle, Esc to close")
        self.search_bar.setFixedHeight(40)
        self.search_bar.setVisible(False)
        self.search_bar.textChanged.connect(self.apply_filter)
        self.search_bar.installEventFilter(self)
        layout.addWidget(self.search_bar)
        
        # Transaction table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'Date', 'Description', 'Amount', 'Category', 'Actions', 'ID'
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        
        self.table.setColumnWidth(0, 150)  # Date
        self.table.setColumnWidth(2, 170)  # Amount
        self.table.setColumnWidth(3, 160)  # Category
        self.table.setColumnWidth(4, 140)  # Actions
        
        self.table.setWordWrap(True)
        self.table.verticalHeader().setDefaultSectionSize(52)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Hide ID column
        self.table.setColumnHidden(5, True)
        
        # Set table properties
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        header.sectionClicked.connect(self.on_header_clicked)
        self.sort_state = {"section": None, "order": Qt.AscendingOrder}

        # Shortcuts with application-wide context for reliability
        self.shortcut_refresh = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcut_refresh.setContext(Qt.ApplicationShortcut)
        self.shortcut_refresh.activated.connect(self._shortcut_refresh_triggered)

        self.shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_new.setContext(Qt.ApplicationShortcut)
        self.shortcut_new.activated.connect(self._shortcut_new_triggered)

        self.shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_search.setContext(Qt.ApplicationShortcut)
        self.shortcut_search.activated.connect(self.toggle_search)
        
        layout.addWidget(self.table)
        
        # Set layout
        self.setLayout(layout)
        
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton {
                padding: 10px 24px;
                border: none;
                border-radius: 8px;
            }
            
            QPushButton#add_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
            }
            
            QPushButton#add_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
            
            QPushButton#refresh_btn {
                background-color: white;
                color: #64748b;
                border: 2px solid #e2e8f0;
            }
            
            QPushButton#refresh_btn:hover {
                background-color: #f1f5f9;
                color: #475569;
                border-color: #cbd5e0;
            }
            
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background-color: white;
                selection-background-color: #e0e7ff;
                gridline-color: transparent;
            }

            QTableWidget QWidget { background: transparent; }
            
            QTableWidget::item {
                padding: 12px 14px;
                border-bottom: 1px solid #f1f5f9;
                color: #2d3748;
                min-height: 40px;
            }
            
            QTableWidget::item:selected {
                background-color: #e0e7ff;
                color: #2d3748;
            }
            
            QHeaderView::section {
                background-color: #f8fafc;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 14px 12px;
                font-weight: 600;
                color: #475569;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            QTableWidget::item:alternate {
                background-color: #f8fafc;
            }
            QHeaderView {
                background-color: #f8fafc;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                padding: 14px 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:horizontal {
                border-right: 1px solid #e2e8f0;
            }
            QTableCornerButton::section {
                background-color: #f8fafc;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
            }
        """)
    
    def load_categories(self):
        """Load categories from backend"""
        try:
            result = self.api_client.get_categories()
            self.categories = result.get('data', [])
        except Exception as e:
            log_user_action("load_categories_error", "TransactionListWidget", {"error": str(e)})
    
    def load_transactions(self):
        """Load transactions from backend"""
        if self.refresh_btn.isEnabled():
            log_user_action("load_transactions", "TransactionListWidget")
            self.set_loading(True)

            self.worker = TransactionWorker(self.api_client, 'load')
            self.worker.success.connect(self.on_load_success)
            self.worker.error.connect(self.on_load_error)
            self.worker.start()

            self._begin_refresh_cooldown()
        else:
            log_user_action("refresh_debounced", "TransactionListWidget")
    
    def on_load_success(self, result):
        """Handle successful load"""
        self.set_loading(False)
        self.transactions = result.get('transactions', []) or []
        self.filtered_transactions = self.transactions
        self.populate_table()
        log_user_action("transactions_loaded", "TransactionListWidget", 
                       {"count": len(self.transactions)})
    
    def on_load_error(self, error_message):
        """Handle load error"""
        self.set_loading(False)
        QMessageBox.critical(self, 'Error', f'Failed to load transactions: {error_message}')
    
    def populate_table(self):
        data = self.filtered_transactions if self.filtered_transactions is not None else self.transactions
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(data))
        for row, transaction in enumerate(data):
            # Date
            date_str = transaction.get('transaction_date', '')[:10]
            date_item = QTableWidgetItem(date_str)
            date_item.setFont(QFont('Segoe UI', 10))
            self.table.setItem(row, 0, date_item)
            
            # Description
            description_text = transaction.get('description', '')
            desc_item = QTableWidgetItem(description_text)
            desc_item.setFont(QFont('Segoe UI', 11))
            desc_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            self.table.setItem(row, 1, desc_item)

            if len(description_text) > 90:
                self.table.setRowHeight(row, 78)
            elif len(description_text) > 45:
                self.table.setRowHeight(row, 64)
            else:
                self.table.setRowHeight(row, 46)
            
            # Amount
            amount = transaction.get('amount', 0)
            amount_item = QTableWidgetItem(f"Rp {amount:,.2f}")
            amount_item.setFont(QFont('Segoe UI', 11, QFont.Bold))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if amount < 0:
                amount_item.setForeground(QColor('#ef4444'))
            else:
                amount_item.setForeground(QColor('#10b981'))
            self.table.setItem(row, 2, amount_item)
            
            # Category
            category_name = transaction.get('category_name', 'Uncategorized')
            if not category_name or category_name == '':
                category_name = 'Uncategorized'
            category_item = QTableWidgetItem(category_name)
            category_item.setFont(QFont('Segoe UI', 11))
            self.table.setItem(row, 3, category_item)
            
            actions_widget = self.create_action_buttons(transaction)
            self.table.setCellWidget(row, 4, actions_widget)
            
            id_item = QTableWidgetItem(str(transaction.get('id', '')))
            self.table.setItem(row, 5, id_item)
        
        self.table.setSortingEnabled(True)

    def apply_filter(self):
        term = self.search_bar.text().strip().lower()
        if not term:
            self.filtered_transactions = self.transactions
        else:
            self.filtered_transactions = [t for t in self.transactions if term in (t.get('description','').lower()) or term in (t.get('category_name','') or '').lower()]
        self.populate_table()

    def toggle_search(self):
        self.search_visible = not self.search_visible
        self.search_bar.setVisible(self.search_visible)
        if self.search_visible:
            self.search_bar.setFocus()
        else:
            self.search_bar.clear()
        log_user_action("toggle_search", "TransactionListWidget", {"visible": self.search_visible})

    def eventFilter(self, obj, event):
        if obj == self.search_bar and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape and self.search_visible:
                self.toggle_search()
                return True
        return super().eventFilter(obj, event)
    
    def create_action_buttons(self, transaction):
        widget = QWidget()
        widget.setAttribute(Qt.WA_StyledBackground, True)
        widget.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addStretch(1)

        btn_style = """
            QPushButton {
                border: none;
                background: transparent;
                font-weight: 600;
                padding: 0px;
            }
            QPushButton:hover {
                background: rgba(99,102,241,0.10);
                border-radius: 6px;
            }
        """

        recategorize_btn = QPushButton('🤖')
        recategorize_btn.setToolTip('Recategorize with AI')
        recategorize_btn.setFixedSize(34, 34)
        recategorize_btn.setFont(QFont('Segoe UI', 16))
        recategorize_btn.setStyleSheet(btn_style)
        recategorize_btn.setCursor(Qt.PointingHandCursor)
        recategorize_btn.clicked.connect(lambda: self.recategorize_transaction(transaction['id']))

        delete_btn = QPushButton('🗑️')
        delete_btn.setToolTip('Delete transaction')
        delete_btn.setFixedSize(34, 34)
        delete_btn.setFont(QFont('Segoe UI', 16))
        delete_btn.setStyleSheet(btn_style)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.delete_transaction(transaction['id']))

        layout.addWidget(recategorize_btn)
        layout.addWidget(delete_btn)
        layout.addStretch(1)
        widget.setMinimumHeight(40)
        return widget
    
    def show_add_dialog(self):
        """Show add transaction dialog"""
        log_user_action("show_add_transaction_dialog", "TransactionListWidget")
        
        dialog = AddTransactionDialog(self.api_client, self.categories, self)
        dialog.transaction_added.connect(self.on_transaction_added)
        dialog.exec_()
    
    def on_transaction_added(self, result):
        """Handle new transaction added"""
        log_user_action("transaction_added", "TransactionListWidget")
        self.load_transactions()
    
    def recategorize_transaction(self, transaction_id):
        """Recategorize transaction using AI"""
        log_user_action("recategorize_transaction", "TransactionListWidget", 
                       {"transaction_id": transaction_id})
        
        # Confirm action
        reply = QMessageBox.question(
            self, 
            'Confirm Recategorization',
            'Use AI to automatically categorize this transaction?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Start recategorize operation
            self.worker = TransactionWorker(self.api_client, 'recategorize', id=transaction_id)
            self.worker.success.connect(self.on_recategorize_success)
            self.worker.error.connect(self.on_recategorize_error)
            self.worker.start()
    
    def on_recategorize_success(self, result):
        """Handle successful recategorization"""
        log_user_action("recategorize_success", "TransactionListWidget")
        QMessageBox.information(self, 'Success', 'Transaction recategorized successfully!')
        self.load_transactions()
    
    def on_recategorize_error(self, error_message):
        """Handle recategorization error"""
        QMessageBox.critical(self, 'Error', f'Failed to recategorize: {error_message}')
    
    def delete_transaction(self, transaction_id):
        """Delete transaction"""
        log_user_action("delete_transaction", "TransactionListWidget", 
                       {"transaction_id": transaction_id})
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            'Confirm Deletion',
            'Are you sure you want to delete this transaction?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Start delete operation
            self.worker = TransactionWorker(self.api_client, 'delete', id=transaction_id)
            self.worker.success.connect(self.on_delete_success)
            self.worker.error.connect(self.on_delete_error)
            self.worker.start()
    
    def on_delete_success(self, result):
        """Handle successful deletion"""
        log_user_action("delete_success", "TransactionListWidget")
        QMessageBox.information(self, 'Success', 'Transaction deleted successfully!')
        self.load_transactions()
    
    def on_delete_error(self, error_message):
        """Handle deletion error"""
        QMessageBox.critical(self, 'Error', f'Failed to delete transaction: {error_message}')
    
    def set_loading(self, loading: bool):
        """Set loading state"""
        self.add_btn.setEnabled(not loading)
        self.refresh_btn.setEnabled((not loading) and (not self._refresh_cooldown_timer.isActive()))
        self.table.setEnabled(not loading)
        
        if loading:
            self.refresh_btn.setText('Loading...')
        else:
            self.refresh_btn.setText('Refresh')

    # ----- Keyboard shortcuts -----
    def keyPressEvent(self, event):
        """
        Ctrl+R -> Refresh transactions
        Ctrl+N -> Open add transaction dialog
        """
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_R and self.refresh_btn.isEnabled():
                self.load_transactions()
                event.accept()
                return
            if event.key() == Qt.Key_N and self.add_btn.isEnabled():
                self.show_add_dialog()
                event.accept()
                return
            if event.key() == Qt.Key_F:
                self.toggle_search()
                event.accept()
                return
        super().keyPressEvent(event)

    def _shortcut_refresh_triggered(self):
        log_user_action("shortcut_refresh", "TransactionListWidget")
        self.load_transactions()
    def _begin_refresh_cooldown(self):
        if not self._refresh_cooldown_timer.isActive():
            self._refresh_cooldown_timer.start(self.refresh_cooldown_ms)

    def _end_refresh_cooldown(self):
        # Only re-enable if not currently loading
        if self.refresh_btn.text() != 'Loading...':
            self.refresh_btn.setEnabled(True)
        log_user_action("refresh_cooldown_end", "TransactionListWidget")

    def _shortcut_new_triggered(self):
        log_user_action("shortcut_new", "TransactionListWidget")
        if self.add_btn.isEnabled():
            self.show_add_dialog()


    # ----- Sorting helpers -----
    def on_header_clicked(self, section: int):
        current_section = self.sort_state.get("section")
        if current_section == section:
            new_order = Qt.DescendingOrder if self.sort_state.get("order") == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            new_order = Qt.AscendingOrder
        self.sort_state = {"section": section, "order": new_order}
        self.table.sortItems(section, new_order)
        self.update_sort_indicators()

    def update_sort_indicators(self):
        header = self.table.horizontalHeader()
        active_section = self.sort_state.get("section")
        order = self.sort_state.get("order")
        arrow_up = ""
        arrow_down = ""
        for col in range(self.table.columnCount()):
            item_text = self.table.horizontalHeaderItem(col).text().split(" ")

            if item_text and item_text[-1] in (arrow_up, arrow_down):
                item_text = item_text[:-1]
            base = " ".join(item_text)
            if col == active_section:
                arrow = arrow_up if order == Qt.AscendingOrder else arrow_down
                self.table.horizontalHeaderItem(col).setText(f"{base} {arrow}")

                font = self.table.horizontalHeaderItem(col).font()
                font.setBold(True)
                self.table.horizontalHeaderItem(col).setFont(font)
            else:
                self.table.horizontalHeaderItem(col).setText(base)
                font = self.table.horizontalHeaderItem(col).font()
                font.setBold(False)
                self.table.horizontalHeaderItem(col).setFont(font)