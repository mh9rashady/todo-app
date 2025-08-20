import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox


PRIORITY_ORDER = {
    "بالا": 3,
    "متوسط": 2,
    "پایین": 1,
}


class Task:
    def __init__(self, task_id, title, description, priority):
        self.id = int(task_id)
        self.title = title.strip()
        self.description = description.strip()
        if priority not in PRIORITY_ORDER:
            priority = "پایین"
        self.priority = priority

    def to_row(self):
        return [str(self.id), self.title, self.description, self.priority]

    @staticmethod
    def from_row(row):
        task_id, title, description, priority = row
        return Task(task_id, title, description, priority)


class ToDoList:
    def __init__(self, csv_path="tasks.csv"):
        self.csv_path = csv_path
        self.tasks = []
        self._next_id = 1
        self._load_from_csv_if_exists()

    def _load_from_csv_if_exists(self):
        if not os.path.exists(self.csv_path):
            return
        try:
            with open(self.csv_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if not row:
                        continue
                    try:
                        task = Task.from_row(row)
                        self.tasks.append(task)
                    except Exception:
                        continue
            if self.tasks:
                self._next_id = max(t.id for t in self.tasks) + 1
        except FileNotFoundError:
            pass

    def _save_to_csv(self):
        with open(self.csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "title", "description", "priority"])
            for task in self.tasks:
                writer.writerow(task.to_row())

    def add_task(self, title, description, priority):
        task = Task(self._next_id, title, description, priority)
        self.tasks.append(task)
        self._next_id += 1
        self._save_to_csv()
        return task.id

    def delete_task(self, task_id):
        task_id = int(task_id)
        new_list = [t for t in self.tasks if t.id != task_id]
        if len(new_list) == len(self.tasks):
            return False
        self.tasks = new_list
        self._save_to_csv()
        return True
    
    def get_all_tasks(self):
        sorted_tasks = sorted(self.tasks, key=lambda t: (-PRIORITY_ORDER.get(t.priority, 0), t.id))
        return sorted_tasks

    def list_tasks(self, sort_by_priority=True):
        if sort_by_priority:
            self.tasks.sort(key=lambda t: (-PRIORITY_ORDER.get(t.priority, 0), t.id))
        if not self.tasks:
            print("هیچ کاری در لیست نیست.")
            return
        print("\nلیست کارها:")
        print("-" * 60)
        print(f"{'آیدی':<6} | {'عنوان':<20} | {'اولویت':<7} | توضیحات")
        print("-" * 60)
        for t in self.tasks:
            title_cut = t.title if len(t.title) <= 20 else t.title[:17] + "..."
            print(f"{t.id:<6} | {title_cut:<20} | {t.priority:<7} | {t.description}")
        print("-" * 60)

    def show_priority_chart(self):
        # استفاده ی خیلی ساده از NumPy و Matplotlib برای آمار
        try:
            import numpy as np
            import matplotlib.pyplot as plt
        except Exception:
            print("برای نمایش نمودار باید NumPy و Matplotlib نصب باشد.")
            print("می توانید با دستور pip install numpy matplotlib آن ها را نصب کنید.")
            return

        if not self.tasks:
            print("چیزی برای نمایش وجود ندارد.")
            return

        priorities = [t.priority for t in self.tasks]
        labels = ["بالا", "متوسط", "پایین"]
        counts = []
        for p in labels:
            counts.append(sum(1 for x in priorities if x == p))

        # فقط یک نمودار ستونی خیلی ساده
        positions = np.arange(len(labels))
        plt.bar(positions, counts, color=["#e74c3c", "#f1c40f", "#2ecc71"])  # قرمز/زرد/سبز
        plt.xticks(positions, labels)
        plt.ylabel("تعداد")
        plt.title("تعداد کارها بر اساس اولویت")
        plt.tight_layout()
        plt.show()


def ask_priority_from_user():
    print("اولویت را وارد کنید:")
    print("1) بالا   2) متوسط   3) پایین")
    choice = input("انتخاب شما (1/2/3): ").strip()
    if choice == "1":
        return "بالا"
    if choice == "2":
        return "متوسط"
    if choice == "3":
        return "پایین"
   
    return "پایین"


def main_menu():
    todo = ToDoList()
    while True:
        print("\n— مدیریت لیست کارها —")
        print("1) افزودن کار جدید")
        print("2) حذف کار")
        print("3) مشاهده لیست کارها")
        print("4) نمودار تعداد کارها بر اساس اولویت")
        print("5) خروج")

        cmd = input("یک گزینه را انتخاب کنید: ").strip()

        if cmd == "1":
            title = input("عنوان کار: ").strip()
            desc = input("توضیحات: ").strip()
            pr = ask_priority_from_user()
            new_id = todo.add_task(title, desc, pr)
            print(f"کار با آیدی {new_id} اضافه شد.")
        elif cmd == "2":
            try:
                task_id = int(input("آیدی کاری که میخواهید حذف کنید: ").strip())
            except ValueError:
                print("آیدی معتبر نیست.")
                continue
            ok = todo.delete_task(task_id)
            if ok:
                print("حذف شد.")
            else:
                print("کاری با این آیدی پیدا نشد.")
        elif cmd == "3":
            todo.list_tasks(sort_by_priority=True)
        elif cmd == "4":
            todo.show_priority_chart()
        elif cmd == "5":
            print("خداحافظ!")
            break
        else:
            print("گزینه نامعتبر است.")


def gui_menu():
    """منوی گرافیکی ساده برای لیست کارها."""
    root = tk.Tk()
    root.title("مدیریت لیست کارها")
    root.geometry("700x500")
    
    # تنظیم فونت
    root.option_add('*Font', 'Tahoma 10')
    
    # فریم اصلی
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # عنوان
    title_label = ttk.Label(main_frame, text="مدیریت لیست کارها", font=('Tahoma', 16, 'bold'))
    title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
    
    # بخش افزودن کار جدید
    add_frame = ttk.LabelFrame(main_frame, text="افزودن کار جدید", padding="10")
    add_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
    
    # عنوان کار
    ttk.Label(add_frame, text="عنوان:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
    title_entry = ttk.Entry(add_frame, width=30)
    title_entry.grid(row=0, column=1, padx=(0, 20))
    
    # توضیحات
    ttk.Label(add_frame, text="توضیحات:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
    desc_entry = ttk.Entry(add_frame, width=30)
    desc_entry.grid(row=1, column=1, padx=(0, 20), pady=(10, 0))
    
    # اولویت
    ttk.Label(add_frame, text="اولویت:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
    priority_var = tk.StringVar(value="متوسط")
    priority_combo = ttk.Combobox(add_frame, textvariable=priority_var, 
                                values=["بالا", "متوسط", "پایین"], state="readonly", width=10)
    priority_combo.grid(row=2, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
    
    # دکمه افزودن
    def add_task_gui():
        title = title_entry.get().strip()
        description = desc_entry.get().strip()
        priority = priority_var.get()
        
        if not title:
            messagebox.showwarning("هشدار", "لطفاً عنوان کار را وارد کنید!")
            return
        
        todo = ToDoList()
        task_id = todo.add_task(title, description, priority)
        messagebox.showinfo("موفقیت", f"کار با آیدی {task_id} اضافه شد!")
        
        # پاک کردن فیلدها
        title_entry.delete(0, tk.END)
        desc_entry.delete(0, tk.END)
        priority_var.set("متوسط")
        
        # تازه‌سازی لیست
        refresh_list()
    
    add_button = ttk.Button(add_frame, text="افزودن کار", command=add_task_gui)
    add_button.grid(row=2, column=2, padx=(20, 0), pady=(10, 0))
    
    # بخش لیست کارها
    list_frame = ttk.LabelFrame(main_frame, text="لیست کارها", padding="10")
    list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
    
    # جدول کارها
    columns = ('آیدی', 'عنوان', 'توضیحات', 'اولویت')
    task_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
    
    # تنظیم ستون‌ها
    for col in columns:
        task_tree.heading(col, text=col)
        if col == 'آیدی':
            task_tree.column(col, width=50, anchor='center')
        elif col == 'عنوان':
            task_tree.column(col, width=180)
        elif col == 'اولویت':
            task_tree.column(col, width=80, anchor='center')
        else:
            task_tree.column(col, width=250)
    
    # اسکرول بار
    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=task_tree.yview)
    task_tree.configure(yscrollcommand=scrollbar.set)
    
    task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    # دکمه حذف
    def delete_selected_task():
        selection = task_tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک کار را انتخاب کنید!")
            return
        
        item = task_tree.item(selection[0])
        task_id = item['values'][0]
        
        if messagebox.askyesno("تأیید", "آیا مطمئن هستید که می‌خواهید این کار را حذف کنید؟"):
            todo = ToDoList()
            if todo.delete_task(task_id):
                messagebox.showinfo("موفقیت", "کار حذف شد!")
                refresh_list()
            else:
                messagebox.showerror("خطا", "خطا در حذف کار!")
    
    delete_button = ttk.Button(list_frame, text="حذف کار انتخاب شده", command=delete_selected_task)
    delete_button.grid(row=1, column=0, pady=(10, 0))
    
    # دکمه نمودار
    def show_chart_gui():
        todo = ToDoList()
        todo.show_priority_chart()
    
    chart_button = ttk.Button(list_frame, text="نمایش نمودار", command=show_chart_gui)
    chart_button.grid(row=1, column=1, pady=(10, 0))
    
    # دکمه تازه‌سازی
    def refresh_list():
        for item in task_tree.get_children():
            task_tree.delete(item)
        
        todo = ToDoList()
        tasks = todo.get_all_tasks()
        for task in tasks:
            tags = ()
            if task.priority == "بالا":
                tags = ('high',)
            elif task.priority == "پایین":
                tags = ('low',)
            else:
                tags = ('medium',)
            
            task_tree.insert('', 'end', values=(task.id, task.title, task.description, task.priority), tags=tags)
        
        # تنظیم رنگ‌ها
        task_tree.tag_configure('high', background='#ffebee')
        task_tree.tag_configure('medium', background='#fff8e1')
        task_tree.tag_configure('low', background='#e8f5e8')
    
    refresh_button = ttk.Button(list_frame, text="تازه‌سازی", command=refresh_list)
    refresh_button.grid(row=1, column=2, pady=(10, 0))
    
    # تنظیم وزن ستون‌ها
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(2, weight=1)
    list_frame.columnconfigure(0, weight=1)
    list_frame.rowconfigure(0, weight=1)
    
    # بارگذاری اولیه
    refresh_list()
    
    root.mainloop()


if __name__ == "__main__":
    # اجرای مستقیم رابط گرافیکی
    gui_menu()


