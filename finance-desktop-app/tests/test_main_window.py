import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()

def test_main_window_creation(app):
    from main import MainWindow
    
    window = MainWindow()
    assert window is not None
    assert window.windowTitle() == 'Finance Manager'
    assert window.width() == 800
    assert window.height() == 600

def test_main_window_buttons(app):
    from main import MainWindow
    
    window = MainWindow()
    
    # Find buttons by text
    buttons = window.findChildren(window.__class__.__bases__[0].__bases__[0])
    button_texts = []
    
    from PyQt5.QtWidgets import QPushButton
    for child in window.findChildren(QPushButton):
        button_texts.append(child.text())
    
    assert 'Login' in button_texts
    assert 'Register' in button_texts
    assert 'Demo Mode' in button_texts

def test_button_connections(app):
    from main import MainWindow
    
    window = MainWindow()
    
    # Test that button click methods exist
    assert hasattr(window, 'show_login')
    assert hasattr(window, 'show_register')
    assert hasattr(window, 'show_demo')
    
    # Test that methods are callable
    assert callable(window.show_login)
    assert callable(window.show_register)
    assert callable(window.show_demo)