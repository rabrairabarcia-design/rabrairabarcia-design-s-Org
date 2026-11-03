# Familia Revit: Mesa rectangular paramétrica (pyRevit)

Extensión de pyRevit para **Revit 2027** que genera automáticamente una
familia `.rfa` de mesa rectangular con 4 patas.

## Qué genera

| Elemento | Detalle |
|---|---|
| Categoría | Mobiliario (plantilla métrica de mobiliario, no basada en anfitrión) |
| Origen | Centro de la mesa en planta, a nivel del suelo |
| Geometría | Tablero (1 extrusión) + 4 patas cuadradas (4 extrusiones) |
| Planos de referencia | `Ref_Izquierda`, `Ref_Derecha`, `Ref_Frontal`, `Ref_Trasera`, `Ref_Pata_*_Ext/Int` y los planos centrales de la plantilla |
| Restricciones | Caras laterales bloqueadas a planos; alturas asociadas a parámetros |
| Tipos | `Mesa 1600x800` y `Mesa 1200x600` |

### Parámetros

| Parámetro | Tipo / Ejemplar | Valor inicial | Fórmula |
|---|---|---|---|
| Ancho | Tipo – Longitud | 1600 mm | |
| Profundidad | Tipo – Longitud | 800 mm | |
| Altura | Tipo – Longitud | 750 mm | |
| Espesor_Tablero | Tipo – Longitud | 30 mm | |
| Lado_Pata | Tipo – Longitud | 60 mm | |
| Retranqueo_Patas | Tipo – Longitud | 50 mm | |
| Altura_Patas | Tipo – Longitud | 720 mm | `Altura - Espesor_Tablero` |
| Material_Tablero | Tipo – Material | (vacío) | |
| Material_Patas | Tipo – Material | (vacío) | |

Las medidas son **valores iniciales supuestos**, no de un fabricante. Se
editan desde *Tipos de familia* o en la sección `CONFIGURACION` de
`script.py`.

## Instalación

1. Copia la carpeta `MesaFamilia.extension` en tu PC, por ejemplo en
   `C:\pyRevitExtensions\`.
2. En Revit: pestaña **pyRevit → Settings → Custom Extension Directories**,
   añade `C:\pyRevitExtensions` y guarda.
3. Pulsa **pyRevit → Reload**. Aparecerá la pestaña **MesaFamilia** con el
   botón **Crear Mesa**.

Necesitas una versión de pyRevit compatible con Revit 2027.

## Uso

1. Pulsa **Crear Mesa** (funciona con un proyecto abierto o sin él).
2. Elige la plantilla de mobiliario si el script no la encuentra
   automáticamente (`Metric Furniture.rft` / `Mobiliario métrico.rft`).
3. Elige dónde guardar el `.rfa`.
4. El script construye la familia, ejecuta una **prueba de flexión**
   (800×500×450, 1600×800×750 y 3000×1200×1100 mm) y muestra el resultado
   en la ventana de salida de pyRevit.
5. Opcional: cargar la familia en el proyecto activo y/o abrirla en el
   Editor de familias.

## Estado de las pruebas

El código **no se ha ejecutado en Revit** (se escribió en un entorno sin
Revit). Comprobaciones pendientes en tu equipo:

- [ ] El botón aparece y el script se ejecuta sin errores.
- [ ] La prueba de flexión de la ventana de salida da `OK` en las 3 filas.
- [ ] En el Editor de familias: cambiar Ancho, Profundidad y Altura en
      *Tipos de familia* actualiza tablero y patas.
- [ ] Cambiar `Lado_Pata` y `Retranqueo_Patas` mueve las patas correctamente.
- [ ] Asignar materiales y comprobarlos en 3D sombreado/realista.
- [ ] Planta, alzados y 3D coherentes.
- [ ] Cargar en un proyecto, colocar ambos tipos y verlos en una tabla de
      planificación de Mobiliario.

Si algo falla, copia el mensaje de error de la ventana de salida de pyRevit.

## Limitaciones y posibles mejoras

- Sin niveles de detalle ni representación simbólica en planta.
- Sin subcategorías (Tablero / Patas).
- Sin parámetros de identidad (fabricante, modelo, coste…) ni compartidos.
- Patas solo cuadradas; se podrían añadir patas redondas o un faldón
  mediante parámetros Sí/No.
