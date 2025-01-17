import tkinter as tk
import random
import time

class ConveyorBeltSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Симуляция расфасовки муки")

        # Панель с информацией слева
        self.info_frame = tk.Frame(root)
        self.info_frame.pack(side="left", padx=20)

        # Поля информации
        self.type_label = tk.Label(self.info_frame, text="Тип мешка: null", font=("Arial", 14))
        self.type_label.pack()
        self.voltage_label = tk.Label(self.info_frame, text="Напряжение: 0 В", font=("Arial", 14))
        self.voltage_label.pack()

        self.f1_label = tk.Label(self.info_frame, text="Датчик ФЭ1 (наличие мешка): 0", font=("Arial", 14))
        self.f1_label.pack()
        self.f2_label = tk.Label(self.info_frame, text="Датчик ФЭ2 (тип мешка): 0", font=("Arial", 14))
        self.f2_label.pack()
        self.lock_label = tk.Label(self.info_frame, text="Блокировка загрузки: 0", font=("Arial", 14))
        self.lock_label.pack()

        self.status_label = tk.Label(self.info_frame, text="Статус: ожидание", font=("Arial", 14))
        self.status_label.pack()

        # Масса бункера с возможностью редактирования
        self.bunker_mass_label = tk.Label(self.info_frame, text="Масса в бункере:", font=("Arial", 14))
        self.bunker_mass_label.pack()
        self.bunker_mass_entry = tk.Entry(self.info_frame, font=("Arial", 14))
        self.bunker_mass_entry.insert(0, "5000")  # Начальная масса 5000 кг
        self.bunker_mass_entry.pack()

        # Добавим новое поле для массы мешка
        self.bag_mass_label = tk.Label(self.info_frame, text="Масса мешка: 0 кг", font=("Arial", 14))
        self.bag_mass_label.pack()

        # Холст для анимации
        self.canvas = tk.Canvas(root, width=800, height=400, bg="white")
        self.canvas.pack()

        # Элементы на холсте
        self.belt = self.canvas.create_rectangle(0, 200, 800, 250, fill="gray")
        self.dosator = self.canvas.create_polygon(380, 100, 420, 100, 400, 150, fill="blue")
        self.bag = None

        # Управление
        self.start_button = tk.Button(root, text="Старт", command=self.start_simulation)
        self.start_button.pack(side="left")
        self.stop_button = tk.Button(root, text="Остановить", command=self.stop_simulation)
        self.stop_button.pack(side="left")

        # Переменные состояния
        self.running = False
        self.bag_speed = 10
        self.bag_position = -50
        self.bag_filling = False  # Состояние заполнения
        self.bag_mass = 0  # Масса мешка
        self.locked = False  # Блокировка загрузки
        self.bunker_mass = 5000  # Начальная масса в бункере
        self.fill_time = 0  # Время для заполнения мешка (в секундах)
        self.start_time = 0  # Время начала заполнения

        # Сообщение об ошибке
        self.error_message_label = tk.Label(root, text="", font=("Arial", 14), fg="red")
        self.error_message_label.pack()

        # Функция обновления
        self.update_animation()

    def start_simulation(self):
        try:
            self.bunker_mass = float(self.bunker_mass_entry.get())
            # Проверка на переполнение бункера
            if self.bunker_mass > 8000:
                self.stop_simulation()
                self.status_label.config(text="Статус: Бункер переполнен")
                self.error_message_label.config(text="Ошибка: Бункер переполнен")
                return
            elif self.bunker_mass <= 0:
                self.stop_simulation()
                self.status_label.config(text="Статус: Недостаточно муки в бункере")
                self.error_message_label.config(text="Ошибка: Недостаточно муки в бункере")
                return
            else:
                self.error_message_label.config(text="")  # Очищаем сообщение об ошибке

            if not self.running:
                self.running = True

                # Проверяем, существует ли мешок и если его нет, то создаем новый
                if self.bag is None or self.bag_position > 800:
                    self.spawn_bag()

        except ValueError:
            self.error_message_label.config(text="Ошибка: Неверный формат массы бункера")

    def stop_simulation(self):
        self.running = False

    def spawn_bag(self):
        self.bag_position = -50
        bag_height = random.choice([30, 50])  # Высота для определения типа мешка
        self.bag = self.canvas.create_rectangle(
            self.bag_position, 200 - bag_height, self.bag_position + 50, 200, fill="brown"
        )
        self.type_label.config(text="Тип мешка: null")
        self.voltage_label.config(text="Напряжение: 0 В")

        # Обновление датчиков
        self.f1_label.config(text="Датчик ФЭ1 (наличие мешка): 1")
        self.f2_label.config(text="Датчик ФЭ2 (тип мешка): 0")  # Пока 15 кг
        self.status_label.config(text="Статус: ожидание")

    def update_animation(self):
        if self.running and self.bag:
            if not self.bag_filling:  # Если мешок не заполняется
                self.bag_position += self.bag_speed
                self.canvas.move(self.bag, self.bag_speed, 0)

                # Если мешок вышел за пределы экрана, удаляем его и создаем новый
                if self.bag_position > 800:
                    self.canvas.delete(self.bag)  # Удаляем мешок с холста
                    self.bag = None  # Обнуляем переменную мешка
                    self.spawn_bag()  # Создаем новый мешок

                # Проверка под дозатором
                if 375 <= self.bag_position <= 380 and self.bunker_mass > 0:
                    self.bag_filling = True
                    bag_coords = self.canvas.coords(self.bag)
                    bag_height = bag_coords[3] - bag_coords[1]
                    bag_type = "30 кг" if bag_height == 50 else "15 кг"
                    voltage = 32 if bag_type == "30 кг" else 16

                    self.type_label.config(text=f"Тип мешка: {bag_type}")
                    self.voltage_label.config(text=f"Напряжение: {voltage} В")
                    self.f2_label.config(text=f"Датчик ФЭ2 (тип мешка): {1 if bag_type == '30 кг' else 0}")
                    self.status_label.config(text="Статус: заполнение")

                    # Инициализация массы мешка
                    self.bag_mass = 0
                    self.target_bag_mass = 30 if bag_type == "30 кг" else 15
                    self.start_time = time.time()

                    # Обновляем массу мешка в интерфейсе
                    self.bag_mass_label.config(text=f"Масса мешка: {self.bag_mass} кг")

            # Заполнение мешка и уменьшение массы из бункера
            if self.bag_filling:
                elapsed_time = time.time() - self.start_time
                fill_rate = 0.3  # Ускоряем скорость наполнения (кг в секунду)

                # Плавное увеличение массы мешка и уменьшение массы в бункере
                if self.bag_mass < self.target_bag_mass and self.bunker_mass > 0:
                    self.bag_mass += fill_rate
                    self.bunker_mass -= fill_rate
                    self.start_time = time.time()  # сброс таймера для плавности

                    # Обновляем массу мешка в интерфейсе
                    self.bag_mass_label.config(text=f"Масса мешка: {self.bag_mass:.1f} кг")

                    # Обновляем массу в бункере в поле ввода
                    self.bunker_mass_entry.delete(0, tk.END)
                    self.bunker_mass_entry.insert(0, f"{self.bunker_mass:.1f}")

                    # Изменение напряжения в зависимости от массы мешка
                    remaining_mass = self.target_bag_mass - self.bag_mass
                    if remaining_mass > 5:
                        voltage = 31.5
                    elif remaining_mass > 1:
                        voltage = 18.5
                    elif remaining_mass > 0.4:
                        voltage = 18
                    else:
                        voltage = 0

                    self.voltage_label.config(text=f"Напряжение: {voltage:.1f} В")

                # Когда мешок заполнился
                if self.bag_mass >= self.target_bag_mass:
                    self.bag_filling = False
                    self.status_label.config(text="Статус: мешок готов")
                    self.bag_mass_label.config(text=f"Масса мешка: {self.bag_mass:.1f} кг")

        self.root.after(50, self.update_animation)

# Запуск приложения
root = tk.Tk()
simulation = ConveyorBeltSimulation(root)
root.mainloop()
