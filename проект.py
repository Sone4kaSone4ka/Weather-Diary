import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime
import shutil

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("700x500")
        self.records = []
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # --- Форма ввода ---
        frame = tk.LabelFrame(self.root, text="Новая запись", padx=10, pady=10)
        frame.pack(pady=10, fill="x")

        tk.Label(frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="e")
        self.date_entry = tk.Entry(frame)
        self.date_entry.grid(row=0, column=1, sticky="we", padx=5)

        tk.Label(frame, text="Температура (°C):").grid(row=1, column=0, sticky="e")
        self.temp_entry = tk.Entry(frame)
        self.temp_entry.grid(row=1, column=1, sticky="we", padx=5)

        tk.Label(frame, text="Описание:").grid(row=2, column=0, sticky="ne")
        self.desc_entry = tk.Entry(frame)
        self.desc_entry.grid(row=2, column=1, sticky="we", padx=5)

        tk.Label(frame, text="Осадки:").grid(row=3, column=0, sticky="e")
        self.rain_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Да", variable=self.rain_var).grid(row=3, column=1, sticky="w")

        tk.Button(frame, text="Добавить запись", command=self.add_record).grid(row=4, column=0, columnspan=2, pady=10)

        # --- Фильтры ---
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=5, fill="x")

        tk.Label(filter_frame, text="Фильтр по дате:").pack(side="left")
        self.filter_date = tk.Entry(filter_frame)
        self.filter_date.pack(side="left", padx=5)

        tk.Label(filter_frame, text="Фильтр по температуре > (°C):").pack(side="left")
        self.filter_temp = tk.Entry(filter_frame)
        self.filter_temp.pack(side="left", padx=5)

        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).pack(side="left", padx=5)
        
        # Кнопка для сброса фильтра и показа всех записей
        tk.Button(filter_frame, text="Показать все", command=self.show_all).pack(side="left", padx=5)

        # --- Список записей ---
        self.tree = ttk.Treeview(self.root, columns=("date", "temp", "desc", "rain"), show='headings')
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("rain", text="Осадки")
        
        self.tree.column("date", width=120)
        self.tree.column("temp", width=100)
        self.tree.column("desc", width=300)
        self.tree.column("rain", width=80)
        
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

    def add_record(self):
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        
        if not date or not temp_str or not desc:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            temp = float(temp_str)
            if not self.validate_date(date):
                raise ValueError("Неверный формат даты. Используйте ДД.ММ.ГГГГ.")
            
            record = {
                "date": date,
                "temperature": temp,
                "description": desc,
                "rain": self.rain_var.get()
            }
            self.records.append(record)
            self.save_data()
            self.update_tree() # Обновляем полный список после добавления

            # Очистка полей
            self.date_entry.delete(0, tk.END)
            self.temp_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.rain_var.set(False)

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False

    def update_tree(self, records_to_display=None):
         # Если передан список для отображения (например, отфильтрованный), используем его.
         # Если нет (None) - отображаем основной список self.records.
         records = records_to_display if records_to_display is not None else self.records

         # Очистка таблицы перед обновлением
         for i in self.tree.get_children():
             self.tree.delete(i)
         
         for rec in records:
             rain_text = "Да" if rec["rain"] else "Нет"
             self.tree.insert("", "end", values=(rec["date"], f"{rec['temperature']}°C", rec["description"], rain_text))

    def apply_filter(self):
         filter_date = self.filter_date.get().strip()
         filter_temp_str = self.filter_temp.get().strip()
         
         filtered_records = self.records.copy()
         
         if filter_date:
             if not self.validate_date(filter_date):
                 messagebox.showerror("Ошибка", "Неверный формат даты в фильтре!")
                 return
             filtered_records = [r for r in filtered_records if r["date"] == filter_date]
         
         if filter_temp_str:
             try:
                 temp_val = float(filter_temp_str)
                 filtered_records = [r for r in filtered_records if r["temperature"] > temp_val]
             except ValueError:
                 messagebox.showerror("Ошибка", "Температура в фильтре должна быть числом!")
                 return

         # Передаем отфильтрованный список в метод обновления таблицы
         self.update_tree(filtered_records)

    def show_all(self):
         # Сброс фильтров: показываем все записи из self.records
         self.filter_date.delete(0, tk.END)
         self.filter_temp.delete(0, tk.END)
         self.update_tree()

    def load_data(self):
         try:
             with open('weather_data.json', 'r', encoding='utf-8') as f:
                 data = json.load(f)
                 if isinstance(data, list):
                     self.records = data
                     self.update_tree()
                 else:
                     raise json.JSONDecodeError("Данные не являются списком", "", 0)
         except FileNotFoundError:
             # Файла нет - создаем новый пустой файл и список записей.
             messagebox.showinfo("Инициализация", "Файл данных не найден. Создан новый.")
             self.records = []
             self.save_data()
             self.update_tree()
         except json.JSONDecodeError:
             # Файл поврежден или имеет неверный формат.
             messagebox.showerror("Ошибка чтения", "Файл данных поврежден. Будет создана новая база.")
             self.records = []
             
             # Сохраняем резервную копию поврежденного файла (если он существует)
             try:
                 shutil.copy('weather_data.json', 'weather_data.json.bak')
                 messagebox.showinfo("Восстановление", "Поврежденный файл сохранен как 'weather_data.json.bak'")
             except FileNotFoundError:
                 pass # Файла нет, просто продолжаем

             # Создаем чистый файл для дальнейшей работы
             with open('weather_data.json', 'w', encoding='utf-8') as f:
                 json.dump([], f)
             
             self.update_tree()
         except Exception as e:
             messagebox.showerror("Критическая ошибка", f"Не удалось загрузить данные: {e}")
             self.records = []

    def save_data(self):
         try:
             with open('weather_data.json', 'w', encoding='utf-8') as f:
                 json.dump(self.records, f, ensure_ascii=False, indent=4)
         except Exception as e: # Обработка любых ошибок записи (например, права доступа на диске)
             messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()