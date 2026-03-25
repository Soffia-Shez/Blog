# Blog
Atroblog que permite a los usuarios registrarse, autenticarse y gestionar contenido interactivo. 

**📌 Descripción:**<br>
El sistema implementa control de sesiones mediante Flask-Login, almacenamiento en SQLite y funcionalidades sociales como publicación de posts, comentarios y sistema de likes. Además, incluye control de acceso, validación de datos y relaciones entre entidades, simulando el comportamiento básico de una red social.
<br>

**🔧 Tecnologías:** Python, Flask, SQLite, Flask-Login, HTML, CSS, Jinja2, Werkzeug Security.
<br>

**📝 Funciones:** <br>
<ul>
  <li>Encriptación de contraseñas.</li>
  <li>Gestión de bases de datos.</li>
  <li>Carga dinámica de usuarios.</li>
  <li>Control de permisos.</li>
  <li>Consultas SQL complejas (uso de JOIN y GROUP BY para combinar usuarios, posts y conteo de likes).</li>
  <li>Validación de formularios.</li>
  <li>Eliminación en cascada manual.</li>
  <li>Renderizado dinámico de contenido.</li>
  <li>Control de usuarios autenticados mediante current_user y rutas protegidas con login_required.</li>
  <li>Modelo de usuario personalizado.</li>
</ul>
<br>

**📊 Arquitectura del sistema:**<br>
Fronted (interfaces HTML renderizadas con Jinja2 y formularios para interacción), backend (manejo de rutas y lógica de negocio y control de autenticación y permisos) y bases de datos (relaciones entre entidades mediante claves foráneas).
