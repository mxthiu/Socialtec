"""
Persistencia basada en archivos JSON.

Ey, en este módulo deberías manejar toda la comunicación con los archivos JSON.
Básicamente es la capa que se conecta con los datos que guardamos en disco. Así el
servidor no accede directamente a los archivos, sino que pasa todo por acá.

FUNCIONES QUE DEBERÍAS IMPLEMENTAR:

1. cargar_usuarios() -> dict
   Deberías cargar todos los usuarios desde datos/usuarios.json y retornar un dict
   donde la clave sea el username. Maneja bien si el archivo no existe o está vacío.

2. guardar_usuarios(usuarios_dict) -> bool
   Guarda el diccionario de usuarios en datos/usuarios.json. Retorna True si anda,
   False si hubo error. Te recomiendo que hagas esto de forma segura, quizás usa
   un archivo temporal primero y después renombra.

3. agregar_amistad(usuario1, usuario2) -> bool
   Agrega usuario2 a la lista de amigos de usuario1 y viceversa. Carga, modifica,
   guarda. Retorna True si se agregó, False si ya eran amigos o no existen.

4. eliminar_amistad(usuario1, usuario2) -> bool
   Lo inverso, elimina a usuario2 de los amigos de usuario1. Retorna True si se
   eliminó, False si no eran amigos.

5. obtener_usuario(username) -> dict o None
   Carga los usuarios y retorna el dict del usuario que buscas. Si no existe
   retorna None.

6. usuario_existe(username) -> bool
   Simple, solo verifica si existe un usuario. Retorna True/False.

COSAS IMPORTANTES:
- Acordate que todos los cambios del servidor (login, registro, amistades) tienen
  que guardarse acá. Si el servidor se cae, los datos no se pierden.
- Si vas a tener múltiples threads accediendo, usa locks para evitar problemas.
- Siempre validá que los JSON sean válidos antes de retornar datos.
"""

