from peewee import *
import datetime

DATABASE = MySQLDatabase('inventarios', host='localhost', user='root', passwd='123456789')

class Usuario(Model):
    class Meta:
        database = DATABASE
        db_table = 'usuario'

    #Se  definen los campos de la tabla
    usuario = CharField(max_length=100)
    contrasena = CharField(max_length=255)
    nombre = CharField(max_length=255)
    descripcion = CharField(max_length=255)
    administrador = SmallIntegerField()

    #Funcion que especifica el fomato de salida
    def to_json(self):
        return {'id': self.id, 'usuario':self.usuario, 'contraseña': self.contrasena, 'nombre': self.nombre, 'descripcion': self.descripcion, 'administrador': self.administrador }

    #Funcion que devuelve solo el campo contraseña
    def pa(self) :
        return self.contrasena
        
    #Clase que se utiliza para crear un nuevo registro en la base de Datos
    @classmethod
    def new(cls, usuario, contrasena, nombre, descripcion, administrador):
        try:
            #Si el registro ya existe no crea uno nuevo
            if not Usuario.select().where(Usuario.usuario == usuario):
                return cls.create(usuario = usuario, contrasena = contrasena, nombre = nombre, descripcion = descripcion, administrador = administrador)
            else:
                return "error"
        except IntegrityError:
            return None

class Inventario(Model):
    class Meta:
        database = DATABASE
        db_table = 'inventario'
    #Se definen los campos de la tabla
    nombre = CharField(max_length=50)
    usuario = ForeignKeyField(Usuario)
    #Funcion que especifica el formato de salida
    def to_json(self, usr):
        return {'id': self.id, 'nombre': self.nombre, 'usuario': usr}
    #Funcion que solo retorna los datos para indicar que fueron ingresados correctamente
    def add_ok(self):
        return {'id':self.id, 'nombre':self.nombre, 'usuario':self.usuario_id}
    #Clase que se utiliza para crear un nuevo registro en la base de datos
    @classmethod
    def new(cls, nombre, usr):
        try:
            #Si el registro ya existe no crea uno nuevo
            if not Inventario.select().where(Inventario.nombre == nombre):
                return cls.create(nombre = nombre, usuario = usr)
            else:
                return "error"
        except IntegrityError:
            return None

class Categoria(Model):
    class Meta:
        database = DATABASE
        db_table = 'categoria'
    #Se definen los campos de la tabla
    nombre = CharField(max_length=100)
    descripcion = CharField(max_length=255)
    inventario = ForeignKeyField(Inventario)
    #Funcion que especifica el fomato de salida
    def to_json(self, inv):
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion, 'inventario':inv}
    #Funcon que solo retorna los datos para indicar que fueron ingresados correctamente
    def add_ok(self):
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion, 'inventario':self.inventario_id}
    #Clase que se utiliza para crear un nuevo registro en la base de datos
    @classmethod
    def new(cls, nombre, descripcion, inventario):
        try:
            #Si el registro ya existe no crea uno nuevo
            if not Categoria.select().where(Categoria.nombre == nombre):
                return cls.create(nombre = nombre, descripcion = descripcion, inventario = inventario)
            else:
                return "error"
        except IntegrityError:
            return None

class Proveedor(Model):
    class Meta:
        database = DATABASE
        db_table = 'proveedor'
    #Se definen los campos de la tabla
    nombre = CharField(max_length=100)
    descripcion = CharField(max_length=255)
    #Funcion que especifica el fomato de salida
    def to_json(self):
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion}
    #Clase que se utiliza para crear un nuevo registro en la base de datos
    @classmethod
    def new(cls, nombre, descripcion):
        try:
            #Si el registro ya existe no crea uno nuevo
            if not Proveedor.select().where(Proveedor.nombre == nombre):
                return cls.create(nombre = nombre, descripcion = descripcion)
            else:
                return "error"
        except IntegrityError:
            return None

class Producto(Model):
    class Meta:
        database = DATABASE
        db_table = 'producto'
    #Se definen los campos de la tabla
    nombre = CharField(max_length=100)
    descripcion = CharField(max_length=255)
    categoria = ForeignKeyField(Categoria)
    proveedor = ForeignKeyField(Proveedor)
    #Funcion que especifica el formato de salida
    def to_json(self, cat, prov):
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion, 'categoria': cat, 'proveedor': prov}
    #Funcion que solo returna los datos para indicar que fueron ingresados correctamente
    def add_ok(self):
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion, 'categoria': self.categoria_id, 'proveedor': self.proveedor_id}
    #Clase que se utiliza para crear un nuevo registro en la base de datos
    @classmethod
    def new(cls, nombre, descripcion, categoria, proveedor):
        try:
            #Si el registro ya existe no crea uno nuevo
            if not Producto.select().where(Producto.nombre == nombre):
                return cls.create(nombre = nombre, descripcion = descripcion, categoria = categoria, proveedor = proveedor)
            else:
                return "error"
        except IntegrityError:
            return None

class Lote(Model):
    class Meta:
        database = DATABASE
        db_table = 'lote'
    #Se definen los campos de la tabla
    costo = FloatField()
    precio = FloatField()
    existencia = IntegerField()
    producto = ForeignKeyField(Producto)
    #Funcion que especifica el formato de salida
    def to_json(self, prod):
        return {'id': self.id, 'costo': self.costo, 'precio':self.precio, 'existencia': self.existencia, 'producto':prod}
    #Funcion que solo returna los datos para indicar que fueron ingresados correctamente
    def add_ok(self):
        return {'id': self.id, 'costo': self.costo, 'precio':self.precio, 'existencia': self.existencia, 'producto':self.producto_id}
    #Clase que se utiliza para crear un nuevo registro en la base de datos
    @classmethod
    def new(cls, costo, precio, existencia, producto):
        try:
            return cls.create(costo = costo, precio = precio, existencia = existencia, producto = producto)
        except IntegrityError:
            return None

def initialize():
    DATABASE.connect()
    DATABASE.close()
