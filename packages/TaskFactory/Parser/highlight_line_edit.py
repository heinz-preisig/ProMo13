from PyQt5.QtWidgets import QTextEdit, QApplication
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt5.QtCore import Qt


class CustomTextEdit(QTextEdit):
  def __init__(self, *args, **kwargs):
    super(CustomTextEdit, self).__init__(*args, **kwargs)
    self.setLineWrapMode(QTextEdit.NoWrap)
    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

  def highlight_word(self, word, color):
    cursor = self.document().find(word)

    while not cursor.isNull() and not cursor.atEnd():
      cursor.select(QTextCursor.WordUnderCursor)
      char_format = QTextCharFormat()
      char_format.setBackground(color)
      cursor.mergeCharFormat(char_format)
      cursor = self.document().find(word, cursor)

  def keyPressEvent(self, event):
    if event.key() in (Qt.Key_Enter, Qt.Key_Return):
      return
    super(CustomTextEdit, self).keyPressEvent(event)


if __name__ == '__main__':
  import sys

  app = QApplication(sys.argv)

  text_edit = CustomTextEdit()
  text_edit.setPlainText("This is a custom QTextEdit example.")
  text_edit.highlight_word("custom", QColor("yellow"))

  text_edit.show()

  sys.exit(app.exec())
