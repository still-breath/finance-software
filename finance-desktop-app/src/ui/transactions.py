"""
Transaction management UI components for Finance Desktop Application
Add, edit, delete, and view transactions with AI categorization
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLineEdit, QPushButton, QLabel, QTableWidget, 
                           QTableWidgetItem, QMessageBox, QComboBox, QDateEdit,
                           QDoubleSpinBox, QHeaderView, QAbstractItemView, QMenu, QAction)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor
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

class AddTransactionDialog(QWidget):
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
        self.setFixedSize(480, 550)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        # Title
        title = QLabel('💳 Add New Transaction')
        title_font = QFont('Segoe UI', 22, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1a202c; margin-bottom: 10px;")
        layout.addWidget(title)
        
        subtitle = QLabel('Enter transaction details below')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #64748b; font-size: 12px; margin-bottom: 15px;")
        layout.addWidget(subtitle)
        
        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(18)
        
        # Description field
        desc_label = QLabel('Description')
        desc_label.setFont(QFont('Segoe UI', 11, QFont.Medium))
        desc_label.setStyleSheet("color: #2d3748; font-weight: 600;")
        form_layout.addWidget(desc_label)
        
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText('Enter transaction description')
        self.description_edit.setFont(QFont('Segoe UI', 12))
        self.description_edit.textChanged.connect(self.on_description_changed)
        form_layout.addWidget(self.description_edit)
        
        self.ai_suggestion_label = QLabel()
        self.ai_suggestion_label.setFont(QFont('Segoe UI', 10))
        self.ai_suggestion_label.setStyleSheet("color: #3498db; margin-top: 5px;")
        self.ai_suggestion_label.hide()
        form_layout.addWidget(self.ai_suggestion_label)
        
        # Amount field
        amount_label = QLabel('Amount')
        amount_label.setFont(QFont('Segoe UI', 11, QFont.Medium))
        amount_label.setStyleSheet("color: #2d3748; font-weight: 600;")
        form_layout.addWidget(amount_label)
        
        self.amount_spinbox = QDoubleSpinBox()
        self.amount_spinbox.setRange(-999999.99, 999999.99)
        self.amount_spinbox.setDecimals(2)
        self.amount_spinbox.setSuffix(' IDR')
        self.amount_spinbox.setFont(QFont('Segoe UI', 12))
        form_layout.addWidget(self.amount_spinbox)
        
        # Date field
        date_label = QLabel('Date')
        date_label.setFont(QFont('Segoe UI', 11, QFont.Medium))
        date_label.setStyleSheet("color: #2d3748; font-weight: 600;")
        form_layout.addWidget(date_label)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFont(QFont('Segoe UI', 12))
        form_layout.addWidget(self.date_edit)
        
        # Category field
        category_label = QLabel('Category')
        category_label.setFont(QFont('Segoe UI', 11, QFont.Medium))
        category_label.setStyleSheet("color: #2d3748; font-weight: 600;")
        form_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem('-- Select Category --', None)
        for category in self.categories:
            self.category_combo.addItem(category['name'], category['id'])
        self.category_combo.setFont(QFont('Segoe UI', 12))
        form_layout.addWidget(self.category_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.save_btn = QPushButton('Save Transaction')
        self.save_btn.setFixedHeight(48)
        self.save_btn.setFont(QFont('Segoe UI', 13, QFont.Bold))
        self.save_btn.clicked.connect(self.save_transaction)
        
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.setFixedHeight(48)
        self.cancel_btn.setFont(QFont('Segoe UI', 13))
        self.cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Set layout
        self.setLayout(layout)
        
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f8fafc, stop:1 #e2e8f0);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLineEdit, QDoubleSpinBox, QDateEdit, QComboBox {
                padding: 14px 18px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 13px;
                background-color: white;
                color: #2d3748;
            }
            
            QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
                border-color: #667eea;
                background-color: white;
            }
            
            QLineEdit:hover, QDoubleSpinBox:hover, QDateEdit:hover, QComboBox:hover {
                border-color: #cbd5e0;
            }
            
            QPushButton {
                padding: 12px 20px;
                font-size: 13px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            
            QPushButton#save_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #10b981, stop:1 #059669);
                color: white;
            }
            
            QPushButton#save_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #059669, stop:1 #047857);
            }
            
            QPushButton#cancel_btn {
                background-color: white;
                color: #64748b;
                border: 2px solid #e2e8f0;
            }
            
            QPushButton#cancel_btn:hover {
                background-color: #f56565;
                color: white;
                border-color: #f56565;
            }
        """)
        
        self.save_btn.setObjectName('save_btn')
        self.cancel_btn.setObjectName('cancel_btn')
    
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
        category_id = self.category_combo.currentData()
        
        transaction_data = {
            'description': description,
            'amount': amount,
            'transaction_date': transaction_date.isoformat(),
            'category_id': category_id
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
        self.close()
    
    def on_save_error(self, error_message):
        """Handle save error"""
        self.set_loading(False)
        QMessageBox.critical(self, 'Error', f'Failed to save transaction: {error_message}')
    
    def on_description_changed(self):
        # Stop previous timer
        self.ai_timer.stop()
        
        description = self.description_edit.text().strip()
        if len(description) >= 3:  # Only suggest for descriptions with 3+ characters
            # Start timer for debounced AI suggestion
            self.ai_timer.start(1000)  # 1 second delay
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
            if suggestion_data and 'predicted_category' in suggestion_data:
                category = suggestion_data['predicted_category']
                confidence = suggestion_data.get('confidence', 0)
                
                self.ai_suggestion_label.setText(
                    f"🤖 AI suggests: {category} ({confidence:.0%} confidence)"
                )
                
                # Auto-select the suggested category if confidence is high
                if confidence >= 0.8:
                    self.auto_select_category(category)
                    
            else:
                self.ai_suggestion_label.setText("🤖 No AI suggestion available")
                
        except Exception as e:
            log_user_action("ai_suggestion_error", "AddTransactionDialog", {"error": str(e)})
            self.ai_suggestion_label.setText("🤖 AI suggestion unavailable")
    
    def auto_select_category(self, category_name: str):
        for i in range(self.category_combo.count()):
            if self.category_combo.itemText(i) == category_name:
                self.category_combo.setCurrentIndex(i)
                break
    
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
        self.categories = []
        self.worker = None
        self.initUI()
        self.load_categories()
        self.load_transactions()
    
    def initUI(self):
        """Initialize transaction list UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel('💳 Transactions')
        title_font = QFont('Segoe UI', 24, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #1a202c;")
        
        self.add_btn = QPushButton('+ Add Transaction')
        self.add_btn.setFixedHeight(42)
        self.add_btn.setFont(QFont('Segoe UI', 12, QFont.Bold))
        self.add_btn.clicked.connect(self.show_add_dialog)
        
        self.refresh_btn = QPushButton('🔄 Refresh')
        self.refresh_btn.setFixedHeight(42)
        self.refresh_btn.setFont(QFont('Segoe UI', 12))
        self.refresh_btn.clicked.connect(self.load_transactions)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Transaction table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'Date', 'Description', 'Amount', 'Category', 'Actions', 'ID'
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # Hide ID column
        self.table.setColumnHidden(5, True)
        
        # Set table properties
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)
        
        # Set layout
        self.setLayout(layout)
        
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton {
                padding: 10px 20px;
                font-size: 12px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
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
            }
            
            QTableWidget {
                border: none;
                border-radius: 12px;
                background-color: white;
                selection-background-color: #e0e7ff;
                gridline-color: #f1f5f9;
            }
            
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            
            QHeaderView::section {
                background-color: #f8fafc;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 12px 8px;
                font-weight: bold;
                color: #475569;
                font-size: 12px;
            }
        """)
        
        self.add_btn.setObjectName('add_btn')
        self.refresh_btn.setObjectName('refresh_btn')
    
    def load_categories(self):
        """Load categories from backend"""
        try:
            result = self.api_client.get_categories()
            self.categories = result.get('data', [])
        except Exception as e:
            log_user_action("load_categories_error", "TransactionListWidget", {"error": str(e)})
    
    def load_transactions(self):
        """Load transactions from backend"""
        log_user_action("load_transactions", "TransactionListWidget")
        
        # Disable controls during loading
        self.set_loading(True)
        
        # Start load operation in background
        self.worker = TransactionWorker(self.api_client, 'load')
        self.worker.success.connect(self.on_load_success)
        self.worker.error.connect(self.on_load_error)
        self.worker.start()
    
    def on_load_success(self, result):
        """Handle successful load"""
        self.set_loading(False)
        self.transactions = result.get('data', [])
        self.populate_table()
        log_user_action("transactions_loaded", "TransactionListWidget", 
                       {"count": len(self.transactions)})
    
    def on_load_error(self, error_message):
        """Handle load error"""
        self.set_loading(False)
        QMessageBox.critical(self, 'Error', f'Failed to load transactions: {error_message}')
    
    def populate_table(self):
        """Populate transaction table with data"""
        self.table.setRowCount(len(self.transactions))
        
        for row, transaction in enumerate(self.transactions):
            # Date
            date_str = transaction.get('transaction_date', '')[:10]
            date_item = QTableWidgetItem(date_str)
            self.table.setItem(row, 0, date_item)
            
            # Description
            desc_item = QTableWidgetItem(transaction.get('description', ''))
            self.table.setItem(row, 1, desc_item)
            
            # Amount
            amount = transaction.get('amount', 0)
            amount_item = QTableWidgetItem(f"Rp {amount:,.2f}")
            if amount < 0:
                amount_item.setForeground(QColor('#ef4444'))
            else:
                amount_item.setForeground(QColor('#10b981'))
            self.table.setItem(row, 2, amount_item)
            
            # Category
            category_name = 'Uncategorized'
            if transaction.get('category'):
                category_name = transaction['category'].get('name', 'Unknown')
            category_item = QTableWidgetItem(category_name)
            self.table.setItem(row, 3, category_item)
            
            # Actions (buttons will be added via cellWidget)
            actions_widget = self.create_action_buttons(transaction)
            self.table.setCellWidget(row, 4, actions_widget)
            
            # ID (hidden)
            id_item = QTableWidgetItem(str(transaction.get('id', '')))
            self.table.setItem(row, 5, id_item)
    
    def create_action_buttons(self, transaction):
        """Create action buttons for each transaction row"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        
        # Recategorize button (AI)
        recategorize_btn = QPushButton('🤖 AI')
        recategorize_btn.setFixedSize(65, 28)
        recategorize_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #8b5cf6, stop:1 #6366f1);
                color: white;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #7c3aed, stop:1 #4f46e5);
            }
        """)
        recategorize_btn.clicked.connect(
            lambda: self.recategorize_transaction(transaction['id'])
        )
        
        # Delete button
        delete_btn = QPushButton('🗑️')
        delete_btn.setFixedSize(40, 28)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #fee2e2;
                color: #dc2626;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #fca5a5;
            }
        """)
        delete_btn.clicked.connect(
            lambda: self.delete_transaction(transaction['id'])
        )
        
        layout.addWidget(recategorize_btn)
        layout.addWidget(delete_btn)
        widget.setLayout(layout)
        
        return widget
    
    def show_add_dialog(self):
        """Show add transaction dialog"""
        log_user_action("show_add_transaction_dialog", "TransactionListWidget")
        
        dialog = AddTransactionDialog(self.api_client, self.categories, self)
        dialog.transaction_added.connect(self.on_transaction_added)
        dialog.show()
    
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
        self.refresh_btn.setEnabled(not loading)
        self.table.setEnabled(not loading)
        
        if loading:
            self.refresh_btn.setText('⏳ Loading...')
        else:
            self.refresh_btn.setText('🔄 Refresh')