from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, jsonify, g, abort, request, make_response, session
from flask_wtf.csrf import CSRFProtect

from models import initialize, Usuario, Inventario, Categoria, Producto, Lote, Proveedor, DATABASE

app = Flask(__name__)
app.secret_key = 'my_secret_key'
#csfr = CSRFProtect(app)
PORT = 8000
DEBUG = True

@app.before_request
def before_request():
    g.db = DATABASE
    g.db.connect()

@app.after_request
def after_request(request):
    g.db.close()
    return request

#Seccion de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify( generate_response(404, error = 'Dato no encontrado') )

@app.errorhandler(400)
def bad_request(error):
    return jsonify( generate_response(400, error = 'Necesitas parametros') )

@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify( generate_response(422, error = 'Datos incorrectos') )

@app.errorhandler(406)
def not_acceptable(error):
    return jsonify( generate_response(406, error = 'Dato ya existe') )

#Funciones generales
def generate_response(status = 200, data = None, error = None):
    return {'status': status, 'data': data, 'error': error}

@app.route('/')
def index():
    custome_cookie = request.cookies.get('custome_cookies', 'Undefined')
    print (custome_cookie)
    return '<h1>Deployed!<h1>'

@app.route('/cookie')
def cookie():
    response = make_response( '<h1>Cookie</h1>')
    response.set_cookie('custome_cookie', 'Chachi')
    return response

#Seccion de Tabla Usuario
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.select()
    usuarios = [ Usuario.to_json() for Usuario in usuarios ]
    identificador = Usuario.select()
    identificador = [ Usuario.iden() for Usuario in identificador ]

    diccionario = {}
    for x in range(len(usuarios)):
        diccionario[identificador[x]] = usuarios[x]

    return jsonify( diccionario )

@app.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
def get_usuario(usuario_id):
    try:
        usuario = Usuario.get(Usuario.id == usuario_id)
        return jsonify( usuario.to_json() )
    except Usuario.DoesNotExist:
        abort(404)

@app.route('/api/usuarios', methods=['POST'])
def post_usuario():
    if not request.json:
        abort(400)

    usuario = request.json.get('usuario')
    contrasena = request.json.get('contrasena')
    nombre = request.json.get('nombre')
    descripcion = request.json.get('descripcion')
    administrador = request.json.get('administrador')

    if (administrador.isdigit() == False):
        return jsonify( generate_response(1, error = 'Administrador tiene que ser numerico') )

    #Encripta la contraseña
    password = generate_password_hash(str(contrasena))

    usuario = Usuario.new(usuario, password, nombre, descripcion, administrador)

    if usuario is None:
        abort(422)

    if usuario == "error":
        abort(406)

    return jsonify( usuario.to_json() )

@app.route('/api/login', methods=['POST'])
def login():
    usuario = request.json['usuario']
    password = request.json['contrasena']
    try:
        contra = Usuario.get(Usuario.usuario == usuario)
        ident = contra.iden()
        contra = contra.pa()
        if check_password_hash(contra, password):
            session['id'] = ident
            return jsonify({'message': 'OK'})  # You'll want to return a token that verifies the user in the future
        return jsonify({'error': 'KO'})
    except Usuario.DoesNotExist:
        return jsonify({'error': 'KO'})

@app.route('/api/logout')
def logout():
    if 'id' in session:
        session.pop('id')
    return jsonify({'message': 'OK'})

@app.route('/api/usuarios/<int:usuario_id>', methods=['PUT'])
def put_usuario(usuario_id):
    try:
        usuario = Usuario.get(Usuario.id == usuario_id)
        contrasena = request.json.get('contrasena'  )
        password = generate_password_hash(str(contrasena))
        administrador = request.json.get('administrador')
        if (administrador.isdigit() == False):
            return jsonify( generate_response(1, error = 'Administrador tiene que ser numerico') )

        usuario.usuario = request.json.get('usuario', usuario.usuario)
        usuario.contrasena = password
        usuario.nombre = request.json.get('nombre', usuario.nombre)
        usuario.descripcion = request.json.get('descripcion', usuario.descripcion)
        usuario.administrador = administrador

        if usuario.save():
            return jsonify( usuario.to_json() )
    except Usuario.DoesNotExist:
        abort(404)

#Seccion de Tabla Inventario
@app.route('/api/inventarios', methods=['GET'])
def get_inventarios():
    if 'id' in session:
        id = session['id']
        inventarios = Inventario.select().where(Inventario.usuario == id)
        inventarios = [ Inventario.to_json( Usuario.get( Usuario.id == Inventario.usuario ).to_json() ) for Inventario in inventarios ]
        identificador = Inventario.select()
        identificador = [ Inventario.iden() for Inventario in identificador ]

        diccionario = {}
        for x in range(len(inventarios)):
            diccionario[identificador[x]] = inventarios[x]

        return jsonify( diccionario )

    return jsonify({'message': 'KO'} )


@app.route('/api/inventarios/<int:inventario_id>', methods=['GET'])
def get_inventario(inventario_id):
    if 'id' in session:
        id = session['id']
        try:
            inventario = Inventario.get((Inventario.id == inventario_id) & (Inventario.usuario == id))
            usuario = Usuario.get(Usuario.id == inventario.usuario)
            return jsonify( inventario.to_json( usuario.to_json() ) )
        except Inventario.DoesNotExist:
            abort(404)
    return jsonify({'message': 'KO'} )

@app.route('/api/inventarios', methods=['POST'])
def post_inventario():
    if 'id' in session:
        id = session['id']
        if not request.json:
            abort(400)

        nombre = request.json.get('nombre')
        usuario = request.json.get('usuario')

        inventario = Inventario.new(nombre, usuario)

        if inventario is None:
            abort(422)

        if inventario == "error":
            abort(406)

        usuario = Usuario.get(Usuario.id == inventario.usuario)
        return jsonify( inventario.to_json( usuario.to_json() ) )
    return jsonify({'message': 'KO'} )

@app.route('/api/inventarios/<int:inventario_id>', methods=['PUT'])
def put_inventario(inventario_id):
    if 'id' in session:
        id = session['id']
        try:
            inventario = Inventario.get((Inventario.id == inventario_id) & (Inventario.usuario == id))
            inventario.nombre = request.json.get('nombre', inventario.nombre)
            inventario.usuario = request.json.get('usuario', inventario.usuario)
            if inventario.save():
                usuario = Usuario.get(Usuario.id == inventario.usuario)
                return jsonify( inventario.to_json( usuario.to_json() ) )
            else:
                abort(422)
        except Inventario.DoesNotExist:
            abort(404)

#Seccion de Categoria
@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    if 'id' in session:
        id = session['id']
        categorias = Categoria.select().join(Inventario).where(Inventario.usuario == id)
        categorias = [ Categoria.to_json( Inventario.get( Inventario.id == Categoria.inventario ).add_ok() ) for Categoria in categorias ]
        identificador = Categoria.select().join(Inventario).where(Inventario.usuario == id)
        identificador = [ Categoria.iden() for Categoria in identificador ]

        diccionario = {}
        for x in range(len(categorias)):
            diccionario[identificador[x]] = categorias[x]

        return jsonify( diccionario )
    return jsonify({'message': 'KO'} )

@app.route('/api/categorias/<int:categoria_id>', methods=['GET'])
def get_categoria(categoria_id):
    if 'id' in session:
        id = session['id']
        try:
            categoria = Categoria.get(Categoria.id == categoria_id)
            inventario = Inventario.get((Inventario.id == categoria.inventario)&(Inventario.usuario == id))
            return jsonify( categoria.to_json( inventario.add_ok() ) )
        except Categoria.DoesNotExist:
            abort(404)
        except Inventario.DoesNotExist:
            abort(404)
    return jsonify({'message': 'KO'} )

@app.route('/api/categorias', methods=['POST'])
def post_categoria():
    if 'id' in session:
        id = session['id']
        if not request.json:
            abort(400)

        nombre = request.json.get('nombre')
        descripcion = request.json.get('descripcion')
        inventario = request.json.get('inventario')

        categoria = Categoria.new(nombre, descripcion, inventario)

        if categoria is None:
            abort(422)

        if categoria == "error":
            abort(406)

        inventario = Inventario.get(Inventario.id == categoria.inventario)
        return jsonify( categoria.to_json( inventario.add_ok() ) )
    return jsonify({'message': 'KO'} )

@app.route('/api/categorias/<int:categoria_id>', methods=['PUT'])
def put_categoria(categoria_id):
    if 'id' in session:
        id = session['id']
        try:
            categoria = Categoria.get(Categoria.id == categoria_id)
            inventario = Inventario.get((Inventario.id == categoria.inventario)&(Inventario.usuario == id))

            categoria.nombre = request.json.get('nombre', categoria.nombre)
            categoria.descripcion = request.json.get('descripcion', categoria.descripcion)
            categoria.inventario = request.json.get('inventario', categoria.inventario)

            if categoria.save():
                inventario = Inventario.get(Inventario.id == categoria.inventario)
                return jsonify( categoria.to_json( inventario.add_ok() ) )
            else:
                abort(422)

        except Categoria.DoesNotExist:
            abort(404)
        except Inventario.DoesNotExist:
            abort(404)
    return jsonify({'message': 'KO'} )
#Seccion de tabla Proveedor
@app.route('/api/proveedores', methods=['GET'])
def get_proveedores():
    if 'id' in session:
        id = session['id']
        proveedores = Proveedor.select()
        proveedores = [ Proveedor.to_json() for Proveedor in proveedores ]
        identificador = Proveedor.select()
        identificador = [ Proveedor.iden() for Proveedor in identificador ]

        diccionario = {}
        for x in range(len(proveedores)):
            diccionario[identificador[x]] = proveedores[x]

        return jsonify( diccionario )
    return jsonify({'message': 'KO'} )

@app.route('/api/proveedores/<int:proveedor_id>', methods=['GET'])
def get_proveedor(proveedor_id):
    if 'id' in session:
        id = session['id']
        try:
            proveedor = Proveedor.get(Proveedor.id == proveedor_id)
            return jsonify( proveedor.to_json() )
        except Proveedor.DoesNotExist:
            abort(404)
    return jsonify({'message': 'KO'} )

@app.route('/api/proveedores', methods=['POST'])
def post_proveedor():
    if 'id' in session:
        id = session['id']
        if not request.json:
            abort(400)

        nombre = request.json.get('nombre')
        descripcion = request.json.get('descripcion')

        proveedor = Proveedor.new(nombre, descripcion)

        if proveedor is None:
            abort(422)

        if proveedor == "error":
            abort(406)

        return jsonify( proveedor.to_json() )
    return jsonify({'message': 'KO'} )

@app.route('/api/proveedores/<int:proveedor_id>', methods =['PUT'])
def put_proveedor(proveedor_id):
    if 'id' in session:
        id = session['id']
        proveedor = Proveedor.get(Proveedor.id == proveedor_id)

        proveedor.nombre = request.json.get('nombre', proveedor.nombre)
        proveedor.descripcion = request.json.get('descripcion', proveedor.descripcion)

        if proveedor.save():
            return jsonify( proveedor.to_json() )
        else:
            abort(422)
    return jsonify({'message': 'KO'} )

@app.route('/api/proveedores/<int:proveedor_id>', methods =  ['DELETE'])
def delete_proveedor(proveedor_id):
    if 'id' in session:
        id = session['id']
        try:
            proveedor = Proveedor.get(Proveedor.id == proveedor_id)
            producto = Producto.select().where(Producto.proveedor == proveedor_id)
            for Producto in producto:
                producto.delete_instance()
            proveedor.delete_instance()
            return jsonify({'message': 'OK'})
        except Proveedor.DoesNotExist:
            abort(404)
    return jsonify({'message': 'KO'} )

#Seccion de productos
@app.route('/api/productos', methods =['GET'])
def get_productos():
    if 'id' in session:
        id = session['id']
        productos = Producto.select().join(Categoria).join(Inventario).where(Inventario.usuario == id)
        productos = [ Producto.to_json( Categoria.get( Categoria.id == Producto.categoria ).add_ok(), Proveedor.get( Proveedor.id == Producto.proveedor ).to_json() ) for Producto in productos ]
        identificador = Producto.select().join(Categoria).join(Inventario).where(Inventario.usuario == id)
        identificador = [ Producto.iden() for Producto in identificador ]

        diccionario = {}
        for x in range(len(productos)):
            diccionario[identificador[x]] = productos[x]

        return jsonify( diccionario )
    return jsonify({'message': 'KO'} )

@app.route('/api/productos/<int:producto_id>', methods=['GET'])
def get_producto(producto_id):
    if 'id' in session:
        id = session['id']
        try:
            producto = Producto.get(Producto.id == producto_id)
            categoria = Categoria.get(Categoria.id == producto.categoria)
            inventario = Inventario.get((Inventario.id == categoria.inventario)&(Inventario.usuario == id))
            proveedor = Proveedor.get(Proveedor.id == producto.proveedor)
            return jsonify( producto.to_json( categoria.add_ok(), proveedor.to_json() ) )
        except Producto.DoesNotExist:
            abort(404)
        except Inventario.DoesNotExist:
            abort(404)
    return jsonify({'message': 'KO'} )

@app.route('/api/productos', methods=['POST'])
def post_producto():
    if 'id' in session:
        id = session['id']
        if not request.json:
            abort(400)

        nombre = request.json.get('nombre')
        descripcion = request.json.get('descripcion')
        categoria = request.json.get('categoria')
        proveedor = request.json.get('proveedor')

        producto = Producto.new(nombre, descripcion, categoria, proveedor)

        if producto is None:
            abort(422)

        if producto == "error":
            abort(406)

        categoria = Categoria.get(Categoria.id == producto.categoria)
        proveedor = Proveedor.get(Proveedor.id == producto.proveedor)
        return jsonify( producto.to_json( categoria.add_ok(), proveedor.to_json() ) )
    return jsonify({'message': 'KO'} )

@app.route('/api/productos/<int:producto_id>', methods=['PUT'])
def put_producto(producto_id):
    if 'id' in session:
        id = session['id']
        try:
            producto = Producto.get(Producto.id == producto_id)
            categoria = Categoria.get(Categoria.id == producto.categoria)
            inventario = Inventario.get((Inventario.id == categoria.inventario)&(Inventario.usuario == id))
            proveedor = Proveedor.get(Proveedor.id == producto.proveedor)
            producto.nombre = request.json.get('nombre', producto.nombre)
            producto.descripcion = request.json.get('descripcion', producto.descripcion)
            producto.categoria = request.json.get('categoria', producto.categoria)
            producto.proveedor = request.json.get('proveedor', producto.proveedor)

            if producto.save():
                return jsonify( producto.to_json( categoria.add_ok(), proveedor.to_json() ) )
            else:
                abort(422)
        except Producto.DoesNotExist:
            abort(404)
        except Inventario.DoesNotExist:
            abort(404)
    return jsonify({'message': 'KO'} )

#Seccion de la tabla lote
@app.route('/api/lotes', methods =['GET'])
def get_lotes():
    if 'id' in session:
        id = session['id']
        lotes = Lote.select().join(Producto).join(Categoria).join(Inventario).where(Inventario.usuario == id)
        lotes = [ Lote.to_json( Producto.get( Producto.id == Lote.producto ).add_ok() ) for Lote in lotes ]
        identificador = Lote.select().join(Producto).join(Categoria).join(Inventario).where(Inventario.usuario == id)
        identificador = [ Lote.iden() for Lote in identificador ]

        diccionario = {}
        for x in range(len(lotes)):
            diccionario[identificador[x]] = lotes[x]

        return jsonify( diccionario )
    return jsonify({'message': 'KO'} )

@app.route('/api/lotes/<int:lote_id>', methods=['GET'])
def get_lote(lote_id):
    if 'id' in session:
        id = session['id']
        try:
            lote = Lote.get(Lote.id == lote_id)
            producto = Producto.get( Producto.id == lote.producto )
            categoria = Categoria.get(Categoria.id == producto.categoria)
            inventario = Inventario.get((Inventario.id == categoria.inventario)&(Inventario.usuario == id))
            return jsonify( lote.to_json( producto.add_ok() ) )
        except Lote.DoesNotExist:
            abort(404)
        except Inventario.DoesNotExist:
            abort(404)
    return jsonify({'message': 'KO'} )

@app.route('/api/lotes', methods=['POST'])
def post_lote():
    if 'id' in session:
        id = session['id']
        if not request.json:
            abort(400)
        costo = request.json.get('costo')
        precio = request.json.get('precio')
        existencia = request.json.get('existencia')
        producto = request.json.get('producto')

        if (costo.isdigit() == False):
            return jsonify( generate_response(1, error = 'Costo tiene que ser numerico') )

        if (precio.isdigit() == False):
            return jsonify( generate_response(1, error = 'Precio tiene que ser numerico') )

        if (existencia.isdigit() == False):
            return jsonify( generate_response(1, error = 'Existencia tiene que ser numerico') )

        lote = Lote.new(costo, precio, existencia, producto)

        if lote is None:
            abort(422)

        producto = Producto.get( Producto.id == lote.producto )
        return jsonify( lote.to_json( producto.add_ok() ) )
    return jsonify({'message': 'KO'} )

@app.route('/api/lotes/<int:lote_id>', methods=['PUT'])
def put_lote(lote_id):
    if 'id' in session:
        id = session['id']
        try:
            lote = Lote.get(Lote.id == lote_id)
            producto = Producto.get( Producto.id == lote.producto )
            categoria = Categoria.get(Categoria.id == producto.categoria)
            inventario = Inventario.get((Inventario.id == categoria.inventario)&(Inventario.usuario == id))

            lote.costo = request.json.get('costo', lote.costo)
            lote.precio = request.json.get('precio', lote.precio)
            lote.existencia = request.json.get('existencia', lote.existencia)
            lote.producto = request.json.get('producto', lote.producto)

            if lote.save():

                return jsonify( lote.to_json( producto.add_ok() ) )
            else:
                abort(422)
        except Lote.DoesNotExist:
            abort(404)
        except Inventario.DoesNotExist:
            abort(404)
    return jsonify({'message': 'KO'} )

@app.route('/api/lotes/<int:lote_id>', methods=['DELETE'])
def delete_lote(lote_id):
    if 'id' in session:
        id = session['id']
        try:
            lote = Lote.get(Lote.id == lote_id)
            producto = Producto.get( Producto.id == lote.producto )
            categoria = Categoria.get(Categoria.id == producto.categoria)
            inventario = Inventario.get((Inventario.id == categoria.inventario)&(Inventario.usuario == id))
            lote.delete_instance()
            return jsonify({'message': 'OK'})
        except Lote.DoesNotExist:
            abort(404)
        except Inventario.DoesNotExist:
            abort(404)
    return jsonify({'message': 'KO'} )

if __name__ == '__main__':
    initialize()
    app.run(port=PORT, debug = DEBUG)
