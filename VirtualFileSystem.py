import json
import base64
import os


class VirtualFileSystem:
    """Виртуальная файловая система с поддержкой base64"""

    def __init__(self, vfs_path):
        self.vfs_path = vfs_path
        try:
            with open(vfs_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.root = self._process_vfs_data(data)
            self._set_parent_references(self.root, None)
            self._ensure_default_permissions(self.root)
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки VFS: {e}")

    def _ensure_default_permissions(self, node):
        """Ставит стандартные права если их нет"""
        if 'permissions' not in node:
            # Для папок - 755, для файлов - 644
            if node['type'] == 'directory':
                node['permissions'] = '755'
            else:
                node['permissions'] = '644'

        # Для всех вложенных файлов/папок тоже ставим права
        if node['type'] == 'directory':
            for child in node['content'].values():
                self._ensure_default_permissions(child)
    def _process_vfs_data(self, node, path=""):
        """Обрабатывает данные VFS, декодируя base64 если нужно"""
        if node['type'] == 'file' and 'content_b64' in node:
            try:
                node['content'] = base64.b64decode(node['content_b64']).decode('utf-8')
                del node['content_b64']
            except Exception as e:
                node['content'] = f"Ошибка декодирования: {e}"
        elif node['type'] == 'directory':
            for name, child in node['content'].items():
                child_path = f"{path}/{name}" if path else name
                node['content'][name] = self._process_vfs_data(child, child_path)
        return node

    def _set_parent_references(self, node, parent):
        """Устанавливает ссылки на родительские узлы"""
        node['parent'] = parent
        if node['type'] == 'directory':
            for child_name, child_node in node['content'].items():
                self._set_parent_references(child_node, node)

    def _ensure_default_permissions(self, node):
        """Устанавливает права доступа по умолчанию если их нет"""
        if 'permissions' not in node:
            node['permissions'] = '755' if node['type'] == 'directory' else '644'

        if node['type'] == 'directory':
            for child_node in node['content'].values():
                self._ensure_default_permissions(child_node)

    def resolve_path(self, current_path, target_path):
        """Разрешает путь относительно текущей директории"""
        if target_path.startswith('/'):
            path_parts = self._split_path(target_path)
            current_node = self.root
        else:
            path_parts = self._split_path(target_path)
            current_node = self._get_node_at_path(current_path)
            if current_node is None:
                return None

        return self._follow_path(path_parts, current_node)

    def _split_path(self, path):
        """Разбивает путь на части"""
        return [p for p in path.split('/') if p]

    def _get_node_at_path(self, path):
        """Получает узел по абсолютному пути"""
        if path == '/':
            return self.root

        path_parts = self._split_path(path)
        current_node = self.root

        for part in path_parts:
            if (part in current_node.get('content', {}) and
                    current_node['content'][part]['type'] == 'directory'):
                current_node = current_node['content'][part]
            else:
                return None
        return current_node

    def _follow_path(self, path_parts, current_node):
        """Следует по пути из частей"""
        for part in path_parts:
            if part == '..':
                current_node = current_node.get('parent', current_node)
            elif part == '.':
                continue
            elif part in current_node.get('content', {}):
                current_node = current_node['content'][part]
            else:
                return None
        return current_node

    def get_file_content(self, current_path, file_path):
        """Получает содержимое файла"""
        node = self.resolve_path(current_path, file_path)
        if node and node['type'] == 'file':
            return node.get('content', '')
        return None

    def create_directory(self, current_path, dir_path):
        """Создает директорию в памяти VFS"""
        parent_node = self._get_node_at_path(current_path)
        if not parent_node or parent_node['type'] != 'directory':
            return False

        path_parts = self._split_path(dir_path)
        if not path_parts:
            return False

        # Создаем все промежуточные директории
        current = parent_node
        for part in path_parts:
            if part not in current['content']:
                current['content'][part] = {
                    'type': 'directory',
                    'content': {},
                    'parent': current,
                    'permissions': '755'
                }
            elif current['content'][part]['type'] != 'directory':
                return False
            current = current['content'][part]

        return True

    def create_file(self, current_path, file_path):
        """Создает файл в памяти VFS"""
        parent_node = self._get_node_at_path(current_path)
        if not parent_node or parent_node['type'] != 'directory':
            return False

        path_parts = self._split_path(file_path)
        if not path_parts:
            return False

        filename = path_parts[-1]
        parent_parts = path_parts[:-1]

        # Переходим к родительской директории
        current = parent_node
        for part in parent_parts:
            if part not in current['content']:
                current['content'][part] = {
                    'type': 'directory',
                    'content': {},
                    'parent': current,
                    'permissions': '755'
                }
            elif current['content'][part]['type'] != 'directory':
                return False
            current = current['content'][part]

        # Создаем файл
        if filename not in current['content']:
            current['content'][filename] = {
                'type': 'file',
                'content': '',
                'parent': current,
                'permissions': '644'
            }

        return True

    def remove_directory(self, current_path, dir_path):
        """Удаляет пустую директорию"""
        target_node = self.resolve_path(current_path, dir_path)
        if not target_node:
            return False

        if target_node['type'] != 'directory':
            return False

        # Проверяем что директория пуста
        if target_node['content']:
            return False

        # Удаляем из родительской директории
        parent = target_node.get('parent')
        if not parent:
            return False  # Нельзя удалить корневую директорию

        # Находим имя директории в родительском содержимом
        for name, node in parent['content'].items():
            if node is target_node:
                del parent['content'][name]
                return True

        return False

    def change_permissions(self, current_path, target_path, mode):
        """Изменяет права доступа файла/директории"""
        target_node = self.resolve_path(current_path, target_path)
        if not target_node:
            return False

        # Проверяем формат прав доступа
        if not self._is_valid_permissions(mode):
            return False

        target_node['permissions'] = mode
        return True

    def _is_valid_permissions(self, mode):
        """Проверяет корректность формата прав доступа"""
        if len(mode) != 3:
            return False

        for char in mode:
            if not char.isdigit() or int(char) > 7:
                return False

        return True
