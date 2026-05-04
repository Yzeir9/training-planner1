import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "training_data.json"

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("750x500")
        self.root.resizable(False, False)

        # Загрузка данных
        self.trainings = self.load_data()

        # Создание интерфейса
        self.create_widgets()
        self.refresh_table()

    def load_data(self):
        """Загружает тренировки из JSON-файла."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_data(self):
        """Сохраняет тренировки в JSON-файл."""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.trainings, f, ensure_ascii=False, indent=2)

    def create_widgets(self):
        # ---- Панель ввода новой тренировки ----
        input_frame = tk.LabelFrame(self.root, text="Новая тренировка", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.date_entry = tk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))  # сегодняшняя дата по умолчанию

        # Тип тренировки
        tk.Label(input_frame, text="Тип тренировки:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.type_combo = ttk.Combobox(input_frame, values=["Бег", "Велосипед", "Плавание", "Силовая", "Йога"], width=13)
        self.type_combo.grid(row=1, column=1, padx=5, pady=2)
        self.type_combo.set("Бег")

        # Длительность (минуты)
        tk.Label(input_frame, text="Длительность (мин):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.duration_entry = tk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=2, column=1, padx=5, pady=2)

        # Кнопка Добавить
        btn_add = tk.Button(input_frame, text="Добавить тренировку", command=self.add_training,
                            bg="#4CAF50", fg="white", width=20)
        btn_add.grid(row=3, column=0, columnspan=2, pady=10)

        # ---- Панель фильтрации ----
        filter_frame = tk.LabelFrame(self.root, text="Фильтр", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Тип:").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_type_combo = ttk.Combobox(filter_frame, values=["Все", "Бег", "Велосипед", "Плавание", "Силовая", "Йога"], width=12)
        self.filter_type_combo.grid(row=0, column=1, padx=5)
        self.filter_type_combo.set("Все")
        self.filter_type_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        tk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky="w", padx=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=12)
        self.filter_date_entry.grid(row=0, column=3, padx=5)
        self.filter_date_entry.bind("<KeyRelease>", lambda e: self.refresh_table())

        btn_reset = tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter, bg="#FFC107")
        btn_reset.grid(row=0, column=4, padx=10)

        # ---- Таблица с тренировками ----
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(table_frame, columns=("date", "type", "duration"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("duration", text="Длительность (мин)")
        self.tree.column("date", width=100)
        self.tree.column("type", width=150)
        self.tree.column("duration", width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка удаления выбранной записи
        btn_delete = tk.Button(self.root, text="Удалить выбранную тренировку", command=self.delete_training,
                               bg="#F44336", fg="white")
        btn_delete.pack(pady=5)

    def add_training(self):
        """Добавляет новую тренировку после валидации."""
        date = self.date_entry.get().strip()
        training_type = self.type_combo.get().strip()
        duration_str = self.duration_entry.get().strip()

        # Валидация
        if not date or not training_type or not duration_str:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        # Проверка формата даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД (например, 2025-04-06)")
            return

        # Проверка длительности
        try:
            duration = float(duration_str)
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
            return

        # Добавление
        self.trainings.append({
            "date": date,
            "type": training_type,
            "duration": duration
        })
        self.save_data()
        self.refresh_table()
        # Очистка полей (дата остаётся сегодняшней, тип сбрасывается на "Бег")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.type_combo.set("Бег")
        self.duration_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", "Тренировка добавлена!")

    def delete_training(self):
        """Удаляет выбранную в таблице тренировку."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления")
            return
        # Получаем значения из выделенной строки
        values = self.tree.item(selected[0], "values")
        # Ищем тренировку в списке по всем трём полям (удаляем первое совпадение)
        for i, t in enumerate(self.trainings):
            if (t["date"] == values[0] and t["type"] == values[1] and float(t["duration"]) == float(values[2])):
                del self.trainings[i]
                break
        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Успех", "Тренировка удалена")

    def refresh_table(self):
        """Обновляет таблицу с учётом текущих фильтров."""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Получаем значения фильтров
        filter_type = self.filter_type_combo.get()
        filter_date = self.filter_date_entry.get().strip()

        # Применяем фильтр к данным
        filtered = self.trainings
        if filter_type != "Все":
            filtered = [t for t in filtered if t["type"] == filter_type]
        if filter_date:
            filtered = [t for t in filtered if t["date"] == filter_date]

        # Заполняем таблицу
        for t in filtered:
            self.tree.insert("", "end", values=(t["date"], t["type"], t["duration"]))

    def reset_filter(self):
        """Сбрасывает фильтры (тип = Все, дата = пусто)."""
        self.filter_type_combo.set("Все")
        self.filter_date_entry.delete(0, tk.END)
        self.refresh_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()