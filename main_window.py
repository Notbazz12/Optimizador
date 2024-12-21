import sys
import os
import subprocess
import psutil
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QTabWidget, 
                             QProgressBar, QStyleFactory, QWidget)
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtCore import Qt, QTimer

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from utils.storage import analyze_storage, find_large_files, find_duplicate_files
except ImportError:
    print("Error: No se pudo importar el módulo utils.storage")
    print("Directorio actual:", current_dir)
    print("Python path:", sys.path)
    sys.exit(1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimizador de Recursos")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 18px;
                color: #333;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                padding: 10px 20px;
            }
            QTabBar::tab:selected {
                background-color: white;
            }
        """)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Título principal
        title_label = QLabel("Optimizador de Recursos del Sistema")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        main_layout.addWidget(title_label)

        # Pestañas para diferentes módulos
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Pestaña de Almacenamiento
        storage_tab = QWidget()
        storage_layout = QVBoxLayout(storage_tab)
        tabs.addTab(storage_tab, QIcon("icons/storage.png"), "Almacenamiento")

        # Sección de análisis de almacenamiento
        storage_analysis_layout = QHBoxLayout()
        analyze_button = QPushButton("Analizar Almacenamiento")
        analyze_button.setIcon(QIcon("icons/analyze.png"))
        analyze_button.clicked.connect(self.analyze_storage)
        storage_analysis_layout.addWidget(analyze_button)
        
        self.storage_info_label = QLabel("Información de Almacenamiento:")
        storage_analysis_layout.addWidget(self.storage_info_label)
        storage_layout.addLayout(storage_analysis_layout)

        # Gráfico de uso de almacenamiento
        self.storage_chart = QProgressBar()
        self.storage_chart.setTextVisible(False)
        storage_layout.addWidget(self.storage_chart)

        # Tablas para archivos grandes y duplicados
        tables_layout = QHBoxLayout()
        
        large_files_layout = QVBoxLayout()
        large_files_label = QLabel("Archivos Grandes:")
        large_files_layout.addWidget(large_files_label)
        self.large_files_table = QTableWidget()
        self.large_files_table.setColumnCount(2)
        self.large_files_table.setHorizontalHeaderLabels(["Archivo", "Tamaño (MB)"])
        large_files_layout.addWidget(self.large_files_table)
        tables_layout.addLayout(large_files_layout)

        duplicate_files_layout = QVBoxLayout()
        duplicate_files_label = QLabel("Archivos Duplicados:")
        duplicate_files_layout.addWidget(duplicate_files_label)
        self.duplicate_files_table = QTableWidget()
        self.duplicate_files_table.setColumnCount(2)
        self.duplicate_files_table.setHorizontalHeaderLabels(["Archivo 1", "Archivo 2"])
        duplicate_files_layout.addWidget(self.duplicate_files_table)
        tables_layout.addLayout(duplicate_files_layout)

        storage_layout.addLayout(tables_layout)

        # Botones de acción
        action_buttons_layout = QHBoxLayout()
        
        clear_cache_button = QPushButton("Depurar Caché y RAM")
        clear_cache_button.setIcon(QIcon("icons/cache.png"))
        clear_cache_button.clicked.connect(self.clear_cache)
        action_buttons_layout.addWidget(clear_cache_button)

        clear_temp_button = QPushButton("Limpiar Archivos Temporales")
        clear_temp_button.setIcon(QIcon("icons/temp.png"))
        clear_temp_button.clicked.connect(self.clear_temp_files)
        action_buttons_layout.addWidget(clear_temp_button)

        manage_startup_button = QPushButton("Gestionar Programas de Inicio")
        manage_startup_button.setIcon(QIcon("icons/startup.png"))
        manage_startup_button.clicked.connect(self.manage_startup_programs)
        action_buttons_layout.addWidget(manage_startup_button)

        storage_layout.addLayout(action_buttons_layout)

        # Pestaña de Rendimiento
        performance_tab = QWidget()
        performance_layout = QVBoxLayout(performance_tab)
        tabs.addTab(performance_tab, QIcon("icons/performance.png"), "Rendimiento")

        self.cpu_usage_bar = QProgressBar()
        self.cpu_usage_bar.setTextVisible(True)
        performance_layout.addWidget(QLabel("Uso de CPU:"))
        performance_layout.addWidget(self.cpu_usage_bar)

        self.memory_usage_bar = QProgressBar()
        self.memory_usage_bar.setTextVisible(True)
        performance_layout.addWidget(QLabel("Uso de Memoria:"))
        performance_layout.addWidget(self.memory_usage_bar)

        monitor_performance_button = QPushButton("Iniciar Monitoreo")
        monitor_performance_button.setIcon(QIcon("icons/monitor.png"))
        monitor_performance_button.clicked.connect(self.toggle_performance_monitoring)
        performance_layout.addWidget(monitor_performance_button)

        self.performance_timer = QTimer(self)
        self.performance_timer.timeout.connect(self.update_performance)

        self.statusBar().showMessage('Listo')

    def analyze_storage(self):
        storage_info = analyze_storage()
        total_gb = storage_info['total']
        used_gb = storage_info['used']
        free_gb = storage_info['free']
        
        self.storage_info_label.setText(
            f"Total: {total_gb} GB, Usado: {used_gb} GB, Libre: {free_gb} GB"
        )
        
        # Actualizar gráfico de uso
        usage_percentage = (used_gb / total_gb) * 100
        self.storage_chart.setValue(int(usage_percentage))
        self.storage_chart.setFormat(f"{usage_percentage:.1f}% usado")
        
        # Color del gráfico basado en el uso
        if usage_percentage < 50:
            color = QColor(0, 255, 0)  # Verde
        elif usage_percentage < 80:
            color = QColor(255, 165, 0)  # Naranja
        else:
            color = QColor(255, 0, 0)  # Rojo
        
        self.storage_chart.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color.name()};
                width: 10px;
            }}
        """)

        # Encontrar archivos grandes
        large_files = list(find_large_files("/", size_threshold_mb=100))
        self.large_files_table.setRowCount(len(large_files))
        for row, (file_path, size_mb) in enumerate(large_files):
            self.large_files_table.setItem(row, 0, QTableWidgetItem(file_path))
            self.large_files_table.setItem(row, 1, QTableWidgetItem(f"{size_mb:.2f}"))

        # Encontrar archivos duplicados
        duplicate_files = find_duplicate_files("/")
        self.duplicate_files_table.setRowCount(len(duplicate_files))
        for row, (file1, file2) in enumerate(duplicate_files):
            self.duplicate_files_table.setItem(row, 0, QTableWidgetItem(file1))
            self.duplicate_files_table.setItem(row, 1, QTableWidgetItem(file2))

    def clear_cache(self):
        try:
            subprocess.run(['ipconfig', '/flushdns'], check=True)
            self.statusBar().showMessage('Caché DNS limpiado con éxito', 5000)
        except Exception as e:
            self.statusBar().showMessage(f'Error al limpiar caché DNS: {e}', 5000)

    def clear_temp_files(self):
        try:
            temp_dir = os.path.join(os.environ['TEMP'])
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                    except Exception:
                        continue
            self.statusBar().showMessage('Archivos temporales limpiados con éxito', 5000)
        except Exception as e:
            self.statusBar().showMessage(f'Error al limpiar archivos temporales: {e}', 5000)

    def manage_startup_programs(self):
        try:
            subprocess.run(['msconfig'], check=True)
            self.statusBar().showMessage('Configuración del sistema abierta', 5000)
        except Exception as e:
            self.statusBar().showMessage(f'Error al abrir la configuración del sistema: {e}', 5000)

    def toggle_performance_monitoring(self):
        if self.performance_timer.isActive():
            self.performance_timer.stop()
            self.statusBar().showMessage('Monitoreo detenido', 5000)
        else:
            self.performance_timer.start(1000)  # Actualizar cada segundo
            self.statusBar().showMessage('Monitoreo iniciado', 5000)

    def update_performance(self):
        # Actualizar uso de CPU
        cpu_percent = psutil.cpu_percent()
        self.cpu_usage_bar.setValue(int(cpu_percent))
        self.cpu_usage_bar.setFormat(f"{cpu_percent:.1f}%")

        # Actualizar uso de memoria
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        self.memory_usage_bar.setValue(int(memory_percent))
        self.memory_usage_bar.setFormat(f"{memory_percent:.1f}% ({memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB)")

        # Cambiar el color de las barras según el uso
        for bar in [self.cpu_usage_bar, self.memory_usage_bar]:
            value = bar.value()
            if value < 50:
                color = "green"
            elif value < 80:
                color = "orange"
            else:
                color = "red"
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    width: 10px;
                }}
            """)