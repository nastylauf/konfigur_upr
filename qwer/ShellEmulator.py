from utils.imports import shlex, socket, getpass
from VirtualFileSystem import VirtualFileSystem


class ShellEmulator:
    def __init__(self):
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.vfs = VirtualFileSystem()
        self.current_path = '/home/user'  # Начальный путь в VFS
        self.running = True

    def get_prompt(self):
        """Формирует приглашение к вводу в формате username@hostname:directory$"""
        # Упрощаем путь для отображения
        if self.current_path.startswith('/home/user'):
            display_path = '~' + self.current_path[len('/home/user'):]
        else:
            display_path = self.current_path

        return f"{self.username}@{self.hostname}:{display_path}$ "

    @staticmethod
    def parse_command(self, command_line):
        """Парсит командную строку с учетом кавычек"""
        try:
            return shlex.split(command_line)
        except ValueError as e:
            print(f"Ошибка парсинга: {e}")
            return None

    def execute_command(self, command_parts):
        """Выполняет команду"""
        if not command_parts:
            return

        command = command_parts[0]
        args = command_parts[1:]

        if command == "exit":
            self.running = False
            print("Выход из эмулятора")

        elif command == "ls":
            self.ls_command(args)

        elif command == "cd":
            self.cd_command(args)

        elif command == "pwd":
            print(f"Команда: pwd")
            print(self.current_path)

        elif command == "cat":
            self.cat_command(args)

        else:
            print(f"{command}: команда не найдена")

    def ls_command(self, args):
        print(f"Команда: ls")
        if args:
            print(f"Аргументы: {args}")
            target_path = args[0]
            # Пытаемся получить список файлов по указанному пути
            files = self.vfs.list_directory(target_path)

            if files is None:
                print(f"ls: невозможно получить доступ к '{target_path}': Нет такого файла или каталога")
            else:
                for file in sorted(files):
                    print(file)
        else:
            print("Аргументы отсутствуют")
            # Показываем содержимое текущей директории
            files = self.vfs.list_directory(self.current_path)
            if files:
                for file in sorted(files):
                    print(file)

    def cd_command(self, args):
        """Обрабатывает команду cd"""
        print(f"Команда: cd")

        if args:
            print(f"Аргументы: {args}")
            if len(args) > 1:
                print("cd: слишком много аргументов")
                return

            target_path = args[0]
            # Обрабатываем специальные пути
            processed_path = self.special_paths(self, target_path)
            if processed_path is None:
                return  # Специальный путь не обработан

            # Пытаемся перейти по пути
            self.follow_the_path(processed_path)
        else:
            # cd без аргументов - переход в домашнюю директорию
            self.current_path = "/home/user"
            print("Переход в домашнюю директорию")

    def cat_command(self, args):
        print(f"Команда: cat")
        if args:
            print(f"Аргументы: {args}")
            for file_path in args:
                content = self.vfs.get_file_content(file_path)
                if content is not None:
                    print(content)
                else:
                    print(f"cat: {file_path}: Нет такого файла или каталога")
        else:
            print("cat: отсутствуют аргументы")

    @staticmethod
    def special_paths(self, target_path):
        """Обрабатывает специальные пути типа ~ и -"""
        if target_path == "~":
            return "/home/user"
        elif target_path == "-":
            # В реальной системе это вернуло бы в предыдущую директорию
            print("cd: функция не реализована")
            return None
        else:
            return target_path  # Возвращаем путь без изменений

    def follow_the_path(self, target_path):
        """Пытается перейти по указанному пути"""
        new_node = self.vfs.resolve_path(self.current_path, target_path)
        if new_node and new_node['type'] == 'directory':
            # Обновляем текущий путь
            self.update_path(target_path)
            # Нормализуем путь
            self.normalize_path()
            print(f"Переход в {self.current_path}")
        else:
            print(f"cd: {target_path}: Нет такой директории")

    def update_path(self, target_path):
        """Обновляет current_path в зависимости от типа пути"""
        if target_path.startswith('/'):
            # Абсолютный путь
            self.current_path = target_path
        else:
            # Относительный путь
            if self.current_path == '/':
                self.current_path = '/' + target_path
            else:
                self.current_path = self.current_path + '/' + target_path

    def normalize_path(self):
        """Нормализует путь (убирает двойные слеши и trailing slash)"""
        self.current_path = self.current_path.replace('//', '/')
        if self.current_path.endswith('/') and len(self.current_path) > 1:
            self.current_path = self.current_path[:-1]

    def run(self):
        """Основной цикл REPL (Read-Eval-Print Loop)"""
        self.terminal_start(self)

        while self.running:
            try:
                # Выводим приглашение и читаем ввод
                command_line = input(self.get_prompt()).strip()

                # Пропускаем пустые строки
                if not command_line:
                    continue

                # Парсим команду
                command_parts = self.parse_command(self, command_line)
                if command_parts is None:
                    continue

                # Выполняем команду
                self.execute_command(command_parts)
                print()  # Пустая строка для читаемости

            except KeyboardInterrupt:
                print("\nДля выхода введите 'exit'")
            except EOFError:
                print("\nВыход из эмулятора")
                break
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")

    @staticmethod
    def terminal_start(self):
        welcome_text = (
            "Добро пожаловать в эмулятор командной строки с VFS!\n"
            "Доступные команды: ls, cd, pwd, cat, exit\n"
            "Виртуальная файловая система содержит:\n"
            "  /home/user/documents/ - файлы документов\n"
            "  /home/user/pictures/ - изображения\n"
            "  /etc/ - конфигурационные файлы\n"
            "  /var/log/ - логи\n"
            "Для выхода введите 'exit'\n"
            + "-" * 50
        )
        print(welcome_text)










