from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QColorDialog, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

class PopupWidget(QWidget):
    """ A custom popup widget that appears near the cursor when shown."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)  #Flag popup means not integrated in a parent window
        self.move(QCursor().pos().x() + 10, QCursor().pos().y() + 10)   #Move the popup near the cursor

    def focusOutEvent(self, event):     #Gets called when Widget out of focus
        """Close the popup when it loses focus."""
        self.close()
        super().focusOutEvent(event)
        
class CustomColorPicker(QColorDialog):
    """A custom color dialog that only shows the RGB square"""
    def __init__(self):
        super().__init__()
        # Hide everything but RGB square
        self.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, False)
        self.setOption(QColorDialog.ColorDialogOption.NoButtons, True)
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        for i in self.children()[1:8]: i.hide()
        for i in self.children()[10:11]: i.hide()
        
class SquareWidget(QWidget):
    """A custom widget that maintains a square aspect ratio."""
    def __init__(self):
        super().__init__()
        
    def resizeEvent(self, event):   #Gets called when widget resize is requested
        self.setMaximumHeight(self.width())
        self.setMinimumHeight(self.width())
        super().resizeEvent(event)

        
if __name__ == "__main__":
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Main Window")
            self.setGeometry(200, 200, 400, 300)

            # Add a button to trigger the popup
            button = QPushButton("Open Popup", self)
            button.clicked.connect(self.show_popup)

            # Layout setup
            layout = QVBoxLayout()
            layout.addWidget(button)

            central_widget = QWidget()
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)

        def show_popup(self):
            popup = PopupWidget(self)
            popup.show()
            
    app = QApplication([])

    main_window = MainWindow()
    main_window.show()

    app.exec()
