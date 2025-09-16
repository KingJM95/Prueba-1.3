import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import sqlite3

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Programación Diaria y Tareas")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")

        # Conectar a la base de datos
        self.db_conn = self.connect_db()
        self.create_table()

        # Configurar la interfaz de usuario
        self.create_widgets()
        self.refresh_task_list()

    def connect_db(self):
        """Conecta a la base de datos SQLite."""
        conn = sqlite3.connect('tareas.db')
        return conn

    def create_table(self):
        """Crea la tabla de tareas si no existe."""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                prioridad TEXT,
                estado TEXT
            )
        ''')
        self.db_conn.commit()

    def create_widgets(self):
        """Crea los elementos de la interfaz (botones, campos de texto, etc.)."""
        # Frame principal para los campos de entrada
        input_frame = tk.Frame(self.root, bg="#e0e0e0", padx=15, pady=15, bd=2, relief="groove")
        input_frame.pack(fill=tk.X, padx=20, pady=10)

        # Título del programa
        tk.Label(input_frame, text="Agregar nueva tarea", font=("Helvetica", 14, "bold"), bg="#e0e0e0").grid(row=0, column=0, columnspan=2, pady=5)

        # Campo Título
        tk.Label(input_frame, text="Título:", bg="#e0e0e0").grid(row=1, column=0, sticky="w", pady=2)
        self.titulo_entry = tk.Entry(input_frame, width=50)
        self.titulo_entry.grid(row=1, column=1, pady=2)

        # Campo Descripción
        tk.Label(input_frame, text="Descripción:", bg="#e0e0e0").grid(row=2, column=0, sticky="w", pady=2)
        self.descripcion_entry = tk.Entry(input_frame, width=50)
        self.descripcion_entry.grid(row=2, column=1, pady=2)

        # Campo Fecha
        tk.Label(input_frame, text="Fecha (YYYY-MM-DD):", bg="#e0e0e0").grid(row=3, column=0, sticky="w", pady=2)
        self.fecha_entry = tk.Entry(input_frame, width=50)
        self.fecha_entry.grid(row=3, column=1, pady=2)
        self.fecha_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        # Campo Hora
        tk.Label(input_frame, text="Hora (HH:MM):", bg="#e0e0e0").grid(row=4, column=0, sticky="w", pady=2)
        self.hora_entry = tk.Entry(input_frame, width=50)
        self.hora_entry.grid(row=4, column=1, pady=2)
        self.hora_entry.insert(0, "09:00")

        # Campo Prioridad (Dropdown)
        tk.Label(input_frame, text="Prioridad:", bg="#e0e0e0").grid(row=5, column=0, sticky="w", pady=2)
        self.prioridad_var = tk.StringVar(self.root)
        self.prioridad_var.set("Baja") # Valor por defecto
        prioridad_opciones = ["Alta", "Media", "Baja"]
        self.prioridad_menu = tk.OptionMenu(input_frame, self.prioridad_var, *prioridad_opciones)
        self.prioridad_menu.grid(row=5, column=1, sticky="ew", pady=2)
        
        # Campo Estado (Dropdown)
        tk.Label(input_frame, text="Estado:", bg="#e0e0e0").grid(row=6, column=0, sticky="w", pady=2)
        self.estado_var = tk.StringVar(self.root)
        self.estado_var.set("Pendiente") # Valor por defecto
        estado_opciones = ["Pendiente", "En progreso", "Completado"]
        self.estado_menu = tk.OptionMenu(input_frame, self.estado_var, *estado_opciones)
        self.estado_menu.grid(row=6, column=1, sticky="ew", pady=2)
        
        # Botón para agregar la tarea
        add_button = tk.Button(input_frame, text="Agregar Tarea", command=self.add_task, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"), relief="raised")
        add_button.grid(row=7, column=0, columnspan=2, pady=10)

        # --- Sección de Visualización de Tareas ---
        task_list_frame = tk.Frame(self.root, bg="#f9f9f9", padx=15, pady=15, bd=2, relief="groove")
        task_list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Título de la lista
        tk.Label(task_list_frame, text="Lista de Tareas", font=("Helvetica", 14, "bold"), bg="#f9f9f9").pack(pady=5)
        
        # Lista de tareas (Treeview para una tabla)
        self.task_tree = ttk.Treeview(task_list_frame, columns=("ID", "Título", "Fecha", "Hora", "Prioridad", "Estado"), show="headings")
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Título", text="Título")
        self.task_tree.heading("Fecha", text="Fecha")
        self.task_tree.heading("Hora", text="Hora")
        self.task_tree.heading("Prioridad", text="Prioridad")
        self.task_tree.heading("Estado", text="Estado")
        
        self.task_tree.column("ID", width=30, anchor="center")
        self.task_tree.column("Título", width=250)
        self.task_tree.column("Fecha", width=100, anchor="center")
        self.task_tree.column("Hora", width=60, anchor="center")
        self.task_tree.column("Prioridad", width=80, anchor="center")
        self.task_tree.column("Estado", width=80, anchor="center")
        
        self.task_tree.pack(fill=tk.BOTH, expand=True)

        # Botones de acción para las tareas
        action_frame = tk.Frame(task_list_frame, bg="#f9f9f9")
        action_frame.pack(pady=5)

        tk.Button(action_frame, text="Eliminar Seleccionada", command=self.delete_selected_task, bg="#e57373", fg="white").pack(side="left", padx=5)
        tk.Button(action_frame, text="Completar Seleccionada", command=self.complete_selected_task, bg="#66BB6A", fg="white").pack(side="left", padx=5)

    def add_task(self):
        """Guarda la tarea en la base de datos y refresca la lista."""
        titulo = self.titulo_entry.get().strip()
        descripcion = self.descripcion_entry.get().strip()
        fecha = self.fecha_entry.get().strip()
        hora = self.hora_entry.get().strip()
        prioridad = self.prioridad_var.get()
        estado = self.estado_var.get()

        if not titulo or not fecha:
            messagebox.showerror("Error", "Los campos Título y Fecha son obligatorios.")
            return

        try:
            cursor = self.db_conn.cursor()
            cursor.execute("INSERT INTO tareas (titulo, descripcion, fecha, hora, prioridad, estado) VALUES (?, ?, ?, ?, ?, ?)",
                           (titulo, descripcion, fecha, hora, prioridad, estado))
            self.db_conn.commit()
            messagebox.showinfo("Éxito", "Tarea agregada correctamente.")
            self.clear_fields()
            self.refresh_task_list()
        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", f"Ocurrió un error: {e}")

    def refresh_task_list(self):
        """Lee todas las tareas de la DB y las muestra en la lista."""
        for row in self.task_tree.get_children():
            self.task_tree.delete(row)
        
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM tareas ORDER BY fecha, hora")
        tasks = cursor.fetchall()
        
        for task in tasks:
            self.task_tree.insert("", tk.END, values=task)

    def delete_selected_task(self):
        """Elimina la tarea seleccionada de la base de datos."""
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Por favor, selecciona una tarea para eliminar.")
            return

        task_id = self.task_tree.item(selected_item, 'values')[0]
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar esta tarea?"):
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("DELETE FROM tareas WHERE id = ?", (task_id,))
                self.db_conn.commit()
                messagebox.showinfo("Éxito", "Tarea eliminada correctamente.")
                self.refresh_task_list()
            except sqlite3.Error as e:
                messagebox.showerror("Error de base de datos", f"Ocurrió un error: {e}")

    def complete_selected_task(self):
        """Actualiza el estado de la tarea seleccionada a 'Completado'."""
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Por favor, selecciona una tarea para completar.")
            return

        task_id = self.task_tree.item(selected_item, 'values')[0]
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("UPDATE tareas SET estado = 'Completado' WHERE id = ?", (task_id,))
            self.db_conn.commit()
            messagebox.showinfo("Éxito", "Tarea marcada como 'Completado'.")
            self.refresh_task_list()
        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", f"Ocurrió un error: {e}")

    def clear_fields(self):
        """Limpia los campos de entrada después de agregar una tarea."""
        self.titulo_entry.delete(0, tk.END)
        self.descripcion_entry.delete(0, tk.END)
        self.fecha_entry.delete(0, tk.END)
        self.hora_entry.delete(0, tk.END)
        self.prioridad_var.set("Baja")
        self.estado_var.set("Pendiente")


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
      
