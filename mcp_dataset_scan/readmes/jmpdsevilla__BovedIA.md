# BovedIA

**Memoria personal para Claude Code: tus notas en Markdown, tuyas y para siempre.**

[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple)](https://modelcontextprotocol.io)

---

## Qué es BovedIA

**BovedIA** (bóveda + IA) es un servidor MCP que le da a Claude Code —y a cualquier cliente MCP— **memoria persistente**. Tus notas viven en archivos Markdown planos, en tu disco, sincronizados en la nube si quieres. La IA puede leerlas, crearlas, buscarlas y organizarlas durante cualquier sesión de trabajo.

Pero BovedIA no es solo el motor. Es también **una forma de organizar la memoria** para que la IA llegue a cada conversación ligera y enfocada, en vez de arrastrar todo el contexto de golpe. Esa forma va incluida en el `vault-example/` de este repositorio, lista para adaptar.

---

## La idea de fondo: no cargar todo de golpe

Casi todos los sistemas de memoria vuelcan todo el contexto en cada sesión. BovedIA parte de lo contrario: **traer solo lo que el caso pide, en el momento en que lo pide**. Cargar de más no es solo trabajo desperdiciado — condiciona y ensucia la respuesta.

Para lograrlo, la bóveda se recorre por niveles (la **pirámide**):

1. **El router (`Inicio`).** La única nota que se lee siempre, al empezar cada conversación. No contiene el trabajo: contiene el criterio para decidir **qué cargar y cuándo**. Si la señal es clara, la IA actúa; si no, pregunta.
2. **Las portadas de rama.** Cada gran área (proyectos, clientes, infraestructura…) tiene una portada que el router carga solo cuando el tema entra por ahí.
3. **Las notas.** El contenido real, al que se llega desde su portada o por búsqueda.

Y una capa aparte, el **alma**: la carpeta donde se vuelca lo que uno piensa y siente — el porqué de fondo, la mentalidad, la manera de mirar el trabajo. No es documentación: es lo que hace que la memoria deje de ser un archivador y empiece a ser **continuidad**.

---

## Por qué así

- **Simple:** un solo archivo de servidor (`index.js`), una sola dependencia.
- **Tuyo:** las notas son archivos `.md` en tu disco — sin bases de datos, sin APIs externas.
- **Portátil:** funciona con iCloud, OneDrive, Google Drive, Dropbox o cualquier carpeta local.
- **Transparente:** abres y editas tus notas en cualquier editor de texto.

---

## La estructura de la bóveda: para qué sirve cada carpeta

El `vault-example/` trae una estructura de referencia lista para usar. No es una jaula: crea las categorías que tu trabajo pida. Pero enseña el método completo.

| Carpeta / archivo | Para qué sirve |
|---|---|
| `Inicio.md` | **El router.** Primera nota que se lee en cada sesión: decide qué cargar y cuándo. No carga a ciegas. |
| `HOME.md` | **El mapa.** Qué carpeta es qué y dónde va cada cosa. |
| `una-tarea-pendiente.md` | Ejemplo de **pendiente** sin fecha, en la raíz, marcado con `#pendiente`. |
| `programado/` | Notas con **fecha** de activación (`> APARECER: AAAA-MM-DD`). El router avisa cuando llega el día. |
| `sistema/` | Cómo funciona todo: la pirámide (regla madre), las portadas de rama y los protocolos de sesión. |
| `alma/` | Filosofía y mentalidad; **dónde se vuelca lo que uno piensa y siente**. Fondo, no operativa. |
| `proyectos/` | Tus proyectos propios. |
| `clientes/` | Una subcarpeta por cliente, con su perfil y contexto. |
| `conocimiento/` | Saber de oficio reutilizable, incluidos los `problemas-resueltos/`. |
| `referencias/` | Guías, técnicas y recursos que se consultan pero no cambian a menudo. |

---

## Instalación

### Opción rápida: npx

No necesitas clonar nada. Añade esto a la configuración MCP de tu cliente (Claude Code, Claude Desktop…) y copia el `vault-example/` a tu carpeta como punto de partida:

```json
{
  "mcpServers": {
    "bovedia": {
      "command": "npx",
      "args": ["-y", "bovedia"],
      "env": { "KB_MEMORY_ROOT": "/ruta/absoluta/a/tu/boveda" }
    }
  }
}
```

El resto de esta sección es la instalación manual (clonando el repo), útil si quieres modificar el código.

### Requisitos

- Node.js 18 o superior
- Claude Code (`npm install -g @anthropic-ai/claude-code`)
- Una carpeta sincronizada en la nube (iCloud, OneDrive, Google Drive, Dropbox) — o cualquier carpeta local

### 1. Clonar el repositorio

```bash
git clone https://github.com/jmpdsevilla/BovedIA.git
cd BovedIA/server
npm install
```

### 2. Crear tu bóveda

Copia la bóveda de ejemplo a tu carpeta sincronizada y personaliza `HOME.md` e `Inicio.md`:

```bash
# Mac + iCloud
cp -r vault-example ~/Library/Mobile\ Documents/com~apple~CloudDocs/mi-boveda

# Windows + OneDrive (PowerShell)
xcopy /E /I vault-example "%USERPROFILE%\OneDrive\mi-boveda"

# Linux + Dropbox
cp -r vault-example ~/Dropbox/mi-boveda
```

### 3. Configurar Claude Code

Apunta el servidor a tu bóveda con la variable `KB_MEMORY_ROOT` (acepta rutas con `~`):

```json
{
  "mcpServers": {
    "bovedia": {
      "command": "node",
      "args": ["/ruta/absoluta/a/BovedIA/server/index.js"],
      "env": {
        "KB_MEMORY_ROOT": "/ruta/absoluta/a/tu/mi-boveda"
      }
    }
  }
}
```

Si no defines `KB_MEMORY_ROOT` (ni su alias `MEMORY_PATH`), BovedIA usa `~/Documents/bovedia` por defecto.

### 4. Verificar

Reinicia Claude Code y pide leer `Inicio`, o ejecutar `get_index`. Deberías ver tu bóveda.

---

## Anotaciones de autoría (opcional)

BovedIA soporta opcionalmente [Markdown Annotations](https://github.com/iainc/Markdown-Annotations), una spec abierta originalmente de iA Writer que registra **qué autor escribió qué parte de cada nota**. Cuando se activa, las notas escritas por la IA llevan al final un bloque que atribuye el cuerpo a `&Claude`; cuando un humano edita la nota en un editor compatible, sus rangos quedan marcados como `@nombre`, y la siguiente vez que BovedIA toque la nota preserva esa autoría en vez de sobrescribirla.

**Está desactivado por defecto.** Para activarlo, añade `KB_ENABLE_ANNOTATIONS=1` al entorno del servidor:

```json
{
  "mcpServers": {
    "bovedia": {
      "command": "node",
      "args": ["/ruta/absoluta/a/BovedIA/server/index.js"],
      "env": {
        "KB_MEMORY_ROOT": "/ruta/absoluta/a/tu/mi-boveda",
        "KB_ENABLE_ANNOTATIONS": "1"
      }
    }
  }
}
```

Con la opción activa se desbloquean dos herramientas: `read_authorship` (resumen de quién escribió qué) y `migrate_annotations` (añade el bloque a todas las notas existentes; ejecútala con `dry_run: true` primero). La firma se puede personalizar con `KB_AUTHOR_NAME` y `KB_AUTHOR_EMAIL`.

Solo actívalo si usas un editor compatible con la spec: los que no la soportan mostrarán el bloque como texto plano al final del archivo.

---

## Las herramientas

38 en total. Las 36 primeras funcionan siempre. Las 2 de autoría (`read_authorship`, `migrate_annotations`) solo se exponen si arrancas el servidor con `KB_ENABLE_ANNOTATIONS=1`.

El listado de herramientas viaja en cada sesión y ocupa contexto. Si tu cliente tiene poca ventana, arranca con `KB_TOOLS=core` y se expondrán solo las 15 de uso diario (la mitad de tokens). Por defecto se exponen todas.

### Lectura y escritura base

| Herramienta | Qué hace |
|---|---|
| `write_note` | Crear o actualizar una nota (upsert completo) |
| `read_note` | Leer una nota (busca en todas las categorías) |
| `search_notes` | Buscar por texto libre (lógica AND, sin distinguir acentos) |
| `list_notes` | Listar notas, filtradas por categoría o etiqueta |
| `get_index` | Mapa de categorías (`full: true` para el detalle) |
| `delete_note` | Eliminar una nota (avisa de backlinks) |
| `create_category` | Crear una carpeta |
| `move_note` | Mover/renombrar una nota (actualiza wikilinks) |
| `delete_category` | Eliminar una carpeta vacía |

### Edición dirigida

| Herramienta | Qué hace |
|---|---|
| `edit_note` | Buscar/reemplazar dentro de una nota |
| `append_to_note` | Añadir contenido al final |
| `prepend_to_note` | Insertar contenido al principio |
| `update_section` | Reemplazar una sección por su encabezado |
| `insert_after_section` | Insertar una sección nueva tras otra |

### Mantenimiento de wikilinks y tags

| Herramienta | Qué hace |
|---|---|
| `list_broken_links` | Todos los wikilinks rotos de la bóveda |
| `find_backlinks` | Backlinks de una nota (sin cargar su contenido) |
| `find_orphans` | Notas sin backlinks ni enlaces salientes |
| `rename_wikilink` | Sustituir `[[viejo]]` por `[[nuevo]]` en toda la bóveda |
| `list_tags` | Todos los hashtags `#snake_case` con su recuento |
| `update_frontmatter` | Actualizar campos YAML sin tocar el cuerpo |

### Lecturas baratas

| Herramienta | Qué hace |
|---|---|
| `peek_note` | Frontmatter + primer párrafo |
| `read_section` | Solo una sección |
| `list_sections` | Índice de encabezados de una nota, sin su contenido |
| `read_frontmatter` | Solo el YAML |

### Mantenimiento de la bóveda

| Herramienta | Qué hace |
|---|---|
| `recently_updated` | Notas modificadas en los últimos N días |
| `move_category` | Renombrar una carpeta (actualiza el frontmatter de cada nota) |
| `validate_note` | Revisar frontmatter, hashtags, "Ver también" y enlaces rotos |
| `bulk_move` | Mover varias notas a la misma categoría |
| `due_notes` | La lista de notas programadas que ya toca sacar hoy, avisando de las que parecen ya hechas o duplicadas. Solo la lista: el contenido se lee al elegir una tarea |
| `audit_tags` | Salud de las etiquetas (y corrección de las mal formadas) |
| `prune_tags` | Fusionar variantes y recortar las notas con etiquetas de más |
| `vault_health` | Parte de salud de la bóveda en una sola llamada |
| `create_snapshot` | Copia de seguridad completa, a demanda |
| `list_snapshots` | Ver las copias disponibles |
| `restore_snapshot` | Volver a una copia anterior (simula por defecto) |
| `migrate_yaml_tags` | Bajar al cuerpo las etiquetas que quedan en el frontmatter YAML |

### Autoría (con `KB_ENABLE_ANNOTATIONS=1`)

| Herramienta | Qué hace |
|---|---|
| `read_authorship` | Resumen de qué autor escribió qué rangos |
| `migrate_annotations` | Añadir el bloque de autoría a las notas existentes |

Referencia completa en [docs/tools-reference.md](docs/tools-reference.md).

---

## Protocolo de uso

Añade esta instrucción a tu `CLAUDE.md` o a la configuración del asistente para sacarle todo el partido:

```
Al empezar cada sesión: leer Inicio (el router). Revisar la carpeta programado/
y avisar de lo que ya toca. No cargar nada más "por si acaso".
Guardar lo que merezca recordarse: credenciales, soluciones, decisiones, comandos.
Enlazar las notas con wikilinks [[slug]]. Cada nota termina con una sección
"Ver también" con 2-5 wikilinks.
```

---

## Wikilinks

Las notas se enlazan entre sí con el formato `[[slug]]`:

```markdown
## Ver también

- [[proyecto-ejemplo]] — proyecto donde se usa esto
- [[cliente-ejemplo]] — cliente al que pertenece
```

Reglas:

- Usa el slug del nombre de archivo (kebab-case, sin `.md`).
- Sin rutas: ~~`[[referencias/x]]`~~ → `[[x]]`.
- Sin alias: ~~`[[x|otro texto]]`~~ → `[[x]]`.

Cuando una nota se renombra, sus wikilinks se actualizan automáticamente.

---

## Guías de instalación detalladas

- [Mac + iCloud Drive](docs/mac-icloud.md)
- [Windows + OneDrive / Google Drive](docs/windows.md)
- [Linux + Dropbox / Google Drive](docs/linux.md)

---

## Autor

Creado por **José Manuel Pérez**, fundador de [santa marta crea](https://santamartacrea.com) — agencia digital. Santa Marta, Colombia.

- Web: [santamartacrea.com](https://santamartacrea.com)
- GitHub: [@jmpdsevilla](https://github.com/jmpdsevilla)

---

## Licencia

[MIT](LICENSE) — libre para usar, modificar y distribuir.
