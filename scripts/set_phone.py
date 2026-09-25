import os
import sys
import glob

def main():
    if len(sys.argv) < 2:
        print("❌ Ошибка: Укажите новый номер телефона.")
        print("Пример: python scripts/set_phone.py +381601234567")
        sys.exit(1)

    new_number_full = sys.argv[1]
    new_number_clean = new_number_full.replace('+', '').replace(' ', '')

    # Все варианты старого номера, которые нашли в аудите
    old_variants = [
        "+995557645196",
        "+995 557 645 196",
        "995557645196"
    ]

    # Ищем все HTML, JS и JSON файлы, исключая системные папки
    files = []
    for pattern in ['**/*.html', '**/*.js', '**/*.json', '**/*.xml']:
        files.extend(glob.glob(pattern, recursive=True))
    
    files = [f for f in files if '.git' not in f and 'venv' not in f and 'node_modules' not in f]

    count = 0
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Заменяем все варианты старого номера
            for old_num in old_variants:
                # Если старый номер был без плюса (для wa.me), заменяем на новый без плюса
                if not old_num.startswith('+'):
                    content = content.replace(old_num, new_number_clean)
                else:
                    content = content.replace(old_num, new_number_full)
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                count += 1
                print(f"✅ Обновлен: {filepath}")
                
        except Exception as e:
            print(f"⚠️ Ошибка в {filepath}: {e}")

    print(f"\n🎉 Готово! Всего обновлено файлов: {count}")
    
    # Финальная проверка через grep
    print("\n🔍 Финальная проверка на остатки старого номера (995):")
    os.system("grep -rn '995' --include='*.html' --include='*.js' --include='*.json' . | grep -v 'node_modules' | grep -v '.git' || echo '   ✅ Старых номеров не найдено. Всё чисто!'")

if __name__ == "__main__":
    main()