"""
Undo/Redo Commands Module
-------------------------
Custom QUndoCommand classes for Graphic Items manipulation.

Author: Boris du Reau
"""

from PyQt6.QtGui import QUndoCommand


class MoveCommand(QUndoCommand):
    """Command to handle moving one or multiple items."""

    def __init__(self, items, old_positions, text="Move Item(s)"):
        super().__init__(text)
        self.items = items
        self.old_positions = old_positions
        self.new_positions = [it.pos() for it in items]

    def undo(self):
        for item, pos in zip(self.items, self.old_positions):
            item.setPos(pos)

    def redo(self):
        for item, pos in zip(self.items, self.new_positions):
            item.setPos(pos)


class AddItemCommand(QUndoCommand):
    """Command to handle adding an item to the scene."""

    def __init__(self, scene, item, text="Add Item"):
        super().__init__(text)
        self.scene = scene
        self.item = item  # Conserve la référence Python

    def undo(self):
        # Utilise la méthode native super_add/removeItem sans déclencher d'événements
        self.scene.removeItemNative(self.item)

    def redo(self):
        self.scene.addItemNative(self.item)


class DeleteItemsCommand(QUndoCommand):
    """Command to handle removing items from the scene."""

    def __init__(self, scene, items, text="Delete Item(s)"):
        super().__init__(text)
        self.scene = scene
        self.items = list(items)  # Garde la liste des références vivante

    def undo(self):
        for item in self.items:
            self.scene.addItemNative(item)

    def redo(self):
        for item in self.items:
            self.scene.removeItemNative(item)

class ResizeItemCommand(QUndoCommand):
    """Command to handle scaling/resizing a graphic item."""

    def __init__(self, item, old_scale, new_scale, text="Resize Image"):
        super().__init__(text)
        self.item = item
        self.old_scale = old_scale
        self.new_scale = new_scale

    def undo(self):
        self.item.prepareGeometryChange()
        self.item.setScale(self.old_scale)
        self.item.update()

    def redo(self):
        self.item.prepareGeometryChange()
        self.item.setScale(self.new_scale)
        self.item.update()