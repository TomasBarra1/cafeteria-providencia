import streamlit as st
import threading
import time
from datetime import datetime, date
from io import BytesIO
import pandas as pd

# ============================================================
# CLASES DEL SISTEMA
# ============================================================

class Producto:
    def __init__(self, codigo, nombre, precio):
        self._codigo = codigo
        self._nombre = nombre
        self._precio = precio

    def obtener_codigo(self):
        return self._codigo

    def obtener_nombre(self):
        return self._nombre

    def obtener_precio(self):
        return self._precio

    def descripcion(self):
        return f"{self._codigo} - {self._nombre} - ${self._precio:,.0f}"


class Bebida(Producto):
    def __init__(self, codigo, nombre, precio, tamanio_ml):
        super().__init__(codigo, nombre, precio)
        self._tamanio_ml = tamanio_ml

    def descripcion(self):
        return f"{self._codigo} - {self._nombre} ({self._tamanio_ml} ml) - ${self._precio:,.0f}"


class Alimento(Producto):
    def __init__(self, codigo, nombre, precio, calorias):
        super().__init__(codigo, nombre, precio)
        self._calorias = calorias

    def descripcion(self):
        return f"{self._codigo} - {self._nombre} ({self._calorias} cal) - ${self._precio:,.0f}"


class Inventario:
    def __init__(self):
        self._productos = {}
        self._stock = {}

    def agregar_producto(self, producto, cantidad):
        codigo = producto.obtener_codigo()
        self._productos[codigo] = producto
        self._stock[codigo] = self._stock.get(codigo, 0) + cantidad

    def reponer_stock(self, codigo, cantidad):
        if codigo in self._stock and cantidad > 0:
            self._stock[codigo] += cantidad
            return True
        return False

    def obtener_producto(self, codigo):
        return self._productos.get(codigo)

    def obtener_stock(self, codigo):
        return self._stock.get(codigo, 0)

    def descontar_stock(self, codigo, cantidad):
        if codigo in self._stock and self._stock[codigo] >= cantidad:
            self._stock[codigo] -= cantidad
            return True
        return False

    def devolver_stock(self, codigo, cantidad):
        if codigo in self._stock:
            self._stock[codigo] += cantidad

    def productos(self):
        return self._productos.items()

    def stock_total(self):
        return sum(self._stock.values())


class ItemPedido:
    def __init__(self, producto, cantidad):
        self._producto = producto
        self._cantidad = cantidad

    def obtener_producto(self):
        return self._producto

    def obtener_cantidad(self):
        return self._cantidad

    def subtotal(self):
        return self._producto.obtener_precio() * self._cantidad

    def descripcion(self):
        return f"{self._cantidad} x {self._producto.obtener_nombre()} = ${self.subtotal():,.0f}"


class Pedido:
    def __init__(self, id_pedido, cliente, fecha_operacion=None):
        self._id_pedido = id_pedido
        self._cliente = cliente
        self._items = []
        self._estado = "Pendiente"
        self._fecha = fecha_operacion if fecha_operacion is not None else date.today()
        self._fecha_hora = datetime.now().strftime("%d-%m-%Y %H:%M")
        self._metodo_pago = "No registrado"

    def obtener_id(self):
        return self._id_pedido

    def obtener_cliente(self):
        return self._cliente

    def obtener_estado(self):
        return self._estado

    def obtener_fecha(self):
        return self._fecha

    def obtener_fecha_hora(self):
        return self._fecha_hora

    def obtener_metodo_pago(self):
        return self._metodo_pago

    def registrar_pago(self, metodo_pago):
        self._metodo_pago = metodo_pago

    def cerrar_pedido(self):
        self._estado = "Cerrado"

    def agregar_item(self, producto, cantidad):
        self._items.append(ItemPedido(producto, cantidad))

    def obtener_items(self):
        return self._items

    def calcular_subtotal(self):
        total = 0
        for item in self._items:
            total += item.subtotal()
        return total

    def calcular_total(self):
        return self.calcular_subtotal()

    def obtener_tipo(self):
        return "Pedido general"


class VentaNormal(Pedido):
    def __init__(self, id_pedido, cliente, fecha_operacion=None):
        super().__init__(id_pedido, cliente, fecha_operacion)
        self._estado = "Pendiente de pago"

    def calcular_total(self):
        return self.calcular_subtotal()

    def obtener_tipo(self):
        return "Venta normal"


class ConsumoLocal(Pedido):
    def __init__(self, id_pedido, cliente, mesa, fecha_operacion=None):
        super().__init__(id_pedido, cliente, fecha_operacion)
        self._mesa = mesa
        self._estado = "En consumo"

    def obtener_mesa(self):
        return self._mesa

    def calcular_total(self):
        return self.calcular_subtotal()

    def obtener_tipo(self):
        return "Consumo en local"


class PedidoDelivery(Pedido):
    def __init__(self, id_pedido, cliente, zona, direccion, cargo_envio, fecha_operacion=None):
        super().__init__(id_pedido, cliente, fecha_operacion)
        self._zona = zona
        self._direccion = direccion
        self._cargo_envio = cargo_envio
        self._estado = "Pendiente de despacho"

    def obtener_zona(self):
        return self._zona

    def obtener_direccion(self):
        return self._direccion

    def obtener_cargo_envio(self):
        return self._cargo_envio

    def calcular_total(self):
        return self.calcular_subtotal() + self._cargo_envio

    def obtener_tipo(self):
        return "Delivery"


class ProcesadorPedidos:
    def __init__(self):
        self._pedidos_procesados = []

    def procesar_pedido(self, pedido):
        time.sleep(2)
        pedido.cerrar_pedido()
        self._pedidos_procesados.append(pedido)

    def procesar_pedidos_concurrentes(self, pedidos):
        hilos = []

        for pedido in pedidos:
            hilo = threading.Thread(target=self.procesar_pedido, args=(pedido,))
            hilos.append(hilo)
            hilo.start()

        for hilo in hilos:
            hilo.join()

        return self._pedidos_procesados


# ============================================================
# FUNCIONES DE APOYO
# ============================================================

def crear_inventario_inicial():
    inventario = Inventario()
    inventario.agregar_producto(Bebida("B001", "Café Americano", 2500, 250), 10)
    inventario.agregar_producto(Bebida("B002", "Café Latte", 3500, 300), 8)
    inventario.agregar_producto(Bebida("B003", "Té", 1800, 250), 12)
    inventario.agregar_producto(Bebida("B004", "Chocolate caliente", 3000, 300), 6)
    inventario.agregar_producto(Alimento("A001", "Sándwich", 4500, 500), 6)
    inventario.agregar_producto(Alimento("A002", "Porción de torta", 3200, 450), 5)
    inventario.agregar_producto(Alimento("A003", "Galleta", 1200, 180), 15)
    inventario.agregar_producto(Alimento("A004", "Muffin", 2200, 300), 9)
    return inventario


def zonas_delivery():
    return {
        "Zona 1 - Cercana a Providencia: Providencia, Ñuñoa, Santiago centro": 1500,
        "Zona 2 - Oriente: Las Condes, Vitacura, La Reina": 2500,
        "Zona 3 - Norte: Recoleta, Independencia, Huechuraba": 3000,
        "Zona 4 - Sur/Poniente: Macul, San Joaquín, San Miguel, Estación Central": 3500,
    }


def metodos_pago():
    return ["Efectivo", "Tarjeta de débito", "Tarjeta de crédito", "Transferencia", "Otro"]


def calcular_total_carrito(carrito):
    total = 0
    for item in carrito:
        total += item["producto"].obtener_precio() * item["cantidad"]
    return total


def limpiar_carrito():
    st.session_state.carrito = []


def pedidos_por_fecha(fecha):
    return [pedido for pedido in st.session_state.historial if pedido.obtener_fecha() == fecha]


def total_ventas_por_fecha(fecha):
    total = 0
    for pedido in pedidos_por_fecha(fecha):
        total += pedido.calcular_total()
    return total


def cantidad_productos_vendidos(fecha):
    cantidad = 0
    for pedido in pedidos_por_fecha(fecha):
        for item in pedido.obtener_items():
            cantidad += item.obtener_cantidad()
    return cantidad


def crear_dataframe_ventas(pedidos):
    filas = []

    for pedido in pedidos:
        for item in pedido.obtener_items():
            producto = item.obtener_producto()
            fila = {
                "Fecha": pedido.obtener_fecha().strftime("%d-%m-%Y"),
                "Fecha y hora": pedido.obtener_fecha_hora(),
                "ID pedido": pedido.obtener_id(),
                "Cliente": pedido.obtener_cliente(),
                "Tipo de venta": pedido.obtener_tipo(),
                "Estado": pedido.obtener_estado(),
                "Método de pago": pedido.obtener_metodo_pago(),
                "Código producto": producto.obtener_codigo(),
                "Producto": producto.obtener_nombre(),
                "Cantidad": item.obtener_cantidad(),
                "Precio unitario": producto.obtener_precio(),
                "Subtotal línea": item.subtotal(),
                "Total pedido": pedido.calcular_total(),
            }

            if isinstance(pedido, ConsumoLocal):
                fila["Mesa"] = pedido.obtener_mesa()
            else:
                fila["Mesa"] = ""

            if isinstance(pedido, PedidoDelivery):
                fila["Zona delivery"] = pedido.obtener_zona()
                fila["Dirección delivery"] = pedido.obtener_direccion()
                fila["Tarifa delivery"] = pedido.obtener_cargo_envio()
            else:
                fila["Zona delivery"] = ""
                fila["Dirección delivery"] = ""
                fila["Tarifa delivery"] = 0

            filas.append(fila)

    return pd.DataFrame(filas)


def convertir_excel(df):
    salida = BytesIO()
    with pd.ExcelWriter(salida, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Ventas")
    return salida.getvalue()


def mostrar_comprobante(pedido):
    st.markdown("---")
    st.subheader("🧾 Comprobante de venta")
    st.write("**Cafetería Providencia**")
    st.write(f"**Fecha y hora:** {pedido.obtener_fecha_hora()}")
    st.write(f"**N° pedido:** {pedido.obtener_id()}")
    st.write(f"**Cliente:** {pedido.obtener_cliente()}")
    st.write(f"**Tipo de venta:** {pedido.obtener_tipo()}")
    st.write(f"**Método de pago:** {pedido.obtener_metodo_pago()}")

    if isinstance(pedido, ConsumoLocal):
        st.write(f"**Mesa:** {pedido.obtener_mesa()}")

    if isinstance(pedido, PedidoDelivery):
        st.write(f"**Zona:** {pedido.obtener_zona()}")
        st.write(f"**Dirección:** {pedido.obtener_direccion()}")
        st.write(f"**Tarifa delivery:** ${pedido.obtener_cargo_envio():,.0f}")

    st.write("**Detalle:**")
    for item in pedido.obtener_items():
        st.write(f"- {item.descripcion()}")

    st.write(f"### Total pagado: ${pedido.calcular_total():,.0f}")
    st.markdown("---")


def resumen_caja(fecha):
    pedidos = pedidos_por_fecha(fecha)
    return {
        "fecha": fecha.strftime("%d-%m-%Y"),
        "cantidad_pedidos": len(pedidos),
        "total_vendido": total_ventas_por_fecha(fecha),
        "productos_vendidos": cantidad_productos_vendidos(fecha),
        "hora_cierre": datetime.now().strftime("%d-%m-%Y %H:%M"),
    }


# ============================================================
# CONFIGURACIÓN INICIAL
# ============================================================

st.set_page_config(page_title="Sistema Cafetería", page_icon="☕", layout="wide")

if "inventario" not in st.session_state:
    st.session_state.inventario = crear_inventario_inicial()

if "pedidos_normales" not in st.session_state:
    st.session_state.pedidos_normales = []

if "pedidos_local" not in st.session_state:
    st.session_state.pedidos_local = []

if "pedidos_delivery" not in st.session_state:
    st.session_state.pedidos_delivery = []

if "historial" not in st.session_state:
    st.session_state.historial = []

if "carrito" not in st.session_state:
    st.session_state.carrito = []

if "caja_abierta" not in st.session_state:
    st.session_state.caja_abierta = True

if "cierres_caja" not in st.session_state:
    st.session_state.cierres_caja = []

if "fecha_sistema" not in st.session_state:
    st.session_state.fecha_sistema = date.today()

fecha_actual = st.date_input("Fecha de operación", value=st.session_state.fecha_sistema)
st.session_state.fecha_sistema = fecha_actual
fecha_texto = fecha_actual.strftime("%d-%m-%Y")

st.title("☕ Sistema de Gestión de Pedidos - Cafetería Providencia")
st.caption(f"Fecha seleccionada: {fecha_texto} | Primero se crea el pedido; pago y cierre se gestionan en Pendientes.")

if st.session_state.caja_abierta:
    st.success("Caja abierta: se pueden crear pedidos.")
else:
    st.error("Caja cerrada: no se pueden crear nuevos pedidos hasta reabrir caja.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Ventas de hoy", f"${total_ventas_por_fecha(fecha_actual):,.0f}")
with col2:
    st.metric("Ventas pendientes", len(st.session_state.pedidos_normales))
with col3:
    st.metric("Mesas en consumo", len(st.session_state.pedidos_local))
with col4:
    st.metric("Delivery pendientes", len(st.session_state.pedidos_delivery))
with col5:
    st.metric("Stock total", st.session_state.inventario.stock_total())

st.divider()

tab_venta, tab_pendientes, tab_inventario, tab_resumen, tab_caja = st.tabs([
    "🧾 Crear pedido",
    "📌 Pendientes y pago",
    "📦 Inventario",
    "📊 Ventas / Excel",
    "🔒 Cierre de caja"
])

# ============================================================
# TAB 1: SOLO CREAR PEDIDO
# ============================================================

with tab_venta:
    if not st.session_state.caja_abierta:
        st.warning("La caja está cerrada. Para crear pedidos debes reabrir caja en la pestaña Cierre de caja.")
    else:
        izquierda, derecha = st.columns([1.1, 1])

        with izquierda:
            st.header("Crear pedido")
            st.info(f"Fecha de registro: {fecha_texto}")

            cliente = st.text_input("Nombre del cliente")

            tipo_venta = st.radio(
                "Tipo de pedido",
                ["Venta normal", "Consumo en local", "Delivery"],
                horizontal=True
            )

            mesa = None
            zona_seleccionada = None
            direccion_delivery = ""
            cargo_envio = 0

            if tipo_venta == "Consumo en local":
                mesa = st.number_input("Número de mesa", min_value=1, step=1)

            if tipo_venta == "Delivery":
                zonas = zonas_delivery()
                zona_seleccionada = st.selectbox("Zona de delivery desde Providencia", list(zonas.keys()))
                direccion_delivery = st.text_input("Dirección exacta de despacho", placeholder="Ejemplo: Av. Providencia 1234, Depto 506")
                cargo_envio = zonas[zona_seleccionada]
                st.info(f"Tarifa de delivery seleccionada: ${cargo_envio:,.0f}")

            st.subheader("Agregar productos")

            opciones_productos = {}
            for codigo, producto in st.session_state.inventario.productos():
                stock = st.session_state.inventario.obtener_stock(codigo)
                texto_visible = f"{codigo} - {producto.obtener_nombre()} | ${producto.obtener_precio():,.0f} | Stock: {stock}"
                opciones_productos[texto_visible] = codigo

            producto_visible = st.selectbox("Producto", list(opciones_productos.keys()))
            producto_codigo = opciones_productos[producto_visible]
            cantidad = st.number_input("Cantidad", min_value=1, step=1)

            if st.button("➕ Agregar producto", use_container_width=True):
                producto = st.session_state.inventario.obtener_producto(producto_codigo)
                stock = st.session_state.inventario.obtener_stock(producto_codigo)

                if stock < cantidad:
                    st.error("No hay stock suficiente para agregar ese producto.")
                else:
                    st.session_state.inventario.descontar_stock(producto_codigo, cantidad)
                    st.session_state.carrito.append({"producto": producto, "cantidad": cantidad})
                    st.success(f"Agregado: {cantidad} x {producto.obtener_nombre()}")
                    st.rerun()

        with derecha:
            st.header("Pedido en creación")

            if len(st.session_state.carrito) == 0:
                st.info("Aún no hay productos agregados.")
            else:
                for indice, item in enumerate(st.session_state.carrito):
                    producto = item["producto"]
                    cantidad_item = item["cantidad"]
                    subtotal = producto.obtener_precio() * cantidad_item

                    col_item_1, col_item_2 = st.columns([3, 1])
                    with col_item_1:
                        st.write(f"**{cantidad_item} x {producto.obtener_nombre()}**")
                        st.caption(f"Subtotal: ${subtotal:,.0f}")
                    with col_item_2:
                        if st.button("Quitar", key=f"quitar_{indice}"):
                            st.session_state.inventario.devolver_stock(producto.obtener_codigo(), cantidad_item)
                            st.session_state.carrito.pop(indice)
                            st.rerun()

                subtotal_carrito = calcular_total_carrito(st.session_state.carrito)
                total_previo = subtotal_carrito + cargo_envio
                st.divider()
                st.write(f"Subtotal productos: **${subtotal_carrito:,.0f}**")
                if tipo_venta == "Delivery":
                    st.write(f"Delivery: **${cargo_envio:,.0f}**")
                st.subheader(f"Total estimado: ${total_previo:,.0f}")
                st.caption("El pago y el cierre se realizan después en la pestaña Pendientes y pago.")

                col_crear, col_limpiar = st.columns(2)
                with col_crear:
                    if st.button("✅ Crear pedido", use_container_width=True):
                        if cliente.strip() == "":
                            st.warning("Debes ingresar el nombre del cliente.")
                        elif tipo_venta == "Delivery" and direccion_delivery.strip() == "":
                            st.warning("Para delivery debes ingresar la dirección exacta de despacho.")
                        else:
                            id_pedido = f"P{len(st.session_state.historial) + len(st.session_state.pedidos_normales) + len(st.session_state.pedidos_local) + len(st.session_state.pedidos_delivery) + 1}"

                            if tipo_venta == "Venta normal":
                                pedido = VentaNormal(id_pedido, cliente, fecha_actual)
                                st.session_state.pedidos_normales.append(pedido)
                                st.success("Pedido de venta normal creado. Quedó pendiente de pago.")
                            elif tipo_venta == "Consumo en local":
                                pedido = ConsumoLocal(id_pedido, cliente, mesa, fecha_actual)
                                st.session_state.pedidos_local.append(pedido)
                                st.success("Pedido local creado. Quedó en consumo.")
                            else:
                                pedido = PedidoDelivery(id_pedido, cliente, zona_seleccionada, direccion_delivery, cargo_envio, fecha_actual)
                                st.session_state.pedidos_delivery.append(pedido)
                                st.success("Pedido delivery creado. Quedó pendiente de pago/despacho.")

                            for item in st.session_state.carrito:
                                pedido.agregar_item(item["producto"], item["cantidad"])

                            limpiar_carrito()
                            st.rerun()

                with col_limpiar:
                    if st.button("🗑️ Vaciar pedido", use_container_width=True):
                        for item in st.session_state.carrito:
                            st.session_state.inventario.devolver_stock(item["producto"].obtener_codigo(), item["cantidad"])
                        limpiar_carrito()
                        st.rerun()

# ============================================================
# TAB 2: PENDIENTES, MODIFICACIÓN Y PAGO
# ============================================================

with tab_pendientes:
    st.header("Pendientes y pago")

    col_normal, col_local, col_delivery = st.columns(3)

    with col_normal:
        st.subheader("Ventas normales por pagar")

        if len(st.session_state.pedidos_normales) == 0:
            st.info("No hay ventas normales pendientes.")
        else:
            for indice, pedido in enumerate(st.session_state.pedidos_normales):
                with st.container(border=True):
                    st.write(f"### {pedido.obtener_id()} - {pedido.obtener_cliente()}")
                    st.caption(pedido.obtener_fecha_hora())
                    for item in pedido.obtener_items():
                        st.write(f"- {item.descripcion()}")
                    st.write(f"**Total a pagar: ${pedido.calcular_total():,.0f}**")

                    metodo_pago = st.selectbox("Método de pago", metodos_pago(), key=f"pago_normal_{indice}")
                    if st.button(f"Pagar y cerrar {pedido.obtener_id()}", key=f"cerrar_normal_{indice}"):
                        pedido.registrar_pago(metodo_pago)
                        pedido.cerrar_pedido()
                        st.session_state.historial.append(pedido)
                        st.session_state.pedidos_normales.pop(indice)
                        st.rerun()

    with col_local:
        st.subheader("Mesas en consumo")

        if len(st.session_state.pedidos_local) == 0:
            st.info("No hay mesas con consumo pendiente.")
        else:
            for indice, pedido in enumerate(st.session_state.pedidos_local):
                with st.container(border=True):
                    st.write(f"### Mesa {pedido.obtener_mesa()} - {pedido.obtener_cliente()}")
                    st.caption(f"Pedido {pedido.obtener_id()} | {pedido.obtener_fecha_hora()}")
                    for item in pedido.obtener_items():
                        st.write(f"- {item.descripcion()}")
                    st.write(f"**Total actual: ${pedido.calcular_total():,.0f}**")

                    with st.expander("Agregar más productos al pedido"):
                        opciones_extra = {}
                        for codigo, producto in st.session_state.inventario.productos():
                            stock = st.session_state.inventario.obtener_stock(codigo)
                            texto_visible = f"{codigo} - {producto.obtener_nombre()} | Stock: {stock}"
                            opciones_extra[texto_visible] = codigo

                        producto_extra_visible = st.selectbox("Producto adicional", list(opciones_extra.keys()), key=f"extra_producto_{indice}")
                        codigo_extra = opciones_extra[producto_extra_visible]
                        cantidad_extra = st.number_input("Cantidad adicional", min_value=1, step=1, key=f"extra_cantidad_{indice}")

                        if st.button("Agregar al consumo", key=f"agregar_extra_{indice}"):
                            producto_extra = st.session_state.inventario.obtener_producto(codigo_extra)
                            stock_extra = st.session_state.inventario.obtener_stock(codigo_extra)
                            if stock_extra < cantidad_extra:
                                st.error("No hay stock suficiente para agregar ese producto.")
                            else:
                                st.session_state.inventario.descontar_stock(codigo_extra, cantidad_extra)
                                pedido.agregar_item(producto_extra, cantidad_extra)
                                st.success("Producto agregado al consumo local.")
                                st.rerun()

                    metodo_pago_local = st.selectbox("Método de pago", metodos_pago(), key=f"pago_local_{indice}")
                    if st.button(f"Cerrar y pagar mesa {pedido.obtener_mesa()}", key=f"cerrar_local_{indice}"):
                        pedido.registrar_pago(metodo_pago_local)
                        pedido.cerrar_pedido()
                        st.session_state.historial.append(pedido)
                        st.session_state.pedidos_local.pop(indice)
                        st.rerun()

    with col_delivery:
        st.subheader("Delivery por cerrar")

        if len(st.session_state.pedidos_delivery) == 0:
            st.info("No hay delivery pendientes.")
        else:
            for indice, pedido in enumerate(st.session_state.pedidos_delivery):
                with st.container(border=True):
                    st.write(f"### {pedido.obtener_id()} - {pedido.obtener_cliente()}")
                    st.caption(pedido.obtener_fecha_hora())
                    st.write(f"**Zona:** {pedido.obtener_zona()}")
                    st.write(f"**Dirección:** {pedido.obtener_direccion()}")
                    st.write(f"**Tarifa delivery:** ${pedido.obtener_cargo_envio():,.0f}")
                    for item in pedido.obtener_items():
                        st.write(f"- {item.descripcion()}")
                    st.write(f"**Total a pagar: ${pedido.calcular_total():,.0f}**")

                    metodo_pago_delivery = st.selectbox("Método de pago", metodos_pago(), key=f"pago_delivery_{indice}")
                    if st.button(f"Pagar y cerrar delivery {pedido.obtener_id()}", key=f"cerrar_delivery_{indice}"):
                        pedido.registrar_pago(metodo_pago_delivery)
                        pedido.cerrar_pedido()
                        st.session_state.historial.append(pedido)
                        st.session_state.pedidos_delivery.pop(indice)
                        st.rerun()

    st.divider()
    st.subheader("Cierre concurrente de pendientes")
    st.write("Cierra simultáneamente ventas normales, mesas y delivery pendientes usando hilos.")
    metodo_pago_concurrente = st.selectbox("Método de pago para cierre masivo", metodos_pago())

    if st.button("⚙️ Cerrar todos los pendientes con concurrencia"):
        pedidos_pendientes = st.session_state.pedidos_normales + st.session_state.pedidos_local + st.session_state.pedidos_delivery

        if len(pedidos_pendientes) == 0:
            st.warning("No hay pedidos pendientes para cerrar.")
        else:
            for pedido in pedidos_pendientes:
                pedido.registrar_pago(metodo_pago_concurrente)

            with st.spinner("Cerrando pedidos en paralelo con hilos..."):
                procesador = ProcesadorPedidos()
                pedidos_cerrados = procesador.procesar_pedidos_concurrentes(pedidos_pendientes)

            for pedido in pedidos_cerrados:
                st.session_state.historial.append(pedido)

            st.session_state.pedidos_normales = []
            st.session_state.pedidos_local = []
            st.session_state.pedidos_delivery = []
            st.success("Todos los pendientes fueron cerrados con concurrencia.")
            st.rerun()

# ============================================================
# TAB 3: INVENTARIO
# ============================================================

with tab_inventario:
    st.header("Inventario actualizado")
    st.write("El stock se descuenta al agregar productos a un pedido y se puede aumentar con reposición.")

    st.subheader("Reponer stock")
    opciones_repo = {}
    for codigo, producto in st.session_state.inventario.productos():
        stock = st.session_state.inventario.obtener_stock(codigo)
        texto_visible = f"{codigo} - {producto.obtener_nombre()} | Stock actual: {stock}"
        opciones_repo[texto_visible] = codigo

    producto_repo_visible = st.selectbox("Producto a reponer", list(opciones_repo.keys()))
    codigo_reposicion = opciones_repo[producto_repo_visible]
    cantidad_reposicion = st.number_input("Cantidad que llegó por reposición", min_value=1, step=1)

    if st.button("📦 Agregar reposición al inventario"):
        ok = st.session_state.inventario.reponer_stock(codigo_reposicion, cantidad_reposicion)
        if ok:
            producto = st.session_state.inventario.obtener_producto(codigo_reposicion)
            st.success(f"Reposición registrada: +{cantidad_reposicion} unidades de {producto.obtener_nombre()}.")
            st.rerun()
        else:
            st.error("No se pudo reponer el producto.")

    st.divider()
    st.subheader("Agregar nuevo producto")

    with st.expander("Crear producto nuevo en inventario"):
        nuevo_codigo = st.text_input("Código nuevo", placeholder="Ejemplo: A005")
        nuevo_nombre = st.text_input("Nombre del producto", placeholder="Ejemplo: Brownie")
        nuevo_precio = st.number_input("Precio", min_value=1, step=100)
        nuevo_stock = st.number_input("Stock inicial", min_value=1, step=1)
        nuevo_tipo = st.selectbox("Tipo de producto", ["Bebida", "Alimento"])

        if nuevo_tipo == "Bebida":
            nuevo_extra = st.number_input("Tamaño en ml", min_value=1, step=50)
        else:
            nuevo_extra = st.number_input("Calorías", min_value=1, step=50)

        if st.button("➕ Crear nuevo producto"):
            codigo_limpio = nuevo_codigo.strip().upper()
            if codigo_limpio == "" or nuevo_nombre.strip() == "":
                st.warning("Debes completar código y nombre del producto.")
            elif st.session_state.inventario.obtener_producto(codigo_limpio) is not None:
                st.error("Ya existe un producto con ese código.")
            else:
                if nuevo_tipo == "Bebida":
                    producto_nuevo = Bebida(codigo_limpio, nuevo_nombre, nuevo_precio, nuevo_extra)
                else:
                    producto_nuevo = Alimento(codigo_limpio, nuevo_nombre, nuevo_precio, nuevo_extra)
                st.session_state.inventario.agregar_producto(producto_nuevo, nuevo_stock)
                st.success("Producto nuevo agregado al inventario.")
                st.rerun()

    st.divider()
    st.subheader("Estado actual del inventario")
    for codigo, producto in st.session_state.inventario.productos():
        stock = st.session_state.inventario.obtener_stock(codigo)
        if stock <= 3:
            st.error(f"{codigo} | {producto.descripcion()} | Stock crítico: {stock}")
        elif stock <= 6:
            st.warning(f"{codigo} | {producto.descripcion()} | Stock bajo: {stock}")
        else:
            st.success(f"{codigo} | {producto.descripcion()} | Stock disponible: {stock}")

# ============================================================
# TAB 4: VENTAS, EXCEL Y COMPROBANTES
# ============================================================

with tab_resumen:
    st.header("Ventas por día, comprobantes y descarga en Excel")

    fecha_consulta = st.date_input("Selecciona fecha a revisar", value=fecha_actual, key="fecha_reporte")
    pedidos_filtrados = pedidos_por_fecha(fecha_consulta)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total vendido", f"${total_ventas_por_fecha(fecha_consulta):,.0f}")
    with col_b:
        st.metric("Pedidos cerrados", len(pedidos_filtrados))
    with col_c:
        st.metric("Productos vendidos", cantidad_productos_vendidos(fecha_consulta))

    st.divider()
    df_ventas = crear_dataframe_ventas(pedidos_filtrados)

    if len(pedidos_filtrados) == 0:
        st.info("No hay ventas registradas para la fecha seleccionada.")
    else:
        st.subheader("Detalle de ventas")
        st.dataframe(df_ventas, use_container_width=True)
        archivo_excel = convertir_excel(df_ventas)
        st.download_button(
            label="📥 Descargar ventas en Excel",
            data=archivo_excel,
            file_name=f"ventas_cafeteria_{fecha_consulta.strftime('%d_%m_%Y')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.divider()
        st.subheader("Comprobantes visuales")
        for pedido in pedidos_filtrados:
            with st.expander(f"Ver comprobante {pedido.obtener_id()} - {pedido.obtener_cliente()} - ${pedido.calcular_total():,.0f}"):
                mostrar_comprobante(pedido)

# ============================================================
# TAB 5: CIERRE DE CAJA
# ============================================================

with tab_caja:
    st.header("Cerrar caja / cerrar ventas del día")
    resumen_hoy = resumen_caja(fecha_actual)

    col_caja_1, col_caja_2, col_caja_3 = st.columns(3)
    with col_caja_1:
        st.metric("Total vendido", f"${resumen_hoy['total_vendido']:,.0f}")
    with col_caja_2:
        st.metric("Pedidos cerrados", resumen_hoy["cantidad_pedidos"])
    with col_caja_3:
        st.metric("Productos vendidos", resumen_hoy["productos_vendidos"])

    pendientes_totales = len(st.session_state.pedidos_normales) + len(st.session_state.pedidos_local) + len(st.session_state.pedidos_delivery)
    if pendientes_totales > 0:
        st.warning("Aún existen pedidos pendientes. Se recomienda pagarlos y cerrarlos antes de cerrar caja.")

    if st.session_state.caja_abierta:
        if st.button("🔒 Cerrar caja del día"):
            cierre = resumen_caja(fecha_actual)
            st.session_state.cierres_caja.append(cierre)
            st.session_state.caja_abierta = False
            st.success("Caja cerrada correctamente.")
            st.rerun()
    else:
        st.info("La caja ya se encuentra cerrada.")
        if st.button("🔓 Reabrir caja"):
            st.session_state.caja_abierta = True
            st.success("Caja reabierta correctamente.")
            st.rerun()

    st.divider()
    st.subheader("Historial de cierres de caja")
    if len(st.session_state.cierres_caja) == 0:
        st.info("Aún no se han registrado cierres de caja.")
    else:
        for cierre in st.session_state.cierres_caja:
            with st.container(border=True):
                st.write(f"**Fecha:** {cierre['fecha']}")
                st.write(f"**Hora de cierre:** {cierre['hora_cierre']}")
                st.write(f"**Total vendido:** ${cierre['total_vendido']:,.0f}")
                st.write(f"**Pedidos cerrados:** {cierre['cantidad_pedidos']}")
                st.write(f"**Productos vendidos:** {cierre['productos_vendidos']}")