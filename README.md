# Эмулятор командной строки с виртуальной файловой системой

Проект представляет собой эмулятор командной строки с полнофункциональной виртуальной файловой системой (VFS), поддерживающий как интерактивный режим, так и выполнение скриптов.

## Возможности

### Поддерживаемые команды

- **ls** - список файлов и директорий
- **cd** - смена текущей директории
- **pwd** - вывод текущего пути
- **cat** - вывод содержимого файлов
- **echo** - вывод текста
- **mkdir** - создание директорий
- **touch** - создание файлов
- **rev** - переворот строк
- **cal** - отображение календаря
- **rmdir** - удаление пустых директорий
- **chmod** - изменение прав доступа
- **exit** - выход из эмулятора

### Особенности VFS

- Иерархическая структура файлов и директорий
- Поддержка прав доступа (chmod)
- Хранение содержимого файлов в формате base64
- Предопределенная структура с домашними директориями, системными файлами и логами

## Установка и запуск

### Требования

- Python 3.6+
- Стандартные библиотеки Python (не требует дополнительных зависимостей)

### Запуск

#### Пример запуска
```bash
python main.py utils/vfs_structure.json tests/stage4_test.txt
```
Пример вывода
```bash
==================================================
КОНФИГУРАЦИЯ ЭМУЛЯТОРА
==================================================
Путь к VFS: utils/vfs_structure.json
Путь к стартовому скрипту: tests/stage4_test.txt
==================================================

Anastasia@LAPTOP-V969GJES:~$ pwd
/home/user

Anastasia@LAPTOP-V969GJES:~$ ls
755 documents/
755 empty_dir1/
755 pictures/
644 readme.md

Anastasia@LAPTOP-V969GJES:~$ ls /home/user
755 documents/
755 empty_dir1/
755 pictures/
644 readme.md

Anastasia@LAPTOP-V969GJES:~$ ls /nonexistent
ОШИБКА В СКРИПТЕ: Нет доступа к '/nonexistent': Нет такого файла или каталога
ОШИБКА: Нет доступа к '/nonexistent': Нет такого файла или каталога

```

```bash
project/
├── main.py                 # Основной файл запуска
├── ShellEmulator.py        # Эмулятор командной строки
├── VirtualFileSystem.py    # Виртуальная файловая система
├── utils/
│   └── vfs_structure.json  # Структура VFS по умолчанию
├── scripts/
│   └── test_basic.txt
    └── test_basic_2.txt
    └── test_krutoy.txt
    └── stage4_test.txt
└── README.md
```

VFS
```bash
{
  "type": "directory",
  "content": {
    "home": {
      "type": "directory",
      "content": {
        "user": {
          "type": "directory",
          "content": {
            "documents": {
              "type": "directory",
              "content": {
                "readme.txt": {
                  "type": "file",
                  "content_b64": "SGVsbG8gV29ybGQh"
                }
              }
            }
          }
        }
      }
    }
  }
}
```
