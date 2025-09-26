import json
import base64

class VirtualFileSystem:
    """Виртуальная файловая система с поддержкой base64"""

    def __init__(self, vfs_path):
        self.vfs_path = vfs_path
        try:
            with open(vfs_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.root = self._process_vfs_data(data)
            self._set_parent_references(self.root, None)
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки VFS: {e}")

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