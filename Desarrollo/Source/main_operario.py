import sys
import sqlite3
from datetime import datetime, time
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QPushButton, QMessageBox, QGridLayout, QLabel, QComboBox, QListView, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QTime, QRegExp
from PyQt5.QtGui import QPixmap, QIcon, QColor, QFont, QRegExpValidator

# Importar el script del lector RFID
from PyQt5.QtCore import QThread, pyqtSignal
from evdev import InputDevice, categorize, ecodes, list_devices

class RFIDThread(QThread):
    data_read = pyqtSignal(str)  # Señal para enviar los datos leídos del RFID

    def run(self):
        # Encuentra el dispositivo de entrada del lector RFID
        devices = [InputDevice(fn) for fn in list_devices()]
        rfid_device = None
        for device in devices:
            if 'IC Reader' in device.name or "ARM CM0 USB HID Keyboard" in device.name:
                rfid_device = device
                break

        if not rfid_device:
            print("RFID device not found")
            return

        buffer = ""

        # Procesa eventos del dispositivo de entrada
        try:
            for event in rfid_device.read_loop():
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == key_event.key_down:
                        if key_event.keycode == 'KEY_ENTER':
                            # Emitir señal con los datos leídos
                            self.data_read.emit(buffer)
                            buffer = ""
                        elif key_event.keycode == 'KEY_ESC':
                            break
                        else:
                            buffer += key_event.keycode.lstrip('KEY_').lower()
        except Exception as e:
            print(f"Error reading from RFID device: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.tamañoFuenteTitulos = 120
        self.anchoVentana = 1920      # Ancho por defecto de la ventana
        self.altoVentana = 1080
        
        self.tamañoFuenteReloj = 40
        self.colorFuenteReloj1 = "#0D5690"
        self.colorFuenteReloj2 = "#FFFFFF"
        self.tipografia = "Poppins"
        self.colorFuente = "#727272"
        self.colorFuente2 = "#1D8DD0"
        self.colorError = "#E10909"
        self.colorFuenteServicio= "#0D5690"
        self.tamañoFuentePrincipal = 36
        self.tamañoFuenteSecundario = 26
        self.tamañoFuenteAvisos = 25
        self.tamañoFuenteTerciario = 55
        self.sede = "Planchado"
        self.rfid_thread = None  # Inicializar el hilo del lector RFID
        self.db = "Desarrollo/Database/marmato_db.db"
        
        self.areas=['Seleccionar','Sin asignar','Directo','ADMINISTRACION MINA LA MARUJA','ADMINISTRACION GENERAL','AMBIENTAL','PEQUEÑA MINERIA','ASUNTOS CORPORATIVOS Y SOCIAL','ALMACEN MATERIALES Y SUMINISTROS OPERACION',
                    'COO CORP. G&A','EXPLORACION','FINANCIERA CORP. G&A','TECNOLOGIAS DE INFORMACION Y COMUNICACIÓN','ADMINISTRACION LABORATORIO QUIMICO','LM','ADMINISTRACION MANTENIMIENTOS',
                    'ADMINISTRACION PLANTA DE BENEFICIO','PROYECTOS','SALUD OCUPACIONAL Y SEGURIDAD INDUSTRIAL','RECURSOS HUMANOS','RELAVES','ADMINISTRACION SEGURIDAD']
        
        self.allowed_characters_numeric = "0-9"  # Permitir solo dígitos
        self.allowed_characters_alpha = "a-zA-Z "  # Permitir letras y dígitos
        
        self.setWindowTitle("Menu Principal")
        self.setGeometry(0, 0, self.anchoVentana, self.altoVentana)
        self.showMaximized()
        
        self.menu_principal=QWidget(self) #check
        self.menu_usuarios=QWidget(self) #check
        self.menu_formulario_usuarioN=QWidget(self) #check
        self.menu_confirmar_usuarioN=QWidget(self) #check 
        self.menu_lista_usuarios=QWidget(self) #check
        self.menu_editar_usuario=QWidget(self) #check
        self.menu_confirmar_usuarioE=QWidget(self) #check
        self.menu_registros=QWidget(self) 
        self.menu_registro_tarjeta=QWidget(self)
        self.menu_registro_tarjeta_invalida=QWidget(self)
        self.menu_registro_manual=QWidget(self)
        self.menu_registro_manualE=QWidget(self)
        self.menu_registro_manualN=QWidget(self)
        self.menu_confirmar_registro_manualN=QWidget(self) #check
        self.menu_confirmar_registro_manualE=QWidget(self) #check
        self.menu_aprobar_pedidos=QWidget(self)
        
        
        self.clock_widget = self.create_clock_widget()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        self.init_menu_principal()
        
        self.setCentralWidget(self.menu_principal)
        
    ### DEFINICION GENERAL DE WIDGETS
    
    def get_current_service(self, database_path):
        # Conectar a la base de datos
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Obtener la hora actual
        now = datetime.now().time()
        
        # Consulta para obtener el servicio actual basado en la hora y flag_horario
        query = """
        SELECT tipo, hora_inicio, hora_fin 
        FROM menu 
        WHERE flag_horario = 1
        """
        
        cursor.execute(query)
        services = cursor.fetchall()
        
        # Cerrar la conexión
        conn.close()
        
        # Iterar sobre los servicios para encontrar el servicio actual
        for service in services:
            tipo, hora_inicio, hora_fin = service
            inicio = datetime.strptime(hora_inicio, "%H:%M").time()
            fin = datetime.strptime(hora_fin, "%H:%M").time()
            
            if inicio <= now <= fin:
                return tipo
        
        # Si no se encuentra ningún servicio actual
        return "No hay servicio"
        
    def update_service_label(self):
        self.valor_servicio_actual = self.get_current_service(self.db)
        self.menu_principal_label_servicio.setText(f"Servicio: {self.valor_servicio_actual}")
        
    def update_service_label2(self):
        self.valor_servicio_actual = self.get_current_service(self.db)
        self.menu_registros_label_servicio.setText(f"Servicio: {self.valor_servicio_actual}")
        
    def update_time(self):
        current_time = QTime.currentTime()
        time_string = current_time.toString("h:mm ap")
        self.clock_widget.setText(time_string)
            
    def create_clock_widget(self):
        clock_widget = QLabel("", self)
        clock_widget.setGeometry(1652, 70, 200, 60)
        clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj1}; font-family: {self.tipografia}")
        return clock_widget
    
    def set_background_image(self, menu, image_path):
        palette = self.palette()
        palette.setBrush(self.backgroundRole(), Qt.transparent)
        self.setPalette(palette)
        pixmap = QPixmap(image_path)
        self.background_label = QLabel(menu)
        self.background_label.setGeometry(0, 0, self.anchoVentana, self.altoVentana)
        self.background_label.setPixmap(pixmap.scaled(self.anchoVentana, self.altoVentana))
        
    def set_background_images(self, menu, image_path1, image_path2):
        self.background_label1 = QLabel(menu)
        self.background_label1.setGeometry(0, 0, self.anchoVentana, self.altoVentana)
        pixmap1 = QPixmap(image_path1)
        self.background_label1.setPixmap(pixmap1.scaled(self.anchoVentana, self.altoVentana))
        
        self.background_label2 = QLabel(menu)
        self.background_label2.setGeometry(0, 0, self.anchoVentana, self.altoVentana)
        pixmap2 = QPixmap(image_path2)
        self.background_label2.setPixmap(pixmap2.scaled(self.anchoVentana, self.altoVentana))
        self.background_label2.lower()  # Poner fondo_2.png por debajo de fondo_1.png

    def create_label(self, menu, text, x, y, width, height, font_size, font_color, font_family, flag):
        label = QLabel(text, menu)
        label.setGeometry(x, y, width, height)
        if flag:
            label.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family}; font-weight: bold")  
        else:
            label.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family};")
        return label
    
    def create_image_button(self, menu, image_path, width, height, x, y, action, transparent):
        button = QPushButton(menu)
        button.setGeometry(x, y, width, height)
        pixmap = QPixmap(image_path)
        icon = QIcon(pixmap)
        button.setIcon(icon)
        button.setIconSize(pixmap.size())
        button.clicked.connect(action)
        if transparent:
            button.setStyleSheet("background-color: transparent; border: none;")
        return button
    
    def create_hover_image_button(self, menu, normal_image_path, hover_image_path, width, height, x, y, action, transparent):
        button = QPushButton(menu)
        button.setGeometry(x, y, width, height)
        normal_pixmap = QPixmap(normal_image_path)
        hover_pixmap = QPixmap(hover_image_path)
        normal_icon = QIcon(normal_pixmap)
        hover_icon = QIcon(hover_pixmap)
        
        button.setIcon(normal_icon)
        button.setIconSize(normal_pixmap.size())
        button.clicked.connect(action)
        
        if transparent:
            button.setStyleSheet("background-color: transparent; border: none;")
        
        # Define the enterEvent and leaveEvent within the method
        def enterEvent(event):
            button.setIcon(hover_icon)
            super(QPushButton, button).enterEvent(event)

        def leaveEvent(event):
            button.setIcon(normal_icon)
            super(QPushButton, button).leaveEvent(event)

        # Attach the events to the button
        button.enterEvent = enterEvent
        button.leaveEvent = leaveEvent
        
        return button
    
    def create_text_button(self, menu, text, x, y, width, height, font_size, font_color, font_family, action, no_border):
        button = QPushButton(text, menu)
        button.setGeometry(x, y, width, height)
        button.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family};")
        button.clicked.connect(action)
        if no_border:
            button.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family}; background-color: transparent; border: none;")  # Removiendo el borde
        else:
            button.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family};")
        return button
    
    def create_dropdown_menu(self, menu, x, y, width, height, options, index=0):
        dropdown_menu = QComboBox(menu)
        dropdown_menu.setGeometry(x, y, width, height)
        dropdown_menu.addItems(options)
        dropdown_menu.setCurrentIndex(index)
        
        # Usar QListView para habilitar el scroll
        list_view = QListView()
        dropdown_menu.setView(list_view)

        dropdown_menu.setMaxVisibleItems(len(options))
    
        dropdown_menu.view().setFixedSize(width, min(400, len(options) * 30))
    
        return dropdown_menu

    def create_entry(self, menu, x, y, width, height, text=""):
        entry = QLineEdit(menu)
        entry.setGeometry(x, y, width, height)
        entry.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
        entry.setText(text)
        return entry
    
    def cargar_datos_usuarios(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        cursor.execute("SELECT nombre, cedula, rol FROM usuarios WHERE flag_retirado = 0 ORDER BY fecha_ultima_modificacion DESC")
        self.rows = cursor.fetchall()  # Guardar los datos en un atributo de la instancia
        connection.close()
        self.actualizar_tabla_usuarios(self.rows)
        
    def cargar_datos_pedidos(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        cursor.execute("SELECT fecha, hora, tipo, cantidad, area, estado FROM pedidos ORDER BY fecha_ultima_modificacion DESC")
        self.rows = cursor.fetchall()  # Guardar los datos en un atributo de la instancia
        connection.close()
        self.actualizar_tabla_pedidos(self.rows)

    def actualizar_tabla_usuarios(self, rows):
        self.menu_lista_usuarios_tabla.setRowCount(len(rows))
        
        for row_index, row_data in enumerate(rows):
            for column_index, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignLeft)
                self.menu_lista_usuarios_tabla.setItem(row_index, column_index, item)
            
            # Crear y configurar el checkbox centrado
            checkbox = QCheckBox()
            checkbox.setFixedSize(15, 15)
            checkbox_layout = QHBoxLayout()
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_container = QWidget()
            checkbox_container.setLayout(checkbox_layout)
            self.menu_lista_usuarios_tabla.setCellWidget(row_index, 3, checkbox_container)
            
    def actualizar_tabla_pedidos(self, rows):
        self.menu_lista_pedidos_tabla.setRowCount(len(rows))
        
        for row_index, row_data in enumerate(rows):
            for column_index, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignLeft)
                self.menu_lista_pedidos_tabla.setItem(row_index, column_index, item)
            
            # Crear y configurar el checkbox centrado
            checkbox = QCheckBox()
            checkbox.setFixedSize(15, 15)
            checkbox_layout = QHBoxLayout()
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_container = QWidget()
            checkbox_container.setLayout(checkbox_layout)
            self.menu_lista_pedidos_tabla.setCellWidget(row_index, 6, checkbox_container)

    def filtrar_tabla_usuarios(self):
        filtro_texto = self.menu_lista_usuarios_entry_filtro.text()
        filtro_tipo = self.menu_lista_usuarios_dropdown_menu.currentText()
        
        if filtro_tipo == "Seleccionar":
            filtrados = self.rows
        else:
            filtrados = [row for row in self.rows if filtro_texto.lower() in row[self.get_usuarios_column_index(filtro_tipo)].lower()]
        
        self.actualizar_tabla_usuarios(filtrados)
        
    def filtrar_tabla_pedidos(self):
        filtro_texto = self.menu_lista_pedidos_entry_filtro.text()
        filtro_tipo = self.menu_lista_pedidos_dropdown_menu.currentText()
        
        if filtro_tipo == "Seleccionar":
            filtrados = self.rows
        else:
            filtrados = [row for row in self.rows if filtro_texto.lower() in row[self.get_pedidos_column_index(filtro_tipo)].lower()]
        
        self.actualizar_tabla_pedidos(filtrados)
        
    def get_usuarios_column_index(self, filtro_tipo):
        if filtro_tipo == "Nombre":
            return 0
        elif filtro_tipo == "Cedula":
            return 1
        else:
            return -1

    def get_pedidos_column_index(self, filtro_tipo):
        if filtro_tipo == "Tipo":
            return 2
        elif filtro_tipo == "Área":
            return 4
        else:
            return -1
        
    def on_menu_formulario_usuarioN_rfid_data_received(self, data):
        # Escribir los datos leídos en el entry de la tarjeta
        self.menu_formulario_usuarioN_entry_tarjeta.setText(data)
        
    def on_menu_formulario_usuarioE_rfid_data_received(self, data):
        # Escribir los datos leídos en el entry de la tarjeta
        self.menu_editar_usuario_entry_tarjeta.setText(data)
        
    def on_menu_registros_rfid_data_received(self, data):
        # Conectar a la base de datos
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Buscar en la tabla usuarios donde id_tarjeta coincida con el valor de data
        cursor.execute("SELECT nombre, cedula, rol FROM usuarios WHERE id_tarjeta = ?", (data,))
        result = cursor.fetchone()

        if result:
            nombre, cedula, rol = result
            servicio = self.valor_servicio_actual
            now = datetime.now()
            fecha = now.strftime("%Y-%m-%d")
            hora = now.strftime("%H:%M")
            sede = self.sede
            id_registro = f"{fecha}-{hora}-{servicio}-{sede}-{cedula}"
            self.join_rfid_thread()
            self.timer_servicio2.stop()
            
            # Verificar que la cédula no exista en la base de datos
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM registros WHERE cedula = ? AND tipo = ? AND fecha = ?", (cedula, servicio, fecha))
            result = cursor.fetchone()
            conn.close()
            
            if result[0]>0:
                self.menu_registro_tarjeta_invalida = QWidget(self)
                self.init_menu_registro_tarjeta_invalida()
                self.setCentralWidget(self.menu_registro_tarjeta_invalida)
            else:
                self.menu_registro_tarjeta = QWidget(self)
                self.init_menu_confirmar_registro_tarjeta(cedula, nombre, rol, servicio)
                self.setCentralWidget(self.menu_registro_tarjeta)
        else:
            self.join_rfid_thread()
            self.timer_servicio2.stop()
            self.menu_registro_tarjeta_invalida = QWidget(self)
            self.init_menu_registro_tarjeta_invalida()
            self.setCentralWidget(self.menu_registro_tarjeta_invalida)

        # Cerrar la conexión a la base de datos
        conn.close()
        
    def on_menu_aprobar_pedidos_rfid_data_received(self, data):
        # Conectar a la base de datos
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Recuperar el rol del usuario con el id_tarjeta correspondiente a data
        cursor.execute('SELECT rol, cedula FROM usuarios WHERE id_tarjeta=?', (data,))
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado:
            rol, cedula = resultado

            if rol == "Revisor":
                # Conectar a la base de datos
                conn = sqlite3.connect(self.db)
                cursor = conn.cursor()
                fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                try:
                    # Crear una consulta SQL para actualizar el campo estado
                    query = '''UPDATE pedidos SET estado = ?, fecha_ultima_modificacion = ?, cedula_aprobador = ? 
                    WHERE id_pedido IN ({seq})'''.format(seq=','.join(['?']*len(self.lista_id_pedido)))

                    # Ejecutar la consulta con los parámetros
                    cursor.execute(query, ["Aprobado", fecha_actual, cedula] + self.lista_id_pedido)

                    # Confirmar los cambios
                    conn.commit()
                    
                except sqlite3.Error as e:
                    conn.rollback()  # Revertir cambios en caso de error
                finally:
                    # Cerrar la conexión a la base de datos
                    conn.close()
                self.menu_aprobar_pedidos_label.setStyleSheet(f"font-size: {36}px; color: {self.colorFuenteReloj1}; font-family: {self.tipografia}")
                self.menu_aprobar_pedidos_label.setText("Pedidos aprobados exitosamente")
                self.join_rfid_thread()
            else:
                self.menu_aprobar_pedidos_label.setStyleSheet(f"font-size: {36}px; color: {self.colorError}; font-family: {self.tipografia}")
                self.menu_aprobar_pedidos_label.setText("Coloque una tarjeta autorizada")
        else:
            pass

    


### DEFINICION DE MENUS
    
    def init_menu_principal(self):
        self.set_background_image(self.menu_principal, "Desarrollo/Assets/menuPrincipal/fondo.png")
        
        self.setWindowTitle("Menu Principal")
        self.clock_widget.setParent(self.menu_principal)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj1}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        
        boton_usuarios = self.create_hover_image_button(self.menu_principal, "Desarrollo/Assets/menuPrincipalOp/boton_usuarios_1.png", "Desarrollo/Assets/menuPrincipalOp/boton_usuarios_2.png", 432, 345, 505, 462, self.on_menu_principal_usuarios_clicked, True)
        boton_pedidos = self.create_hover_image_button(self.menu_principal, "Desarrollo/Assets/menuPrincipalOp/boton_pedidos_1.png", "Desarrollo/Assets/menuPrincipalOp/boton_pedidos_2.png", 432, 345, 999, 462, self.on_menu_principal_pedidos_clicked, True)
        boton_registros = self.create_hover_image_button(self.menu_principal, "Desarrollo/Assets/menuPrincipalOp/boton_registro_1.png", "Desarrollo/Assets/menuPrincipalOp/boton_registro_2.png", 926, 117, 505, 854, self.on_menu_principal_registros_clicked, True)
        
        # Crear el label
        self.menu_principal_label_servicio = self.create_label(self.menu_principal, "", 628, 310, 800, 105, 70, self.colorFuenteServicio, self.tipografia, False)
        self.menu_principal_label_servicio.show()
        self.menu_principal_label_servicio.setAlignment(Qt.AlignCenter)

        # Actualizar el servicio actual al iniciar
        self.update_service_label()
        
        # Crear un timer para actualizar el servicio cada minuto
        self.timer_servicio = QTimer(self)
        self.timer_servicio.timeout.connect(self.update_service_label)
        self.timer_servicio.start(60000)  # Actualizar cada 60 segundos
        
    def init_menu_usuarios(self):
        self.set_background_image(self.menu_usuarios, "Desarrollo/Assets/menuUsuarios/fondo.png")
        
        self.setWindowTitle("Menu Usuarios")
        self.clock_widget.setParent(self.menu_usuarios)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj1}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        boton_agregar = self.create_hover_image_button(self.menu_usuarios, "Desarrollo/Assets/menuUsuarios/boton_agregar_perfil_1.png", "Desarrollo/Assets/menuUsuarios/boton_agregar_perfil_2.png", 500, 355, 428, 397, self.on_menu_usuarios_agregar_clicked, True)
        boton_editar = self.create_hover_image_button(self.menu_usuarios, "Desarrollo/Assets/menuUsuarios/boton_editar_perfil_1.png", "Desarrollo/Assets/menuUsuarios/boton_editar_perfil_2.png", 500, 355, 991, 397, self.on_menu_usuarios_editar_clicked, True)
        
        boton_atras = self.create_image_button(self.menu_usuarios, "Desarrollo/Assets/Commons/boton_atras.png", 143, 63, 1670, 908, self.on_menu_usuarios_atras_clicked, True)
        
    def init_menu_formulario_usuarioN(self):
        self.set_background_image(self.menu_formulario_usuarioN, "Desarrollo/Assets/menuFormularioUsuarioNOp/fondo.png")
        
        self.setWindowTitle("Formulario Usuario Nuevo")
        self.clock_widget.setParent(self.menu_formulario_usuarioN)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        self.label_errores=QLabel("", self)
        self.label_errores.setStyleSheet(f"font-size: {self.tamañoFuenteSecundario}px; color: {self.colorError}; font-family: {self.tipografia}")
        self.label_errores.setParent(self.menu_formulario_usuarioN)
        
        self.menu_formulario_usuarioN_entry_tarjeta = self.create_entry(self.menu_formulario_usuarioN, 957, 380, 434, 52)
        self.menu_formulario_usuarioN_entry_tarjeta.setReadOnly(True)
        self.menu_formulario_usuarioN_entry_cedula = self.create_entry(self.menu_formulario_usuarioN, 957, 461, 434, 52)
        self.menu_formulario_usuarioN_entry_nombre = self.create_entry(self.menu_formulario_usuarioN, 957, 543, 434, 52)
        
        self.menu_formulario_usuarioN_rol_drop = self.create_dropdown_menu(self.menu_formulario_usuarioN, 957, 625, 434, 52, self.areas)
        
        boton_cancelar = self.create_text_button(self.menu_formulario_usuarioN, "Cancelar", 762, 730, 168, 40, self.tamañoFuentePrincipal, self.colorFuente, self.tipografia, self.on_menu_formulario_usuarioN_cancelar_clicked, True)
        boton_aceptar = self.create_image_button(self.menu_formulario_usuarioN, "Desarrollo/Assets/Commons/boton_aceptar.png", 201, 60, 957, 720, self.on_menu_formulario_usuarioN_aceptar_clicked, True)
        boton_cerrar = self.create_image_button(self.menu_formulario_usuarioN, "Desarrollo/Assets/Commons/x.png", 39, 39, 1406, 258, self.on_menu_formulario_usuarioN_cerrar_clicked, True)
        
        regex = QRegExp(f"[{self.allowed_characters_numeric}]*")
        validator = QRegExpValidator(regex)
        self.menu_formulario_usuarioN_entry_cedula.setValidator(validator)
        
        regex = QRegExp(f"[{self.allowed_characters_alpha}]*")
        validator = QRegExpValidator(regex)
        self.menu_formulario_usuarioN_entry_nombre.setValidator(validator)
        
        # Crear instancia del hilo del lector RFID
        self.rfid_thread = RFIDThread()
        self.rfid_thread.data_read.connect(self.on_menu_formulario_usuarioN_rfid_data_received)
        self.rfid_thread.start()
        
    def init_menu_confirmar_usuarioN(self, cedula, nombre, area, tarjeta):
        self.set_background_images(self.menu_confirmar_usuarioN, "Desarrollo/Assets/menuConfirmarUsuarioN/fondo_1.png", "Desarrollo/Assets/menuConfirmarUsuarioN/fondo_2.png")
    
        self.setWindowTitle("Confirmar Usuario Nuevo")
        self.clock_widget.setParent(self.menu_confirmar_usuarioN)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        boton_cerrar = self.create_image_button(self.menu_confirmar_usuarioN, "Desarrollo/Assets/Commons/x.png", 39, 39, 1406, 258, self.on_menu_confirmar_usuarioN_cerrar_clicked, True)
        
        label_tarjeta=self.create_label(self.menu_confirmar_usuarioN, tarjeta, 1009, 372, 434, 40, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
        label_cedula=self.create_label(self.menu_confirmar_usuarioN, cedula, 1009, 439, 434, 40, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
        label_nombre=self.create_label(self.menu_confirmar_usuarioN, nombre, 1009, 506, 520, 60, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
        label_rol=self.create_label(self.menu_confirmar_usuarioN, area, 1009, 573, 350, 40, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
        
        self.menu_confirmar_usuarioN_boton_editar = self.create_text_button(self.menu_confirmar_usuarioN, "Editar", 791, 732, 105, 40, self.tamañoFuentePrincipal, self.colorFuente, self.tipografia, self.on_menu_confirmar_usuarioN_editar_clicked, True)
        self.menu_confirmar_usuarioN_boton_aceptar = self.create_image_button(self.menu_confirmar_usuarioN, "Desarrollo/Assets/Commons/boton_aceptar.png", 201, 60, 928, 722, self.on_menu_confirmar_usuarioN_aceptar_clicked, True)
        
        self.menu_confirmar_usuario_cedula=cedula
        self.menu_confirmar_usuario_nombre=nombre
        self.menu_confirmar_usuario_area=area
        self.menu_confirmar_usuario_tarjeta=tarjeta
        
    def init_menu_lista_usuarios(self):
        self.set_background_image(self.menu_lista_usuarios, "Desarrollo/Assets/menuListaUsuarios/fondo.png")
        
        self.setWindowTitle("Menu lista de Usuarios")
        self.clock_widget.setParent(self.menu_lista_usuarios)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        # Crear entry y drop down menu
        self.menu_lista_usuarios_entry_filtro = self.create_entry(self.menu_lista_usuarios, 725, 269, 210, 39)
        self.menu_lista_usuarios_entry_filtro.setStyleSheet("font-size: 14px; font-family: Poppins; color: #727272; border-radius: 10px;")
        self.menu_lista_usuarios_dropdown_menu = self.create_dropdown_menu(self.menu_lista_usuarios, 984, 269, 210, 39, ["Seleccionar", "Nombre", "Cedula"])
        
        # Añadir botones
        boton_cerrar = self.create_image_button(self.menu_lista_usuarios, "Desarrollo/Assets/Commons/x.png", 39, 39, 1652, 185, self.on_menu_lista_usuarios_cerrar_clicked, True)
        boton_editar = self.create_image_button(self.menu_lista_usuarios, "Desarrollo/Assets/Commons/boton_editar.png", 191, 44, 740, 946, self.on_menu_lista_usuarios_editar_clicked, True)
        boton_eliminar = self.create_image_button(self.menu_lista_usuarios, "Desarrollo/Assets/Commons/boton_eliminar.png", 191, 44, 989, 946, self.on_menu_lista_usuarios_eliminar_clicked, True)
        
        self.menu_lista_usuarios_tabla = QTableWidget(self.menu_lista_usuarios)
        self.menu_lista_usuarios_tabla.setGeometry(195, 333, 1530, 578)
        self.menu_lista_usuarios_tabla.setColumnCount(4)
        self.menu_lista_usuarios_tabla.setHorizontalHeaderLabels(["Usuarios", "Cédula", "Rol", "Selec."])
        
        # Configurar el encabezado de la tabla
        header = self.menu_lista_usuarios_tabla.horizontalHeader()
        header.setFont(QFont(self.tipografia, 20, QFont.Bold))
        header.setStyleSheet("background-color: #D9D9D9; color: #727272;")
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.menu_lista_usuarios_tabla.setColumnWidth(0, 558)
        self.menu_lista_usuarios_tabla.setColumnWidth(1, 492)
        self.menu_lista_usuarios_tabla.setColumnWidth(2, 290)
        self.menu_lista_usuarios_tabla.setColumnWidth(3, 173)
        
        # Configurar el contenido de la tabla
        self.menu_lista_usuarios_tabla.setFont(QFont(self.tipografia, 14))
        self.menu_lista_usuarios_tabla.setStyleSheet("background-color: #ECECEC; color: #727272;")
        
        # Desactivar la columna de índices
        self.menu_lista_usuarios_tabla.verticalHeader().setVisible(False)
        
        # Conectar los eventos
        self.menu_lista_usuarios_entry_filtro.textChanged.connect(self.filtrar_tabla_usuarios)
        self.menu_lista_usuarios_dropdown_menu.currentIndexChanged.connect(self.filtrar_tabla_usuarios)
        
        self.cargar_datos_usuarios()
        
    def init_menu_editar_usuarios(self, cedula):
        self.set_background_image(self.menu_editar_usuario, "Desarrollo/Assets/menuFormularioUsuarioNOp/fondo.png")
        
        self.setWindowTitle("Menu Editar Usuarios")
        self.clock_widget.setParent(self.menu_editar_usuario)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        self.label_errores=QLabel("", self)
        self.label_errores.setStyleSheet(f"font-size: {self.tamañoFuenteSecundario}px; color: {self.colorError}; font-family: {self.tipografia}")
        self.label_errores.setParent(self.menu_editar_usuario)
        
        self.menu_editar_usuario_cedula_selected=cedula
        
        # Consultar la base de datos para obtener el nombre y el rol del usuario con la cédula proporcionada
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        cursor.execute("SELECT nombre, area, id_tarjeta FROM usuarios WHERE cedula = ?", (cedula,))
        user_data = cursor.fetchone()  # Obtenemos una tupla (nombre, rol) o None si no se encuentra la cédula
        connection.close()
        
        self.menu_editar_usuario_entry_tarjeta = self.create_entry(self.menu_editar_usuario, 957, 380, 434, 52)
        self.menu_editar_usuario_entry_tarjeta.setReadOnly(True)
        self.menu_editar_usuario_entry_cedula = self.create_entry(self.menu_editar_usuario, 957, 461, 434, 52)
        self.menu_editar_usuario_entry_nombre = self.create_entry(self.menu_editar_usuario, 957, 543, 434, 52)
        
        self.menu_editar_usuario_rol_drop = self.create_dropdown_menu(self.menu_editar_usuario, 957, 625, 434, 52, self.areas)
        
        nombre, area, id_tarjeta = user_data

        # Asignar los valores obtenidos a los widgets correspondientes
        self.menu_editar_usuario_entry_tarjeta.setText(id_tarjeta)
        self.menu_editar_usuario_entry_cedula.setText(cedula)
        self.menu_editar_usuario_entry_nombre.setText(nombre)

        # Seleccionar el rol en el QComboBox
        if area in self.areas:
            index = self.areas.index(area)
            self.menu_editar_usuario_rol_drop.setCurrentIndex(index)
        
        boton_cancelar = self.create_text_button(self.menu_editar_usuario, "Cerrar", 762, 727, 168, 40, self.tamañoFuentePrincipal, self.colorFuente, self.tipografia, self.on_menu_editar_usuario_cancelar_clicked, True)
        boton_aceptar = self.create_image_button(self.menu_editar_usuario, "Desarrollo/Assets/Commons/boton_siguiente.png", 201, 60, 957, 717, self.on_menu_editar_usuario_aceptar_clicked, True)
        boton_cerrar = self.create_image_button(self.menu_editar_usuario, "Desarrollo/Assets/Commons/x.png", 39, 39, 1406, 258, self.on_menu_editar_usuario_cerrar_clicked, True)
        
        regex = QRegExp(f"[{self.allowed_characters_numeric}]*")
        validator = QRegExpValidator(regex)
        self.menu_editar_usuario_entry_cedula.setValidator(validator)
        
        regex = QRegExp(f"[{self.allowed_characters_alpha}]*")
        validator = QRegExpValidator(regex)
        self.menu_editar_usuario_entry_nombre.setValidator(validator)
        
        # Crear instancia del hilo del lector RFID
        self.rfid_thread = RFIDThread()
        self.rfid_thread.data_read.connect(self.on_menu_formulario_usuarioE_rfid_data_received)
        self.rfid_thread.start()
        
    def init_menu_confirmar_usuarioE(self, cedula_selected, cedula, nombre, area, tarjeta):
        self.set_background_images(self.menu_confirmar_usuarioE, "Desarrollo/Assets/menuConfirmarUsuarioN/fondo_1.png", "Desarrollo/Assets/menuConfirmarUsuarioN/fondo_2.png")
        
        self.setWindowTitle("Confirmar Usuario Editado")
        self.clock_widget.setParent(self.menu_confirmar_usuarioE)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        self.menu_confirmar_usuarioE_cedula_selected=cedula_selected
        self.menu_confirmar_usuarioE_cedula=cedula
        self.menu_confirmar_usuarioE_nombre=nombre
        self.menu_confirmar_usuarioE_area=area
        self.menu_confirmar_usuarioE_tarjeta=tarjeta
        
        boton_cerrar = self.create_image_button(self.menu_confirmar_usuarioE, "Desarrollo/Assets/Commons/x.png", 39, 39, 1406, 258, self.on_menu_confirmar_usuarioE_cerrar_clicked, True)
        
        label_tarjeta=self.create_label(self.menu_confirmar_usuarioN, tarjeta, 1009, 372, 434, 40, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
        label_cedula=self.create_label(self.menu_confirmar_usuarioE, cedula, 1009, 439, 400, 40, self.tamañoFuenteSecundario, self.colorFuente ,self.tipografia, False)
        label_nombre=self.create_label(self.menu_confirmar_usuarioE, nombre, 1009, 506, 300, 60, self.tamañoFuenteSecundario, self.colorFuente ,self.tipografia, False)
        label_rol=self.create_label(self.menu_confirmar_usuarioE, area, 1009, 573, 350, 40, self.tamañoFuenteSecundario, self.colorFuente ,self.tipografia, False)
        
        self.menu_confirmar_usuarioE_boton_editar = self.create_text_button(self.menu_confirmar_usuarioE, "Editar", 791, 732, 120, 40, self.tamañoFuentePrincipal, self.colorFuente, self.tipografia, self.on_menu_confirmar_usuarioE_editar_clicked, True)
        self.menu_confirmar_usuarioE_boton_aceptar = self.create_image_button(self.menu_confirmar_usuarioE, "Desarrollo/Assets/Commons/boton_aceptar.png", 201, 60, 928, 722, self.on_menu_confirmar_usuarioE_aceptar_clicked, True)
        
    def init_menu_pedidos(self):
        self.set_background_image(self.menu_pedidos, "Desarrollo/Assets/menuPedidos/fondo.png")
        
        self.setWindowTitle("Menu Pedidos")
        self.clock_widget.setParent(self.menu_pedidos)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.show()
        
        boton_crear = self.create_hover_image_button(self.menu_pedidos, "Desarrollo/Assets/menuPedidos/boton_crear_pedido_1.png", "Desarrollo/Assets/menuPedidos/boton_crear_pedido_2.png", 500, 355, 429, 397, self.on_menu_pedidos_agregar_clicked, True)
        boton_editar = self.create_hover_image_button(self.menu_pedidos, "Desarrollo/Assets/menuPedidos/boton_editar_pedido_1.png", "Desarrollo/Assets/menuPedidos/boton_editar_pedido_2.png", 500, 355, 992, 397, self.on_menu_pedidos_editar_clicked, True)
        
        boton_atras = self.create_image_button(self.menu_pedidos, "Desarrollo/Assets/Commons/boton_atras.png", 143, 63, 1670, 908, self.on_menu_pedidos_atras_clicked, True)
        
    def init_menu_crear_pedido(self, numero_desayuno=0, numero_almuerzo=0, numero_cena=0, numero_jugo=0, numero_porron=0, refrigerio_descripcion="", refrigerio_cantidad=0, refrigerio_precio=0): 
        self.set_background_images(self.menu_crear_pedido, "Desarrollo/Assets/menuCrearPedido/fondo_1.png", "Desarrollo/Assets/menuCrearPedido/fondo_2.png")
        
        self.setWindowTitle("Menu Crear Pedido")
        self.clock_widget.setParent(self.menu_crear_pedido)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        self.menu_crear_pedido_boton_cancelar = self.create_text_button(self.menu_crear_pedido, "Cerrar", 757, 722, 168, 40, self.tamañoFuentePrincipal, self.colorFuente, self.tipografia, self.on_menu_crear_pedido_cancelar_clicked, True)
        self.menu_crear_pedido_boton_aceptar = self.create_image_button(self.menu_crear_pedido, "Desarrollo/Assets/Commons/boton_aceptar.png", 201, 60, 952, 712, self.on_menu_crear_pedido_aceptar_clicked, True)
        self.menu_crear_pedido_boton_cerrar = self.create_image_button(self.menu_crear_pedido, "Desarrollo/Assets/Commons/x.png", 39, 39, 1401, 258, self.on_menu_crear_pedido_cerrar_clicked, True)
        
        self.menu_crear_pedido_numero_desayuno=numero_desayuno
        self.menu_crear_pedido_numero_almuerzo=numero_almuerzo
        self.menu_crear_pedido_numero_cena=numero_cena
        self.menu_crear_pedido_numero_jugo=numero_jugo
        self.menu_crear_pedido_numero_porron=numero_porron
        
        self.menu_crear_pedido_entry_desayuno = self.create_entry(self.menu_crear_pedido, 813, 443, 60, 40)
        self.menu_crear_pedido_entry_almuerzo = self.create_entry(self.menu_crear_pedido, 813, 519, 60, 40)
        self.menu_crear_pedido_entry_cena = self.create_entry(self.menu_crear_pedido, 813, 599, 60, 40)
        self.menu_crear_pedido_entry_jugo = self.create_entry(self.menu_crear_pedido, 1257, 443, 60, 40)
        self.menu_crear_pedido_entry_porron = self.create_entry(self.menu_crear_pedido, 1257, 519, 60, 40)
        
        self.menu_crear_pedido_entry_desayuno.setAlignment(Qt.AlignCenter)
        self.menu_crear_pedido_entry_almuerzo.setAlignment(Qt.AlignCenter)
        self.menu_crear_pedido_entry_cena.setAlignment(Qt.AlignCenter)
        self.menu_crear_pedido_entry_jugo.setAlignment(Qt.AlignCenter)
        self.menu_crear_pedido_entry_porron.setAlignment(Qt.AlignCenter)
        
        self.menu_crear_pedido_entry_desayuno.setStyleSheet("font-size: 36px; font-family: Poppins; color: {}; border-radius: 10px;".format(self.colorFuente2))
        self.menu_crear_pedido_entry_almuerzo.setStyleSheet("font-size: 36px; font-family: Poppins; color: {}; border-radius: 10px;".format(self.colorFuente2))
        self.menu_crear_pedido_entry_cena.setStyleSheet("font-size: 36px; font-family: Poppins; color: {}; border-radius: 10px;".format(self.colorFuente2))
        self.menu_crear_pedido_entry_jugo.setStyleSheet("font-size: 36px; font-family: Poppins; color: {}; border-radius: 10px;".format(self.colorFuente2))
        self.menu_crear_pedido_entry_porron.setStyleSheet("font-size: 36px; font-family: Poppins; color: {}; border-radius: 10px;".format(self.colorFuente2))
        
        self.menu_crear_pedido_entry_desayuno.setText(str(self.menu_crear_pedido_numero_desayuno))
        self.menu_crear_pedido_entry_almuerzo.setText(str(self.menu_crear_pedido_numero_almuerzo))
        self.menu_crear_pedido_entry_cena.setText(str(self.menu_crear_pedido_numero_cena))
        self.menu_crear_pedido_entry_jugo.setText(str(self.menu_crear_pedido_numero_jugo))
        self.menu_crear_pedido_entry_porron.setText(str(self.menu_crear_pedido_numero_porron))
        
        self.menu_crear_pedido_entry_desayuno.setMaxLength(2)
        self.menu_crear_pedido_entry_almuerzo.setMaxLength(2)
        self.menu_crear_pedido_entry_cena.setMaxLength(2)
        self.menu_crear_pedido_entry_jugo.setMaxLength(2)
        self.menu_crear_pedido_entry_porron.setMaxLength(2)
        
        regex = QRegExp(f"[{self.allowed_characters_numeric}]*")
        validator = QRegExpValidator(regex)
        
        self.menu_crear_pedido_entry_desayuno.setValidator(validator)
        self.menu_crear_pedido_entry_almuerzo.setValidator(validator)
        self.menu_crear_pedido_entry_cena.setValidator(validator)
        self.menu_crear_pedido_entry_jugo.setValidator(validator)
        self.menu_crear_pedido_entry_porron.setValidator(validator)
        
        self.menu_crear_pedido_refrigerio_descripcion=refrigerio_descripcion
        self.menu_crear_pedido_refrigerio_cantidad=refrigerio_cantidad
        self.menu_crear_pedido_refrigerio_precio=refrigerio_precio
        
        self.menu_crear_pedido_boton_refrigerio = self.create_image_button(self.menu_crear_pedido, "Desarrollo/Assets/menuCrearPedido/boton_crear.png", 131, 42, 1216, 601, self.on_menu_crear_pedido_refrigerio_clicked, True)
        
        self.menu_crear_pedido_entry_refrigerio_descripcion = self.create_entry(self.menu_crear_pedido, 0, 0, 0, 0)
        self.menu_crear_pedido_entry_refrigerio_cantidad = self.create_entry(self.menu_crear_pedido, 0, 0, 0, 0)
        
        self.menu_crear_pedido_entry_refrigerio_descripcion.setText(self.menu_crear_pedido_refrigerio_descripcion)
        self.menu_crear_pedido_entry_refrigerio_cantidad.setText(str(self.menu_crear_pedido_refrigerio_cantidad))
        
        self.menu_crear_pedido_entry_refrigerio_cantidad.setValidator(validator)
        
        regex = QRegExp(f"[{self.allowed_characters_alpha}]*")
        validator = QRegExpValidator(regex)
        
        self.menu_crear_pedido_entry_refrigerio_descripcion.setValidator(validator)
        
    def init_menu_confirmar_pedido(self, numero_desayuno, numero_almuerzo, numero_cena, numero_jugo, numero_porron, descripcion_refrigerio, cantidad_refrigerio, precio_refrigerio):
        self.set_background_images(self.menu_confirmar_pedido, "Desarrollo/Assets/menuConfirmarPedido/fondo_1.png", "Desarrollo/Assets/menuConfirmarPedido/fondo_2.png")
        
        self.label_errores=QLabel("", self)
        self.label_errores.setStyleSheet(f"font-size: {self.tamañoFuenteSecundario}px; color: {self.colorError}; font-family: {self.tipografia}")
        self.label_errores.setParent(self.menu_confirmar_pedido)
        
        self.setWindowTitle("Menu Confirmar Pedido")
        self.clock_widget.setParent(self.menu_confirmar_pedido)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.show()
        
        self.menu_confirmar_pedido_precio_refrigerio=precio_refrigerio
        self.menu_confirmar_pedido_descripcion_refrigerio=descripcion_refrigerio
        
        boton_cerrar = self.create_image_button(self.menu_confirmar_pedido, "Desarrollo/Assets/Commons/x.png", 39, 39, 1401, 198, self.on_menu_confirmar_pedido_cerrar_clicked, True)
        
        self.menu_confirmar_pedido_boton_editar = self.create_text_button(self.menu_confirmar_pedido, "Editar", 778, 807, 120, 40, self.tamañoFuentePrincipal, self.colorFuente, self.tipografia, self.on_menu_confirmar_pedido_editar_clicked, True)
        self.menu_confirmar_pedido_boton_aceptar = self.create_image_button(self.menu_confirmar_pedido, "Desarrollo/Assets/Commons/boton_aceptar.png", 201, 60, 941, 797, self.on_menu_confirmar_pedido_aceptar_clicked, True)
        
        self.menu_confirmar_pedido_drop_area = self.create_dropdown_menu(self.menu_confirmar_pedido, 865, 643, 383, 50, self.areas)
        self.menu_confirmar_pedido_entry_soporte = self.create_entry(self.menu_confirmar_pedido, 865, 710, 383, 50)
        
        regex = QRegExp(f"[{self.allowed_characters_alpha}]*")
        validator = QRegExpValidator(regex)
        
        
        self.lista_servicios=["Desayuno", "Almuerzo", "Cena", "Jugo", "Porron", "Refrigerio"]
        self.cantidades=[numero_desayuno, numero_almuerzo, numero_cena, numero_jugo, numero_porron, cantidad_refrigerio]
        acumulador=0
        
        for i in range(len(self.lista_servicios)):
            if (self.cantidades[i]!=0):
                self.create_label(self.menu_confirmar_pedido, self.lista_servicios[i], 818, 340+acumulador, 200, 48, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
                self.create_label(self.menu_confirmar_pedido, str(self.cantidades[i]), 1069, 340+acumulador, 45, 48, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
                acumulador+=50
    
    ###
    
    def init_menu_lista_pedidos(self):
        self.set_background_image(self.menu_lista_pedidos, "Desarrollo/Assets/menuListaPedidos/fondo.png")
        
        self.setWindowTitle("Menu lista de Pedidos")
        self.clock_widget.setParent(self.menu_lista_pedidos)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        # Crear entry y drop down menu
        self.menu_lista_pedidos_entry_filtro = self.create_entry(self.menu_lista_pedidos, 725, 269, 210, 39)
        self.menu_lista_pedidos_entry_filtro.setStyleSheet("font-size: 14px; font-family: Poppins; color: #727272; border-radius: 10px;")
        self.menu_lista_pedidos_dropdown_menu = self.create_dropdown_menu(self.menu_lista_pedidos, 984, 269, 210, 39, ["Seleccionar", "Tipo", "Área"])
        
        # Añadir botones
        boton_cerrar = self.create_image_button(self.menu_lista_pedidos, "Desarrollo/Assets/Commons/x.png", 39, 39, 1652, 185, self.on_menu_lista_pedidos_cerrar_clicked, True)
        boton_crear = self.create_image_button(self.menu_lista_pedidos, "Desarrollo/Assets/Commons/boton_crear.png", 191, 44, 616, 946, self.on_menu_lista_pedidos_crear_clicked, True)
        boton_aprobar = self.create_image_button(self.menu_lista_pedidos, "Desarrollo/Assets/Commons/boton_aprobar.png", 191, 44, 865, 946, self.on_menu_lista_pedidos_aprobar_clicked, True)
        boton_eliminar = self.create_image_button(self.menu_lista_pedidos, "Desarrollo/Assets/Commons/boton_eliminar.png", 191, 44, 1114, 946, self.on_menu_lista_pedidos_eliminar_clicked, True)
        
        self.menu_lista_pedidos_tabla = QTableWidget(self.menu_lista_pedidos)
        self.menu_lista_pedidos_tabla.setGeometry(195, 333, 1530, 578)
        self.menu_lista_pedidos_tabla.setColumnCount(7)
        self.menu_lista_pedidos_tabla.setHorizontalHeaderLabels(["Fecha", "Hora", "Tipo", "Cantidad", "Área", "Estado", "Selec."])
        
        # Configurar el encabezado de la tabla
        header = self.menu_lista_pedidos_tabla.horizontalHeader()
        header.setFont(QFont(self.tipografia, 20, QFont.Bold))
        header.setStyleSheet("background-color: #D9D9D9; color: #727272;")
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.menu_lista_pedidos_tabla.setColumnWidth(0, 279)
        self.menu_lista_pedidos_tabla.setColumnWidth(1, 191)
        self.menu_lista_pedidos_tabla.setColumnWidth(2, 324)
        self.menu_lista_pedidos_tabla.setColumnWidth(3, 187)
        self.menu_lista_pedidos_tabla.setColumnWidth(4, 263)
        self.menu_lista_pedidos_tabla.setColumnWidth(5, 165)
        self.menu_lista_pedidos_tabla.setColumnWidth(6, 101)
        
        # Configurar el contenido de la tabla
        self.menu_lista_pedidos_tabla.setFont(QFont(self.tipografia, 14))
        self.menu_lista_pedidos_tabla.setStyleSheet("background-color: #ECECEC; color: #727272;")
        
        # Desactivar la columna de índices
        self.menu_lista_pedidos_tabla.verticalHeader().setVisible(False)
        
        # Conectar los eventos
        self.menu_lista_pedidos_entry_filtro.textChanged.connect(self.filtrar_tabla_pedidos)
        self.menu_lista_pedidos_dropdown_menu.currentIndexChanged.connect(self.filtrar_tabla_pedidos)
        
        self.cargar_datos_pedidos()
        
    def init_menu_aprobar_pedidos(self, lista_pedidos):
        self.set_background_image(self.menu_aprobar_pedidos, "Desarrollo/Assets/menuAprobarPedidos/fondo.png")
        
        self.setWindowTitle("Aprobar Pedidos")
        self.clock_widget.setParent(self.menu_aprobar_pedidos)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        boton_cerrar = self.create_image_button(self.menu_aprobar_pedidos, "Desarrollo/Assets/Commons/x.png", 39, 39, 1500, 185, self.on_menu_aprobar_pedidos_cerrar_clicked, True)
        
        self.menu_aprobar_pedidos_label = self.create_label(self.menu_aprobar_pedidos, "Coloque la tarjeta sobre el lector", 621, 807, 652, 54, 36, self.colorFuenteReloj1, self.tipografia, False)
        self.menu_aprobar_pedidos_label.show()
        self.menu_aprobar_pedidos_label.setAlignment(Qt.AlignCenter)
        
        # Inicializar las listas
        self.lista_id_pedido = []
        lista_tabla_pedidos = []

        # Conectar a la base de datos
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        for pedido in lista_pedidos:
            fecha, hora, tipo = pedido

            # Recuperar los campos de la base de datos para este pedido
            cursor.execute('SELECT id_pedido, cantidad, area FROM pedidos WHERE fecha=? AND hora=? AND tipo=?', (fecha, hora, tipo))
            resultado = cursor.fetchone()

            if resultado:
                id_pedido, cantidad, area = resultado

                # Agregar el id_pedido a la lista de ids
                self.lista_id_pedido.append(id_pedido)

                # Agregar los datos a la lista_tabla_pedidos
                lista_tabla_pedidos.append([fecha, tipo, cantidad, area])

        # Cerrar la conexión a la base de datos
        conn.close()
        
        menu_aprobar_pedidos_tabla = QTableWidget(self.menu_aprobar_pedidos)
        menu_aprobar_pedidos_tabla.setGeometry(489, 359, 943, 372)
        menu_aprobar_pedidos_tabla.setColumnCount(4)
        menu_aprobar_pedidos_tabla.setHorizontalHeaderLabels(["Fecha", "Tipo", "Cantidad", "Área"])
        
        # Configurar el encabezado de la tabla
        header = menu_aprobar_pedidos_tabla.horizontalHeader()
        header.setFont(QFont(self.tipografia, 20, QFont.Bold))
        header.setStyleSheet("background-color: #D9D9D9; color: #727272;")
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        menu_aprobar_pedidos_tabla.setColumnWidth(0, 191)
        menu_aprobar_pedidos_tabla.setColumnWidth(1, 316)
        menu_aprobar_pedidos_tabla.setColumnWidth(2, 187)
        menu_aprobar_pedidos_tabla.setColumnWidth(3, 244)
        
        # Configurar el contenido de la tabla
        menu_aprobar_pedidos_tabla.setFont(QFont(self.tipografia, 14))
        menu_aprobar_pedidos_tabla.setStyleSheet("background-color: #ECECEC; color: #727272;")
        
        # Desactivar la columna de índices
        menu_aprobar_pedidos_tabla.verticalHeader().setVisible(False)
        
        # Configurar el número de filas de la tabla
        menu_aprobar_pedidos_tabla.setRowCount(len(lista_tabla_pedidos))
        
        # Llenar la tabla con los datos de lista_tabla_pedidos
        for row_index, pedido in enumerate(lista_tabla_pedidos):
            for col_index, value in enumerate(pedido):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignLeft)
                menu_aprobar_pedidos_tabla.setItem(row_index, col_index, item)
        
        menu_aprobar_pedidos_tabla.show()
        
        # Crear instancia del hilo del lector RFID
        self.rfid_thread = RFIDThread()
        self.rfid_thread.data_read.connect(self.on_menu_aprobar_pedidos_rfid_data_received)
        self.rfid_thread.start()
        
    def init_menu_registros(self):
        self.set_background_image(self.menu_registros, "Desarrollo/Assets/menuRegistros/fondo.png")
        
        self.setWindowTitle("Menu Registros")
        self.clock_widget.setParent(self.menu_registros)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj1}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        boton_atras = self.create_image_button(self.menu_registros, "Desarrollo/Assets/Commons/boton_atras.png", 143, 63, 1670, 908, self.on_menu_registros_atras_clicked, True)
        boton_manual = self.create_hover_image_button(self.menu_registros, "Desarrollo/Assets/menuRegistros/boton_manual1.png", "Desarrollo/Assets/menuRegistros/boton_manual2.png", 686, 96, 617, 765, self.on_menu_registros_manual_clicked, True)
        
        
        # Crear el label
        self.menu_registros_label_servicio = self.create_label(self.menu_registros, "", 371, 146, 1260, 180, 120, self.colorFuente2, self.tipografia, True)
        self.menu_registros_label_servicio.show()
        self.menu_registros_label_servicio.setAlignment(Qt.AlignCenter)

        # Actualizar el servicio actual al iniciar
        self.update_service_label2()
        
        # Crear un timer para actualizar el servicio cada minuto
        self.timer_servicio2 = QTimer(self)
        self.timer_servicio2.timeout.connect(self.update_service_label2)
        self.timer_servicio2.start(60000)  # Actualizar cada 60 segundos
        
        # Crear instancia del hilo del lector RFID
        self.rfid_thread = RFIDThread()
        self.rfid_thread.data_read.connect(self.on_menu_registros_rfid_data_received)
        self.rfid_thread.start()
        
    def init_menu_registro_manual(self):
        self.set_background_image(self.menu_registro_manual, "Desarrollo/Assets/menuRegistroManual/fondo.png")
        
        self.setWindowTitle("Menu Registro Manual")
        self.clock_widget.setParent(self.menu_registro_manual)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        boton_existente = self.create_hover_image_button(self.menu_registro_manual, "Desarrollo/Assets/menuRegistroManual/boton_existente_1.png", "Desarrollo/Assets/menuRegistroManual/boton_existente_2.png", 349, 298, 572, 391, self.on_menu_registro_manual_existente_clicked, True)
        boton_nuevo = self.create_hover_image_button(self.menu_registro_manual, "Desarrollo/Assets/menuRegistroManual/boton_nuevo_1.png", "Desarrollo/Assets/menuRegistroManual/boton_nuevo_2.png", 349, 298, 998, 391, self.on_menu_registro_manual_nuevo_clicked, True)
        
        boton_cerrar = self.create_image_button(self.menu_registro_manual, "Desarrollo/Assets/Commons/x.png", 39, 39, 1401, 316, self.on_menu_registro_manual_cerrar_clicked, True)
        
    def init_menu_registro_existente(self, cedula=""):
        self.set_background_image(self.menu_registro_manualE, "Desarrollo/Assets/menuRegistroExistente/fondo.png")
        
        self.setWindowTitle("Registro Usuario Existente")
        self.clock_widget.setParent(self.menu_registro_manualE)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        self.label_errores=QLabel("", self)
        self.label_errores.setStyleSheet(f"font-size: {self.tamañoFuenteSecundario}px; color: {self.colorError}; font-family: {self.tipografia}")
        self.label_errores.setParent(self.menu_registro_manualE)
        
        self.menu_registro_existente_entry_cedula = self.create_entry(self.menu_registro_manualE, 730, 529, 462, 52, cedula)
        self.menu_registro_existente_entry_cedula.setAlignment(Qt.AlignCenter)
        
        regex = QRegExp(f"[{self.allowed_characters_numeric}]*")
        validator = QRegExpValidator(regex)
        self.menu_registro_existente_entry_cedula.setValidator(validator)
       
        boton_cancelar = self.create_text_button(self.menu_registro_manualE, "Cancelar", 762, 652, 168, 40, self.tamañoFuentePrincipal, self.colorFuente, self.tipografia, self.on_menu_registro_existente_cancelar_clicked, True)
        boton_siguiente = self.create_image_button(self.menu_registro_manualE, "Desarrollo/Assets/Commons/boton_siguiente.png", 201, 60, 957, 642, self.on_menu_registro_existente_siguiente_clicked, True)
        boton_cerrar = self.create_image_button(self.menu_registro_manualE, "Desarrollo/Assets/Commons/x.png", 39, 39, 1406, 346, self.on_menu_registro_existente_cerrar_clicked, True)
        
    def init_menu_registro_nuevo(self, cedula="", nombre="", rol="Visitante"):
        self.set_background_image(self.menu_registro_manualN, "Desarrollo/Assets/menuFormularioUsuarioN/fondo.png")
        
        self.setWindowTitle("Registro Visitante")
        self.clock_widget.setParent(self.menu_registro_manualN)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        self.label_errores=QLabel("", self)
        self.label_errores.setStyleSheet(f"font-size: {self.tamañoFuenteSecundario}px; color: {self.colorError}; font-family: {self.tipografia}")
        self.label_errores.setParent(self.menu_registro_manualN)
        
        self.menu_formulario_usuarioN_entry_cedula = self.create_entry(self.menu_registro_manualN, 957, 447, 434, 52, cedula)
        self.menu_formulario_usuarioN_entry_nombre = self.create_entry(self.menu_registro_manualN, 957, 529, 434, 52, nombre)
        
        self.menu_formulario_usuarioN_rol_drop = self.create_dropdown_menu(self.menu_registro_manualN, 957, 611, 434, 52, self.areas)
        
        regex = QRegExp(f"[{self.allowed_characters_numeric}]*")
        validator = QRegExpValidator(regex)
        self.menu_formulario_usuarioN_entry_cedula.setValidator(validator)
        
        regex = QRegExp(f"[{self.allowed_characters_alpha}]*")
        validator = QRegExpValidator(regex)
        self.menu_formulario_usuarioN_entry_nombre.setValidator(validator)
        
        boton_cancelar = self.create_text_button(self.menu_registro_manualN, "Cancelar", 762, 727, 168, 40, self.tamañoFuentePrincipal, self.colorFuente, self.tipografia, self.on_menu_registro_nuevo_cancelar_clicked, True)
        boton_siguiente = self.create_image_button(self.menu_registro_manualN, "Desarrollo/Assets/Commons/boton_siguiente.png", 201, 60, 957, 717, self.on_menu_registro_nuevo_siguiente_clicked, True)
        boton_cerrar = self.create_image_button(self.menu_registro_manualN, "Desarrollo/Assets/Commons/x.png", 39, 39, 1406, 258, self.on_menu_registro_nuevo_cerrar_clicked, True)
        
    def init_menu_confirmar_registro_manual_nuevo(self, cedula, nombre, area, servicio):
        self.set_background_images(self.menu_confirmar_registro_manualN, "Desarrollo/Assets/menuConfirmarRegistroManual/fondo1.png", "Desarrollo/Assets/menuConfirmarRegistroManual/fondo2.png")
    
        self.setWindowTitle("Confirmar Registro Manual Usuario Nuevo")
        self.clock_widget.setParent(self.menu_confirmar_registro_manualN)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        boton_cerrar = self.create_image_button(self.menu_confirmar_registro_manualN, "Desarrollo/Assets/Commons/x.png", 39, 39, 1406, 258, self.on_menu_confirmar_registro_manualN_cerrar_clicked, True)
        
        label_cedula=self.create_label(self.menu_confirmar_registro_manualN, cedula, 1009, 391, 434, 40, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
        label_nombre=self.create_label(self.menu_confirmar_registro_manualN, nombre, 1009, 452, 520, 60, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
        label_rol=self.create_label(self.menu_confirmar_registro_manualN, area, 1009, 513, 350, 40, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
        label_servicio=self.create_label(self.menu_confirmar_registro_manualN, servicio, 1009, 574, 434, 40, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, True)
        
        
        self.menu_confirmar_registro_manualN_boton_editar = self.create_text_button(self.menu_confirmar_registro_manualN, "Editar", 791, 732, 105, 40, self.tamañoFuentePrincipal, self.colorFuente, self.tipografia, self.on_menu_confirmar_registro_manualN_editar_clicked, True)
        self.menu_confirmar_registro_manualN_boton_aceptar = self.create_image_button(self.menu_confirmar_registro_manualN, "Desarrollo/Assets/Commons/boton_aceptar.png", 201, 60, 928, 722, self.on_menu_confirmar_registro_manualN_aceptar_clicked, True)
        
        self.menu_confirmar_registro_manualN_cedula=cedula
        self.menu_confirmar_registro_manualN_nombre=nombre
        self.menu_confirmar_registro_manualN_rol=area
        self.menu_confirmar_registro_manualN_servicio=servicio
    
    def init_menu_confirmar_registro_manual_existente(self, cedula, nombre, rol, servicio):
        self.set_background_images(self.menu_confirmar_registro_manualE, "Desarrollo/Assets/menuConfirmarRegistroManual/fondo1.png", "Desarrollo/Assets/menuConfirmarRegistroManual/fondo2.png")
    
        self.setWindowTitle("Confirmar Registro Manual Usuario Existente")
        self.clock_widget.setParent(self.menu_confirmar_registro_manualE)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj2}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        boton_cerrar = self.create_image_button(self.menu_confirmar_registro_manualE, "Desarrollo/Assets/Commons/x.png", 39, 39, 1406, 258, self.on_menu_confirmar_registro_manualE_cerrar_clicked, True)
        
        label_cedula=self.create_label(self.menu_confirmar_registro_manualE, cedula, 1009, 391, 434, 40, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
        label_nombre=self.create_label(self.menu_confirmar_registro_manualE, nombre, 1009, 452, 520, 60, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
        label_rol=self.create_label(self.menu_confirmar_registro_manualE, rol, 1009, 513, 350, 40, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, False)
        label_servicio=self.create_label(self.menu_confirmar_registro_manualE, servicio, 1009, 574, 434, 40, self.tamañoFuentePrincipal, self.colorFuente ,self.tipografia, True)
        
        self.menu_confirmar_registro_manualE_boton_editar = self.create_text_button(self.menu_confirmar_registro_manualE, "Editar", 791, 732, 105, 40, self.tamañoFuentePrincipal, self.colorFuente, self.tipografia, self.on_menu_confirmar_registro_manualE_editar_clicked, True)
        self.menu_confirmar_registro_manualE_boton_aceptar = self.create_image_button(self.menu_confirmar_registro_manualE, "Desarrollo/Assets/Commons/boton_aceptar.png", 201, 60, 928, 722, self.on_menu_confirmar_registro_manualE_aceptar_clicked, True)
        
        self.menu_confirmar_registro_manualE_cedula=cedula
        self.menu_confirmar_registro_manualE_nombre=nombre
        self.menu_confirmar_registro_manualE_rol=rol
        self.menu_confirmar_registro_manualE_servicio=servicio
    
    def init_menu_confirmar_registro_tarjeta(self, cedula, nombre, rol, servicio):
        self.set_background_image(self.menu_registro_tarjeta, "Desarrollo/Assets/menuConfirmarRegistroTarjeta/fondo.png")
    
        self.setWindowTitle("Confirmar Registro Automatico")
        self.clock_widget.setParent(self.menu_registro_tarjeta)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj1}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        boton_cerrar = self.create_image_button(self.menu_registro_tarjeta, "Desarrollo/Assets/Commons/x_b.png", 39, 39, 1406, 344, self.on_menu_registro_tarjeta_cerrar_clicked, True)
        
        label_cedula=self.create_label(self.menu_registro_tarjeta, cedula, 989, 444, 434, 40, self.tamañoFuentePrincipal, self.colorFuenteReloj2 ,self.tipografia, False)
        label_nombre=self.create_label(self.menu_registro_tarjeta, nombre, 989, 513, 520, 60, self.tamañoFuentePrincipal, self.colorFuenteReloj2 ,self.tipografia, False)
        label_servicio=self.create_label(self.menu_registro_tarjeta, servicio, 989, 582, 350, 40, self.tamañoFuentePrincipal, self.colorFuenteReloj2 ,self.tipografia, True)
        
        self.menu_confirmar_usuario_cedula=cedula
        self.menu_confirmar_usuario_nombre=nombre
        self.menu_confirmar_usuario_rol=rol
        self.menu_confirmar_registro_manualE_servicio=servicio
        
    def init_menu_registro_tarjeta_invalida(self):
        self.set_background_image(self.menu_registro_tarjeta_invalida, "Desarrollo/Assets/menuTarjetaInvalida/fondo.png")
        
        self.setWindowTitle("Registro Tarjeta Invalida")
        self.clock_widget.setParent(self.menu_registro_tarjeta_invalida)  # Asegurarse de que el reloj esté en el menú principal
        self.clock_widget.setStyleSheet(f"font-size: {self.tamañoFuenteReloj}px; color: {self.colorFuenteReloj1}; font-family: {self.tipografia}")
        self.clock_widget.show()
        
        boton_atras = self.create_image_button(self.menu_registro_tarjeta_invalida, "Desarrollo/Assets/Commons/boton_atras.png", 143, 63, 1670, 908, self.on_menu_registro_tarjeta_invalida_atras_clicked, True)
        boton_manual = self.create_hover_image_button(self.menu_registro_tarjeta_invalida, "Desarrollo/Assets/menuRegistros/boton_manual1.png", "Desarrollo/Assets/menuRegistros/boton_manual2.png", 686, 96, 616, 715, self.on_menu_registro_tarjeta_invalida_manual_clicked, True)
        
        
    
        
###ACCIONES DE LOS BOTONES
        
    def on_menu_principal_usuarios_clicked(self): #check
        self.menu_usuarios = QWidget(self)
        self.init_menu_usuarios()
        self.setCentralWidget(self.menu_usuarios)
        self.timer_servicio.stop()
    
    def on_menu_principal_pedidos_clicked(self): #check
        self.menu_pedidos = QWidget(self)
        self.init_menu_pedidos()
        self.setCentralWidget(self.menu_pedidos)
        self.timer_servicio.stop()
        
    def on_menu_principal_registros_clicked(self): #check
        self.menu_registros = QWidget(self)
        self.init_menu_registros()
        self.setCentralWidget(self.menu_registros)
        self.timer_servicio.stop()
    
    def on_menu_usuarios_agregar_clicked(self): #check
        self.menu_formulario_usuarioN = QWidget(self)
        self.init_menu_formulario_usuarioN()
        self.setCentralWidget(self.menu_formulario_usuarioN)
        
    def on_menu_usuarios_editar_clicked(self): #check
        self.menu_lista_usuarios = QWidget(self)
        self.init_menu_lista_usuarios()
        self.setCentralWidget(self.menu_lista_usuarios)
        
    def on_menu_usuarios_atras_clicked(self): #check
        self.menu_principal = QWidget(self)
        self.init_menu_principal()
        self.setCentralWidget(self.menu_principal)
        
    def on_menu_formulario_usuarioN_aceptar_clicked(self): #check
        cedula = self.menu_formulario_usuarioN_entry_cedula.text()
        nombre = self.menu_formulario_usuarioN_entry_nombre.text()
        area = self.menu_formulario_usuarioN_rol_drop.currentText()
        tarjeta = self.menu_formulario_usuarioN_entry_tarjeta.text()
        
        # Verificar que la cédula no exista en la base de datos
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT flag_retirado FROM usuarios WHERE cedula = ?", (cedula,))
        result_cedula = cursor.fetchone()
        
        conn.close()
        
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE id_tarjeta = ? and flag_retirado = 0", (tarjeta,))
        result_tarjeta = cursor.fetchone()
        
        conn.close()
        
        if cedula == "":
            self.label_errores.setText("Por favor, complete todos los campos requeridos")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px; border: 2px solid #E10909;")
        elif not nombre:
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.label_errores.setText("Por favor, complete todos los campos requeridos")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_entry_nombre.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px; border: 2px solid #E10909;")
        elif area == "Seleccionar":
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.menu_formulario_usuarioN_entry_nombre.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.label_errores.setText("Por favor, seleccione un area para el usuario")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_rol_drop.setStyleSheet("border: 2px solid #E10909;")
        elif not tarjeta:
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.menu_formulario_usuarioN_entry_nombre.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.menu_formulario_usuarioN_rol_drop.setStyleSheet("")
            self.label_errores.setText("Por favor, ubique una tarjeta en el lector")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_entry_tarjeta.setStyleSheet("border: 2px solid #E10909;")
        elif result_cedula is not None and result_cedula[0]==False:
            self.menu_formulario_usuarioN_rol_drop.setStyleSheet("")
            self.menu_formulario_usuarioN_entry_nombre.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.menu_formulario_usuarioN_entry_tarjeta.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.label_errores.setText("Número de identificación ya existente")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px; border: 2px solid #E10909;")
        elif result_tarjeta[0] > 0:
            self.menu_formulario_usuarioN_rol_drop.setStyleSheet("")
            self.menu_formulario_usuarioN_entry_nombre.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.label_errores.setText("Ubique una tarjeta que no haya sido asignada")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_entry_tarjeta.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px; border: 2px solid #E10909;")
        else:
            # Proceder con la funcionalidad original si todas las verificaciones pasan
            self.join_rfid_thread()
            self.menu_confirmar_usuarioN = QWidget(self)
            self.init_menu_confirmar_usuarioN(cedula, nombre, area, tarjeta)
            self.setCentralWidget(self.menu_confirmar_usuarioN)
        
    def on_menu_formulario_usuarioN_cancelar_clicked(self): #check
        self.join_rfid_thread()
        self.menu_usuarios = QWidget(self)
        self.init_menu_usuarios()
        self.setCentralWidget(self.menu_usuarios)
        
    def on_menu_formulario_usuarioN_cerrar_clicked(self): #check
        self.join_rfid_thread()
        self.menu_principal = QWidget(self)
        self.init_menu_principal()
        self.setCentralWidget(self.menu_principal)
        
    def join_rfid_thread(self): #check
        # Detener el hilo del lector RFID antes de cerrar el formulario
#        if self.rfid_thread:
#            self.rfid_thread.terminate()
#            self.rfid_thread.wait()
#            self.rfid_thread = None
        if self.rfid_thread:
            if self.rfid_thread.isRunning():
                self.rfid_thread.quit()  # Solicita al hilo que finalice limpiamente
                if not self.rfid_thread.wait(1000):  # Espera hasta 3 segundos
                    print("Advertencia: El hilo RFID no se detuvo a tiempo.")
        self.rfid_thread = None  # Eliminar la referencia al hilo
        
    def on_menu_confirmar_usuarioN_aceptar_clicked(self): #check
        self.menu_confirmar_usuarioN_boton_editar.setParent(None)
        self.menu_confirmar_usuarioN_boton_aceptar.setParent(None)
        
        if self.menu_confirmar_usuario_area == 'Directo':
            rol = 'Directo'
        else:
            rol = 'Usuario'
        
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql_query = """
        INSERT INTO usuarios (cedula, nombre, area, id_tarjeta, rol, fecha_ultima_modificacion)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (self.menu_confirmar_usuario_cedula, self.menu_confirmar_usuario_nombre, self.menu_confirmar_usuario_area, self.menu_confirmar_usuario_tarjeta, rol, fecha_actual)
        try:
            cursor.execute(sql_query, values)
            connection.commit()

            #QMessageBox.information(self, "Éxito", "Usuario insertado correctamente.")
        except sqlite3.Error as e:
            #QMessageBox.critical(self, "Error", f"No se pudo insertar el usuario: {e}")
            pass
        finally:
            connection.close()
            
        self.background_label1.hide()  # Ocultar fondo_1.png para revelar fondo_2.png
        
    def on_menu_confirmar_usuarioN_editar_clicked(self):
        QMessageBox.information(self, "Editar", "Se presionó el botón de Editar")
        
    def on_menu_confirmar_usuarioN_cerrar_clicked(self): #check
        self.menu_usuarios = QWidget(self)
        self.init_menu_usuarios()
        self.setCentralWidget(self.menu_usuarios)
        
    def on_menu_lista_usuarios_cerrar_clicked(self): #check
        self.menu_usuarios = QWidget(self)
        self.init_menu_usuarios()
        self.setCentralWidget(self.menu_usuarios)
    
    def on_menu_lista_usuarios_editar_clicked(self): #check
        count_selected = 0
        for row in range(self.menu_lista_usuarios_tabla.rowCount()):
            checkbox = self.menu_lista_usuarios_tabla.cellWidget(row, 3).layout().itemAt(0).widget()
            if checkbox.isChecked():
                count_selected += 1
                cedula_selected = self.menu_lista_usuarios_tabla.item(row, 1).text()  # Obtener la cédula de la fila seleccionada
        
        if(count_selected==1):
            self.menu_editar_usuario = QWidget(self)
            self.init_menu_editar_usuarios(cedula_selected)
            self.setCentralWidget(self.menu_editar_usuario)
        else:
            pass

    def on_menu_lista_usuarios_eliminar_clicked(self): #check
        count_selected=0
        lista_cedulas=[]
        for row in range(self.menu_lista_usuarios_tabla.rowCount()):
            checkbox = self.menu_lista_usuarios_tabla.cellWidget(row, 3).layout().itemAt(0).widget()
            if checkbox.isChecked():
                count_selected += 1
                lista_cedulas.append(self.menu_lista_usuarios_tabla.item(row, 1).text())
                
        mensaje = "¿Seguro que desea eliminar " + str(count_selected) + " perfiles?"
        self.popup = PopupEliminarUsuarios(mensaje, lista_cedulas)
        self.popup.show()
        
    def on_menu_editar_usuario_aceptar_clicked(self): #check
        cedula = self.menu_editar_usuario_entry_cedula.text()
        nombre = self.menu_editar_usuario_entry_nombre.text()
        area = self.menu_editar_usuario_rol_drop.currentText()
        tarjeta = self.menu_editar_usuario_entry_tarjeta.text()
        cedula_selected= self.menu_editar_usuario_cedula_selected
        
        if cedula == "":
            self.label_errores.setText("Por favor, complete todos los campos requeridos")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px; border: 2px solid #E10909;")
        elif not nombre:
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.label_errores.setText("Por favor, complete todos los campos requeridos")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_entry_nombre.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px; border: 2px solid #E10909;")
        elif area == "Seleccionar":
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.menu_formulario_usuarioN_entry_nombre.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.label_errores.setText("Por favor, seleccione un area para el usuario")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_rol_drop.setStyleSheet("border: 2px solid #E10909;")
        elif not tarjeta:
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.menu_formulario_usuarioN_entry_nombre.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.menu_formulario_usuarioN_rol_drop.setStyleSheet("")
            self.label_errores.setText("Por favor, ubique una tarjeta en el lector")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_entry_tarjeta.setStyleSheet("border: 2px solid #E10909;")
        else:
            # Proceder con la funcionalidad original si todas las verificaciones pasan
            self.join_rfid_thread()
            self.menu_confirmar_usuarioE = QWidget(self)
            self.init_menu_confirmar_usuarioE(cedula_selected, cedula, nombre, area, tarjeta)
            self.setCentralWidget(self.menu_confirmar_usuarioE)
        
    def on_menu_editar_usuario_cancelar_clicked(self): #check
        self.join_rfid_thread()
        self.menu_lista_usuarios = QWidget(self)
        self.init_menu_lista_usuarios()
        self.setCentralWidget(self.menu_lista_usuarios)
        
    def on_menu_editar_usuario_cerrar_clicked(self): #check
        self.join_rfid_thread()
        self.menu_usuarios = QWidget(self)
        self.init_menu_usuarios()
        self.setCentralWidget(self.menu_usuarios)
        
    def on_menu_confirmar_usuarioE_aceptar_clicked(self): #check
        self.menu_confirmar_usuarioE_boton_editar.setParent(None)
        self.menu_confirmar_usuarioE_boton_aceptar.setParent(None)
        
        if self.menu_confirmar_usuarioE_area == 'Directo':
            rol = 'Directo'
        else:
            rol = 'Usuario'
        
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            if self.menu_confirmar_usuarioE_cedula_selected == self.menu_confirmar_usuarioE_cedula:
                # Si las cédulas son iguales, realizar el UPDATE
                sql_query = """
                UPDATE usuarios
                SET cedula = ?, nombre = ?, area = ?, id_tarjeta = ?, rol = ?, fecha_ultima_modificacion = ?
                WHERE cedula = ?
                """
                values = (self.menu_confirmar_usuarioE_cedula, self.menu_confirmar_usuarioE_nombre, self.menu_confirmar_usuarioE_area, self.menu_confirmar_usuarioE_tarjeta, rol, fecha_actual,self.menu_confirmar_usuarioE_cedula_selected)
                cursor.execute(sql_query, values)
            else:
                # Si las cédulas son diferentes, insertar un nuevo registro y actualizar el flag_retirado del registro anterior
                # Insertar un nuevo registro
                insert_query = """
                INSERT INTO usuarios (cedula = ?, nombre = ?, area = ?, id_tarjeta = ?, rol = ?, flag_retirado = ?, fecha_ultima_modificacion = ?)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                insert_values = (self.menu_confirmar_usuarioE_cedula, self.menu_confirmar_usuarioE_nombre, self.menu_confirmar_usuarioE_area, self.menu_confirmar_usuarioE_tarjeta, rol,False, fecha_actual)
                cursor.execute(insert_query, insert_values)

                # Actualizar el flag_retirado del registro anterior
                update_flag_query = """
                UPDATE usuarios
                SET flag_retirado = ?, fecha_ultima_modificacion = ?
                WHERE cedula = ?
                """
                update_flag_values = (True, fecha_actual,self.menu_confirmar_usuarioE_cedula_selected)
                cursor.execute(update_flag_query, update_flag_values)

            # Confirmar los cambios
            connection.commit()

        except sqlite3.Error as e:
            #print(f"An error occurred: {e}")
            connection.rollback()

        finally:
            # Cerrar la conexión
            cursor.close()
            connection.close()
            
        self.background_label1.hide()  # Ocultar fondo_1.png para revelar fondo_2.png
        
    def on_menu_confirmar_usuarioE_editar_clicked(self):
        QMessageBox.information(self, "Editar", "Se presionó el botón de Editar")
        
    def on_menu_confirmar_usuarioE_cerrar_clicked(self): #check
        self.menu_lista_usuarios = QWidget(self)
        self.init_menu_lista_usuarios()
        self.setCentralWidget(self.menu_lista_usuarios)
      
    def on_menu_pedidos_agregar_clicked(self): #check
        self.menu_crear_pedido = QWidget(self)
        self.init_menu_crear_pedido()
        self.setCentralWidget(self.menu_crear_pedido)
        
    def on_menu_pedidos_editar_clicked(self): #check
        self.menu_lista_pedidos = QWidget(self)
        self.init_menu_lista_pedidos()
        self.setCentralWidget(self.menu_lista_pedidos)
        
    def on_menu_pedidos_atras_clicked(self): #check
        self.menu_principal = QWidget(self)
        self.init_menu_principal()
        self.setCentralWidget(self.menu_principal)
        
    def on_menu_crear_pedido_aceptar_clicked(self): #check
        numero_desayuno = int(self.menu_crear_pedido_entry_desayuno.text()) if self.menu_crear_pedido_entry_desayuno.text() else 0
        numero_almuerzo = int(self.menu_crear_pedido_entry_almuerzo.text()) if self.menu_crear_pedido_entry_almuerzo.text() else 0
        numero_cena = int(self.menu_crear_pedido_entry_cena.text()) if self.menu_crear_pedido_entry_cena.text() else 0
        numero_jugo = int(self.menu_crear_pedido_entry_jugo.text()) if self.menu_crear_pedido_entry_jugo.text() else 0
        numero_porron = int(self.menu_crear_pedido_entry_porron.text()) if self.menu_crear_pedido_entry_porron.text() else 0
        descripcion_refrigerio = self.menu_crear_pedido_entry_refrigerio_descripcion.text()
        cantidad_refrigerio = int(self.menu_crear_pedido_entry_refrigerio_cantidad.text()) if self.menu_crear_pedido_entry_refrigerio_cantidad.text() else 0
        precio_refrigerio = 0
        self.menu_confirmar_pedido = QWidget(self)
        self.init_menu_confirmar_pedido(numero_desayuno, numero_almuerzo, numero_cena, numero_jugo, numero_porron, descripcion_refrigerio, cantidad_refrigerio, precio_refrigerio)
        self.setCentralWidget(self.menu_confirmar_pedido)
        self.menu_crear_pedido_limpiar_memoria
        
    def on_menu_crear_pedido_cancelar_clicked(self): #check
        self.menu_pedidos = QWidget(self)
        self.init_menu_pedidos()
        self.setCentralWidget(self.menu_pedidos)
        
    def on_menu_crear_pedido_cerrar_clicked(self): #check
        self.menu_principal = QWidget(self)
        self.init_menu_principal()
        self.setCentralWidget(self.menu_principal)
        
    def on_menu_crear_pedido_refrigerio_clicked(self): #check
        
        self.menu_crear_pedido_boton_cancelar.setGeometry(770, 807, 168, 40)
        self.menu_crear_pedido_boton_aceptar.setGeometry(965, 797, 201, 60)
        self.menu_crear_pedido_boton_refrigerio.setParent(None)

        self.menu_crear_pedido_entry_desayuno.setGeometry(813, 383, 45, 40)
        self.menu_crear_pedido_entry_almuerzo.setGeometry(813, 459, 45, 40)
        self.menu_crear_pedido_entry_cena.setGeometry(813, 539, 45, 40)
        self.menu_crear_pedido_entry_jugo.setGeometry(1257, 383, 45, 40)
        self.menu_crear_pedido_entry_porron.setGeometry(1257, 459, 45, 40)

        self.menu_crear_pedido_boton_refrigerio.setGeometry(1216, 541, 131, 42)
        
        self.menu_crear_pedido_entry_refrigerio_descripcion.setGeometry(562, 666, 383, 71)
        self.menu_crear_pedido_entry_refrigerio_cantidad.setGeometry(981, 666, 152, 71)
        #self.menu_crear_pedido_entry_refrigerio_precio.setGeometry(1192, 666, 151, 71)
        
        self.background_label1.hide()  # Ocultar fondo_1.png para revelar fondo_2.png
        
    def menu_crear_pedido_limpiar_memoria(self): #check
        del self.menu_crear_pedido_boton_cancelar
        del self.menu_crear_pedido_boton_aceptar
        del self.menu_crear_pedido_boton_cerrar
        del self.menu_crear_pedido_numero_desayuno
        del self.menu_crear_pedido_numero_almuerzo
        del self.menu_crear_pedido_numero_cena
        del self.menu_crear_pedido_numero_jugo
        del self.menu_crear_pedido_numero_porron
        del self.menu_crear_pedido_entry_desayuno
        del self.menu_crear_pedido_entry_almuerzo
        del self.menu_crear_pedido_entry_cena
        del self.menu_crear_pedido_entry_jugo
        del self.menu_crear_pedido_entry_porron
        del self.menu_crear_pedido_refrigerio_descripcion
        del self.menu_crear_pedido_refrigerio_cantidad
        del self.menu_crear_pedido_refrigerio_precio
        del self.menu_crear_pedido_boton_refrigerio
        del self.menu_crear_pedido_entry_refrigerio_descripcion
        del self.menu_crear_pedido_entry_refrigerio_cantidad
        #del self.menu_crear_pedido_entry_refrigerio_precio
        
    def on_menu_confirmar_pedido_aceptar_clicked(self): #check
        # Obtener el area y soporte del pedido
        area = self.menu_confirmar_pedido_drop_area.currentText()
        soporte = self.menu_confirmar_pedido_entry_soporte.text()
        
        if area == 'Seleccionar':
            self.label_errores.setText("Por favor, complete todos los campos requeridos")
            self.label_errores.setGeometry(650, 870, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_confirmar_pedido_drop_area.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px; border: 2px solid #E10909;")
        elif not soporte:
            self.menu_confirmar_pedido_drop_area.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.label_errores.setText("Por favor, complete todos los campos requeridos")
            self.label_errores.setGeometry(650, 870, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_confirmar_pedido_entry_soporte.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px; border: 2px solid #E10909;")
        else:
            self.menu_confirmar_pedido_drop_area.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.menu_confirmar_pedido_entry_soporte.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.label_errores.setText("")
            self.menu_confirmar_pedido_boton_editar.setParent(None)
            self.menu_confirmar_pedido_boton_aceptar.setParent(None)
            
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()

            # Obtener la fecha y hora actual
            now = datetime.now()
            fecha = now.strftime("%Y-%m-%d")
            hora = now.strftime("%H:%M")

            sede = self.sede

            # Lista de servicios y cantidades correspondientes
            servicios = self.lista_servicios
            cantidades = self.cantidades
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Iterar sobre los servicios y sus cantidades correspondientes
            for servicio, cantidad in zip(servicios, cantidades):
                if cantidad > 0:
                    if servicio == "Refrigerio":
                        # Usar los valores de refrigerio
                        precio = cantidad * self.menu_confirmar_pedido_precio_refrigerio
                        descripcion = self.menu_confirmar_pedido_descripcion_refrigerio
                    else:
                        
                        cursor.execute("SELECT precio, descripcion FROM menu WHERE tipo = ?", (servicio,))
                        resultado = cursor.fetchone()
                        precio_unitario, descripcion = resultado
                        precio = precio_unitario * cantidad

                    # Generar el id_pedido
                    id_pedido = f"{now.strftime('%d-%m-%H-%M')}-{servicio}-{area}-{sede}"

                    # Insertar el registro en la tabla pedidos
                    cursor.execute("""
                        INSERT INTO pedidos (id_pedido, fecha, hora, tipo, cantidad, area, precio, sede, soporte, descripcion, estado, fecha_ultima_modificacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (id_pedido, fecha, hora, servicio, cantidad, area, precio, sede, soporte, descripcion, "Pendiente", fecha_actual))

            # Confirmar la transacción y cerrar la conexión
            connection.commit()
            connection.close()
            
            self.background_label1.hide()  # Ocultar fondo_1.png para revelar fondo_2.png

    def on_menu_confirmar_pedido_editar_clicked(self): #check
        numero_desayuno=self.cantidades[0]
        numero_almuerzo=self.cantidades[1]
        numero_cena=self.cantidades[2]
        numero_jugo=self.cantidades[3]
        numero_porron=self.cantidades[4]
        refrigerio_cantidad=self.cantidades[5]
        refrigerio_descripcion=self.menu_confirmar_pedido_descripcion_refrigerio
        refrigerio_precio=self.menu_confirmar_pedido_precio_refrigerio
        
        self.menu_crear_pedido = QWidget(self)
        self.init_menu_crear_pedido(numero_desayuno, numero_almuerzo, numero_cena, numero_jugo, numero_porron, refrigerio_descripcion, refrigerio_cantidad, refrigerio_precio)
        self.setCentralWidget(self.menu_crear_pedido)
        
    def on_menu_confirmar_pedido_cerrar_clicked(self): #check
        self.menu_pedidos = QWidget(self)
        self.init_menu_pedidos()
        self.setCentralWidget(self.menu_pedidos) 
    
    def on_menu_lista_pedidos_cerrar_clicked(self): #check
        self.menu_pedidos = QWidget(self)
        self.init_menu_pedidos()
        self.setCentralWidget(self.menu_pedidos)
    
    def on_menu_lista_pedidos_crear_clicked(self): #check
        self.menu_crear_pedido = QWidget(self)
        self.init_menu_crear_pedido()
        self.setCentralWidget(self.menu_crear_pedido)

    def on_menu_lista_pedidos_eliminar_clicked(self): #check
        count_selected=0
        lista_pedidos=[]
        temp=[]
        for row in range(self.menu_lista_pedidos_tabla.rowCount()):
            checkbox = self.menu_lista_pedidos_tabla.cellWidget(row, 6).layout().itemAt(0).widget()
            if checkbox.isChecked():
                count_selected += 1
                temp.append(self.menu_lista_pedidos_tabla.item(row, 0).text())
                temp.append(self.menu_lista_pedidos_tabla.item(row, 1).text())
                temp.append(self.menu_lista_pedidos_tabla.item(row, 2).text())
                lista_pedidos.append(temp)
                temp=[]
                
        mensaje = "¿Seguro que desea eliminar " + str(count_selected) + " pedidos?"
        self.popup = PopupEliminarPedidos(mensaje, lista_pedidos)
        self.popup.show()
        
    def on_menu_lista_pedidos_aprobar_clicked(self): #aprobar
        count_selected = 0
        lista_pedidos = []
        temp = []

        for row in range(self.menu_lista_pedidos_tabla.rowCount()):
            checkbox = self.menu_lista_pedidos_tabla.cellWidget(row, 6).layout().itemAt(0).widget()
            if checkbox.isChecked():
                count_selected += 1
                temp.append(self.menu_lista_pedidos_tabla.item(row, 0).text())
                temp.append(self.menu_lista_pedidos_tabla.item(row, 1).text())
                temp.append(self.menu_lista_pedidos_tabla.item(row, 2).text())
                lista_pedidos.append(temp)
                temp = []
                
        self.menu_aprobar_pedidos = QWidget(self)
        self.init_menu_aprobar_pedidos(lista_pedidos)
        self.setCentralWidget(self.menu_aprobar_pedidos)
            
    ###
    
    def on_menu_aprobar_pedidos_cerrar_clicked(self):
        self.menu_pedidos = QWidget(self)
        self.init_menu_pedidos()
        self.setCentralWidget(self.menu_pedidos)
        self.join_rfid_thread()
    
    def on_menu_registros_atras_clicked(self): #check
        self.join_rfid_thread()
        self.menu_principal = QWidget(self)
        self.init_menu_principal()
        self.setCentralWidget(self.menu_principal)
        self.timer_servicio2.stop()
        
    def on_menu_registros_manual_clicked(self): #check
        self.join_rfid_thread()
        self.menu_registro_manual = QWidget(self)
        self.init_menu_registro_manual()
        self.setCentralWidget(self.menu_registro_manual)
        self.timer_servicio2.stop()
    
    def on_menu_registro_manual_existente_clicked(self): #check
        self.menu_registro_manualE = QWidget(self)
        self.init_menu_registro_existente()
        self.setCentralWidget(self.menu_registro_manualE)
        
    def on_menu_registro_manual_nuevo_clicked(self): #check
        self.menu_registro_manualN = QWidget(self)
        self.init_menu_registro_nuevo()
        self.setCentralWidget(self.menu_registro_manualN)
    
    def on_menu_registro_manual_cerrar_clicked(self): #check
        self.menu_registros = QWidget(self)
        self.init_menu_registros()
        self.setCentralWidget(self.menu_registros)
    
    def on_menu_registro_existente_cerrar_clicked(self): #check
        self.menu_registros = QWidget(self)
        self.init_menu_registros()
        self.setCentralWidget(self.menu_registros)
        
    def on_menu_registro_existente_cancelar_clicked(self): #check
        self.menu_registros = QWidget(self)
        self.init_menu_registros()
        self.setCentralWidget(self.menu_registros)
        
    def on_menu_registro_existente_siguiente_clicked(self):
        cedula=self.menu_registro_existente_entry_cedula.text()
        servicio = self.valor_servicio_actual
        
        # Conectar a la base de datos
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Buscar en la tabla usuarios los campos nombre y rol usando la cédula
        cursor.execute("SELECT nombre, rol FROM usuarios WHERE cedula = ?", (cedula,))
        result = cursor.fetchone()
        
        # Cerrar la conexión a la base de datos
        conn.close()
        
        if result:
            nombre, rol = result
            # Asignar los valores obtenidos a los atributos correspondientes
            self.menu_registro_existente_nombre = nombre
            self.menu_registro_existente_rol = rol
            self.menu_confirmar_registro_manualE = QWidget(self)
            self.init_menu_confirmar_registro_manual_existente(cedula, nombre, rol, servicio)
            self.setCentralWidget(self.menu_confirmar_registro_manualE)
        else:
            self.label_errores.setText("La cedula ingresada no se encuentra registrada")
            self.label_errores.setGeometry(650, 710, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
        
    def on_menu_registro_nuevo_cerrar_clicked(self): #check
        self.menu_registros = QWidget(self)
        self.init_menu_registros()
        self.setCentralWidget(self.menu_registros)
        
    def on_menu_registro_nuevo_cancelar_clicked(self): #check
        self.menu_registros = QWidget(self)
        self.init_menu_registros()
        self.setCentralWidget(self.menu_registros)
        
    def on_menu_registro_nuevo_siguiente_clicked(self): #check
        cedula = self.menu_formulario_usuarioN_entry_cedula.text()
        nombre = self.menu_formulario_usuarioN_entry_nombre.text()
        area = self.menu_formulario_usuarioN_rol_drop.currentText()
        servicio = self.valor_servicio_actual
        
        # Verificar que la cédula no exista en la base de datos
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cedula = ?", (cedula,))
        result = cursor.fetchone()
        
        conn.close()
        
        # Verificar que los campos no estén vacíos y que el rol no sea "Seleccionar"
        if cedula == "":
            self.label_errores.setText("Por favor, complete todos los campos requeridos")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px; border: 2px solid #E10909;")
        elif not nombre:
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.label_errores.setText("Por favor, complete todos los campos requeridos")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_entry_nombre.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px; border: 2px solid #E10909;")
        elif area == "Seleccionar":
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.menu_formulario_usuarioN_entry_nombre.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.label_errores.setText("Por favor, seleccione un area para el usuario")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_rol_drop.setStyleSheet("border: 2px solid #E10909;")
        elif result[0] > 0:
            self.menu_formulario_usuarioN_rol_drop.setStyleSheet("")
            self.menu_formulario_usuarioN_entry_nombre.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px;")
            self.label_errores.setText("Número de identificación ya existente")
            self.label_errores.setGeometry(650, 799, 700, 28)
            self.label_errores.setAlignment(Qt.AlignCenter)
            self.menu_formulario_usuarioN_entry_cedula.setStyleSheet("font-size: 36px; font-family: Poppins; color: #727272; border-radius: 10px; border: 2px solid #E10909;")
        else:
            # Proceder con la funcionalidad original si todas las verificaciones pasan
            self.menu_confirmar_registro_manualN = QWidget(self)
            self.init_menu_confirmar_registro_manual_nuevo(cedula, nombre, area, servicio)
            self.setCentralWidget(self.menu_confirmar_registro_manualN)
    
    def on_menu_confirmar_registro_manualN_cerrar_clicked(self): #check
        self.menu_registros = QWidget(self)
        self.init_menu_registros()
        self.setCentralWidget(self.menu_registros)
        
    def on_menu_confirmar_registro_manualN_editar_clicked(self): #check
        self.menu_registro_manualN = QWidget(self)
        self.init_menu_registro_nuevo(self.menu_confirmar_registro_manualN_cedula, self.menu_confirmar_registro_manualN_nombre, self.menu_confirmar_registro_manualN_rol)
        self.setCentralWidget(self.menu_registro_manualN)
        
    def on_menu_confirmar_registro_manualN_aceptar_clicked(self): #check
        self.menu_confirmar_registro_manualN_boton_editar.setParent(None)
        self.menu_confirmar_registro_manualN_boton_aceptar.setParent(None)
        
        # Obtener la fecha y hora actual
        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M")
        tipo = self.menu_confirmar_registro_manualN_servicio
        sede = self.sede
        cedula = self.menu_confirmar_registro_manualN_cedula
        nombre = self.menu_confirmar_registro_manualN_nombre
        area = self.menu_confirmar_registro_manualN_rol
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if area=='Direacto':
            rol='Directo'
        else:
            rol='Usuario'

        # Conectar a la base de datos
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Obtener el precio del servicio
        cursor.execute("SELECT precio FROM menu WHERE tipo = ?", (tipo,))
        precio_result = cursor.fetchone()
        if precio_result:
            precio = precio_result[0]
        else:
            print("Error: No se encontró el precio para el tipo de servicio proporcionado.")
            conn.close()
            return

        # Insertar el usuario en la tabla usuarios
        cursor.execute("""
            INSERT INTO usuarios (nombre, cedula, area, flag_retirado, rol, fecha_ultima_modificacion)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(cedula) DO UPDATE SET
                nombre = excluded.nombre,
                rol = excluded.rol,
                flag_retirado = excluded.flag_retirado,
                fecha_ultima_modificacion = excluded.fecha_ultima_modificacion
        """, (nombre, cedula, area, 0, rol, fecha_actual))

        # Crear y codificar id_registro
        id_registro = f"{fecha}-{hora}-{tipo}-{sede}-{cedula}"

        # Insertar el registro en la tabla registros
        cursor.execute("""
            INSERT INTO registros (id_registro, fecha, hora, tipo, sede, precio, cedula)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_registro, fecha, hora, tipo, sede, precio, cedula))

        # Confirmar cambios y cerrar la conexión
        conn.commit()
        conn.close()
        
        # Aquí puedes agregar cualquier otra funcionalidad necesaria después de realizar las inserciones
        print("Registro completado con éxito.")
        
        self.background_label1.hide()  # Ocultar fondo_1.png para revelar fondo_2.png
        
    def on_menu_confirmar_registro_manualE_cerrar_clicked(self): #check
        self.menu_registros = QWidget(self)
        self.init_menu_registros()
        self.setCentralWidget(self.menu_registros)
        
    def on_menu_confirmar_registro_manualE_editar_clicked(self): #check
        self.menu_registro_manualN = QWidget(self)
        self.init_menu_registro_nuevo(self.menu_confirmar_registro_manualE_cedula)
        self.setCentralWidget(self.menu_registro_manualN)
        
    def on_menu_confirmar_registro_manualE_aceptar_clicked(self): #check
        self.menu_confirmar_registro_manualE_boton_editar.setParent(None)
        self.menu_confirmar_registro_manualE_boton_aceptar.setParent(None)
        
        # Obtener la fecha y hora actual
        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M")
        tipo = self.menu_confirmar_registro_manualE_servicio
        sede = self.sede
        cedula = self.menu_confirmar_registro_manualE_cedula
        nombre = self.menu_confirmar_registro_manualE_nombre
        rol = self.menu_confirmar_registro_manualE_rol
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Conectar a la base de datos
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Obtener el precio del servicio
        cursor.execute("SELECT precio FROM menu WHERE tipo = ?", (tipo,))
        precio_result = cursor.fetchone()
        if precio_result:
            precio = precio_result[0]
        else:
            print("Error: No se encontró el precio para el tipo de servicio proporcionado.")
            conn.close()
            return

        # Crear y codificar id_registro
        id_registro = f"{fecha}-{hora}-{tipo}-{sede}-{cedula}"

        # Insertar el registro en la tabla registros
        cursor.execute("""
            INSERT INTO registros (id_registro, fecha, hora, tipo, sede, precio, cedula)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_registro, fecha, hora, tipo, sede, precio, cedula))

        # Confirmar cambios y cerrar la conexión
        conn.commit()
        conn.close()
        
        # Aquí puedes agregar cualquier otra funcionalidad necesaria después de realizar las inserciones
        print("Registro completado con éxito.")
        
        self.background_label1.hide()  # Ocultar fondo_1.png para revelar fondo_2.png
        
    def on_menu_registro_tarjeta_invalida_atras_clicked(self): #check
        self.menu_registros = QWidget(self)
        self.init_menu_registros()
        self.setCentralWidget(self.menu_registros)
        
    def on_menu_registro_tarjeta_invalida_manual_clicked(self): #check
        self.menu_registro_manual = QWidget(self)
        self.init_menu_registro_manual()
        self.setCentralWidget(self.menu_registro_manual)
        
    def on_menu_registro_tarjeta_cerrar_clicked(self): #check
        # Obtener la fecha y hora actual
        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M")
        tipo = self.menu_confirmar_registro_manualE_servicio
        sede = self.sede
        cedula = self.menu_confirmar_usuario_cedula
        nombre = self.menu_confirmar_usuario_nombre
        rol = self.menu_confirmar_usuario_rol
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Conectar a la base de datos
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Obtener el precio del servicio
        cursor.execute("SELECT precio FROM menu WHERE tipo = ?", (tipo,))
        precio_result = cursor.fetchone()
        if precio_result:
            precio = precio_result[0]
        else:
            print("Error: No se encontró el precio para el tipo de servicio proporcionado.")
            conn.close()
            return

        # Crear y codificar id_registro
        id_registro = f"{fecha}-{hora}-{tipo}-{sede}-{cedula}"

        # Insertar el registro en la tabla registros
        cursor.execute("""
            INSERT INTO registros (id_registro, fecha, hora, tipo, sede, precio, cedula)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_registro, fecha, hora, tipo, sede, precio, cedula))

        # Confirmar cambios y cerrar la conexión
        conn.commit()
        conn.close()
        
        # Aquí puedes agregar cualquier otra funcionalidad necesaria después de realizar las inserciones
        print("Registro completado con éxito.")
        
        self.menu_registros = QWidget(self)
        self.init_menu_registros()
        self.setCentralWidget(self.menu_registros)
        
        
class PopupEliminarUsuarios(QWidget):
    def __init__(self, mensaje, lista_cedulas):
        super().__init__()
        self.mensaje = mensaje
        self.lista_cedulas = lista_cedulas
        self.init_ui()
        self.db='Desarrollo/Database/marmato_db.db'
    
    def init_ui(self):
        self.setWindowTitle('Eliminar Usuario')
        self.setGeometry(494, 406, 933, 342)  # Posición y tamaño de la ventana
        self.setWindowFlags(Qt.FramelessWindowHint)  # Quitar el marco de la ventana
        self.set_background_images("Desarrollo/Assets/menuListaUsuarios/pop_up_1.png", "Desarrollo/Assets/menuListaUsuarios/pop_up_2.png")

        self.mensaje=self.create_label(self, self.mensaje, 110, 100, 700, 50, 36, "#727272", "Poppins", False)
        self.create_image_button(self, "Desarrollo/Assets/Commons/x.png", 39, 39, 857, 30, self.close_popup, True)
        self.boton_cancelar=self.create_text_button(self, "Cancelar", 269, 227, 168, 40, 36, "#727272", "Poppins", self.close_popup, True)
        self.boton_aceptar=self.create_image_button(self, "Desarrollo/Assets/Commons/boton_aceptar.png", 201, 60, 464, 217, self.accept_action, True)

    def create_label(self, menu, text, x, y, width, height, font_size, font_color, font_family, flag):
        label = QLabel(text, menu)
        label.setGeometry(x, y, width, height)
        if flag:
            label.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family}; font-weight: bold")  
        else:
            label.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family};")
        return label
        
    def set_background_images(self, image_path1, image_path2):
        self.background_label1 = QLabel(self)
        self.background_label1.setGeometry(0, 0, 933, 342)
        pixmap1 = QPixmap(image_path1)
        self.background_label1.setPixmap(pixmap1.scaled(933, 342))
        
        self.background_label2 = QLabel(self)
        self.background_label2.setGeometry(0, 0, 933, 342)
        pixmap2 = QPixmap(image_path2)
        self.background_label2.setPixmap(pixmap2.scaled(933, 342))
        self.background_label2.lower()  # Poner fondo_2.png por debajo de fondo_1.png

    def create_image_button(self, menu, image_path, width, height, x, y, action, transparent):
        button = QPushButton(menu)
        button.setGeometry(x, y, width, height)
        pixmap = QPixmap(image_path)
        icon = QIcon(pixmap)
        button.setIcon(icon)
        button.setIconSize(pixmap.size())
        button.clicked.connect(action)
        if transparent:
            button.setStyleSheet("background-color: transparent; border: none;")
        return button

    def create_text_button(self, menu, text, x, y, width, height, font_size, font_color, font_family, action, no_border):
        button = QPushButton(text, menu)
        button.setGeometry(x, y, width, height)
        button.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family};")
        button.clicked.connect(action)
        if no_border:
            button.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family}; background-color: transparent; border: none;")  # Removiendo el borde
        else:
            button.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family};")
        return button

    def close_popup(self):
        self.close()
    
    def accept_action(self):
        self.mensaje.setParent(None)
        self.boton_cancelar.setParent(None)
        self.boton_aceptar.setParent(None)
        self.background_label1.hide()  # Ocultar fondo_1.png para revelar fondo_2.png
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()

        try:
            placeholders = ','.join(['?'] * len(self.lista_cedulas))

            sql_query = f"""
            UPDATE usuarios
            SET flag_retirado = ?, fecha_ultima_modificacion = ?, id_tarjeta = ?
            WHERE cedula IN ({placeholders})
            """

            values = [True, fecha_actual, ""] + self.lista_cedulas
            cursor.execute(sql_query, values)
            connection.commit()

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
        
class PopupEliminarPedidos(QWidget):
    def __init__(self, mensaje, lista_pedidos):
        super().__init__()
        self.mensaje = mensaje
        self.lista_pedidos = lista_pedidos
        self.init_ui()
        self.db='Desarrollo/Database/marmato_db.db'
    
    def init_ui(self):
        self.setWindowTitle('Eliminar Pedido')
        self.setGeometry(494, 406, 933, 342)  # Posición y tamaño de la ventana
        self.setWindowFlags(Qt.FramelessWindowHint)  # Quitar el marco de la ventana
        self.set_background_images("Desarrollo/Assets/menuListaPedidos/pop_up_1.png", "Desarrollo/Assets/menuListaPedidos/pop_up_2.png")

        self.mensaje=self.create_label(self, self.mensaje, 110, 100, 750, 50, 36, "#727272", "Poppins", False)
        self.create_image_button(self, "Desarrollo/Assets/Commons/x.png", 39, 39, 857, 30, self.close_popup, True)
        self.boton_cancelar=self.create_text_button(self, "Cancelar", 269, 227, 168, 40, 36, "#727272", "Poppins", self.close_popup, True)
        self.boton_aceptar=self.create_image_button(self, "Desarrollo/Assets/Commons/boton_aceptar.png", 201, 60, 464, 217, self.accept_action, True)

    def create_label(self, menu, text, x, y, width, height, font_size, font_color, font_family, flag):
        label = QLabel(text, menu)
        label.setGeometry(x, y, width, height)
        if flag:
            label.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family}; font-weight: bold")  
        else:
            label.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family};")
        return label
        
    def set_background_images(self, image_path1, image_path2):
        self.background_label1 = QLabel(self)
        self.background_label1.setGeometry(0, 0, 933, 342)
        pixmap1 = QPixmap(image_path1)
        self.background_label1.setPixmap(pixmap1.scaled(933, 342))
        
        self.background_label2 = QLabel(self)
        self.background_label2.setGeometry(0, 0, 933, 342)
        pixmap2 = QPixmap(image_path2)
        self.background_label2.setPixmap(pixmap2.scaled(933, 342))
        self.background_label2.lower()  # Poner fondo_2.png por debajo de fondo_1.png

    def create_image_button(self, menu, image_path, width, height, x, y, action, transparent):
        button = QPushButton(menu)
        button.setGeometry(x, y, width, height)
        pixmap = QPixmap(image_path)
        icon = QIcon(pixmap)
        button.setIcon(icon)
        button.setIconSize(pixmap.size())
        button.clicked.connect(action)
        if transparent:
            button.setStyleSheet("background-color: transparent; border: none;")
        return button

    def create_text_button(self, menu, text, x, y, width, height, font_size, font_color, font_family, action, no_border):
        button = QPushButton(text, menu)
        button.setGeometry(x, y, width, height)
        button.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family};")
        button.clicked.connect(action)
        if no_border:
            button.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family}; background-color: transparent; border: none;")  # Removiendo el borde
        else:
            button.setStyleSheet(f"color: {font_color}; font-size: {font_size}px; font-family: {font_family};")
        return button

    def close_popup(self):
        self.close()
    
    def accept_action(self):
        self.mensaje.setParent(None)
        self.boton_cancelar.setParent(None)
        self.boton_aceptar.setParent(None)
        self.background_label1.hide()  # Ocultar fondo_1.png para revelar fondo_2.png
        
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()

        try:
            for pedido in self.lista_pedidos:
                fecha, hora, tipo = pedido
                
                # Crear la consulta SQL para eliminar el pedido específico
                sql_query = """
                DELETE FROM pedidos
                WHERE fecha = ? AND hora = ? AND tipo = ?
                """
                
                # Ejecutar la consulta con los valores correspondientes
                cursor.execute(sql_query, (fecha, hora, tipo))
            
            # Confirmar los cambios
            connection.commit()

        except sqlite3.Error as e:
            #print(f"An error occurred: {e}")
            connection.rollback()

        finally:
            # Cerrar la conexión
            cursor.close()
            connection.close()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
