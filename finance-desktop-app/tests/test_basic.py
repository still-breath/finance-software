import pytest
from PyQt5.QtWidgets import QApplication, QWidget
import sys

def test_pyqt_import():
    """Test that PyQt5 can be imported successfully"""
    try:
        from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
        from PyQt5.QtCore import Qt
        assert True, "PyQt5 imported successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import PyQt5: {e}")

def test_qt_application():
    """Test creating a basic Qt application"""
    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Test creating a basic widget
    widget = QWidget()
    widget.setWindowTitle("Test Window")
    
    assert widget.windowTitle() == "Test Window"
    assert widget is not None