from utils.imports import json

class VirtualFileSystem:
    """Виртуальная файловая система"""

    def __init__(self):
        with open('utils/vfs_structure.json', 'r', encoding='utf-8') as f:
            self.root = json.load(f)

    def resolve_path(self, current_path, target_path):
        """Разрешает путь относительно текущей директории и возвращает узел"""
        # Определяем начальную точку и части пути
        path_parts, current_node = self._get_starting_point(current_path, target_path)
        if current_node is None:
            return None

        # Обрабатываем все части пути
        return self._process_path_parts(path_parts, current_node)

    def _get_starting_point(self, current_path, target_path):
        """Определяет начальную директорию и разбивает целевой путь на части"""
        if target_path.startswith('/'):
            # Абсолютный путь - начинаем от корня
            path_parts = self._split_path(self, target_path)
            return path_parts, self.root
        else:
            # Относительный путь - начинаем от текущей директории
            path_parts = self._split_path(self, target_path)
            current_node = self._get_current_directory_node(current_path)
            return path_parts, current_node

    @staticmethod
    def _split_path(self, path):
        """Разбивает путь на части, убирая пустые элементы"""
        return [p for p in path.split('/') if p]

    def _get_current_directory_node(self, current_path):
        """Возвращает узел текущей директории"""
        if current_path == '/':
            return self.root

        path_parts = self._split_path(self, current_path)
        current_node = self.root

        for part in path_parts:
            if (part in current_node['content'] and
                    current_node['content'][part]['type'] == 'directory'):
                current_node = current_node['content'][part]
            else:
                return None  # Текущий путь не существует

        return current_node

    def _process_path_parts(self, path_parts, current_node):
        """Обрабатывает все части пути последовательно"""
        for part in path_parts:
            current_node = self._process_single_part(part, current_node)
            if current_node is None:
                return None

        return current_node

    def _process_single_part(self, part, current_node):
        """Обрабатывает одну часть пути"""
        if part == '..':
            return self._go_to_parent(self, current_node)
        elif part == '.':
            return current_node  # Остаемся в текущей директории
        elif part in current_node['content']:
            return current_node['content'][part]
        else:
            return None  # Путь не существует

    @staticmethod
    def _go_to_parent(self, current_node):
        """Переходит к родительской директории"""
        if 'parent' in current_node:
            return current_node['parent']
        else:
            # Мы в корне, нельзя подняться выше - остаемся в корне
            return current_node


    def list_directory(self, path):
        """Список содержимого директории"""
        node = self.resolve_path(path, path)
        if node is not None and node['type'] == 'directory':
            return list(node['content'].keys())
        return None

    def is_directory(self, path):
        """Проверяет, является ли путь директорией"""
        node = self.resolve_path(path, path)
        return node and node['type'] == 'directory'

    def is_file(self, path):
        """Проверяет, является ли путь файлом"""
        node = self.resolve_path(path, path)
        return node and node['type'] == 'file'

    def get_file_content(self, path):
        """Получает содержимое файла"""
        node = self.resolve_path(path, path)
        if node and node['type'] == 'file':
            return node['content']
        return None
