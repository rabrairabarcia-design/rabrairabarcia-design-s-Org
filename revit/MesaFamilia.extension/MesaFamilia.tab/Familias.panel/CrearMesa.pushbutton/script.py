# -*- coding: utf-8 -*-
"""Crea una familia parametrica de mesa rectangular (categoria Mobiliario).

Genera un documento de familia nuevo a partir de la plantilla de mobiliario,
crea planos de referencia, parametros, cotas etiquetadas, tablero y 4 patas
bloqueados a los planos, dos tipos de catalogo, ejecuta una prueba de
flexion y guarda el .rfa en la ruta que elija el usuario.

Compatible con IronPython 2.7/3.4 y CPython (sin f-strings).
"""

__title__ = "Crear\nMesa"
__author__ = "Claude Code"

import os

from Autodesk.Revit.DB import (
    BuiltInParameter,
    CurveArray,
    CurveArrArray,
    Extrusion,
    FilteredElementCollector,
    GroupTypeId,
    Line,
    Options,
    Plane,
    PlanarFace,
    ReferenceArray,
    ReferencePlane,
    SaveAsOptions,
    SketchPlane,
    Solid,
    SpecTypeId,
    Transaction,
    UnitTypeId,
    UnitUtils,
    ViewPlan,
    ViewType,
    XYZ,
)

from pyrevit import forms, script

output = script.get_output()
uiapp = __revit__  # noqa: F821  (variable inyectada por pyRevit)
app = uiapp.Application

# ---------------------------------------------------------------------------
# CONFIGURACION (mm). Todo queda como parametro editable en la familia.
# ---------------------------------------------------------------------------
NOMBRE_FAMILIA = "Mesa_Rectangular_Parametrica"

TIPOS = [
    # (nombre de tipo, ancho, profundidad, altura)
    ("Mesa 1600x800", 1600.0, 800.0, 750.0),
    ("Mesa 1200x600", 1200.0, 600.0, 750.0),
]

ESPESOR_TABLERO = 30.0
LADO_PATA = 60.0
RETRANQUEO_PATAS = 50.0

# Nombres de parametros (sin tildes para evitar problemas en formulas)
P_ANCHO = "Ancho"
P_PROF = "Profundidad"
P_ALTURA = "Altura"
P_ESPESOR = "Espesor_Tablero"
P_LADO_PATA = "Lado_Pata"
P_RETRANQUEO = "Retranqueo_Patas"
P_ALT_PATAS = "Altura_Patas"
P_MAT_TABLERO = "Material_Tablero"
P_MAT_PATAS = "Material_Patas"

# Pruebas de flexion: (ancho, profundidad, altura) en mm
PRUEBAS_FLEXION = [
    (800.0, 500.0, 450.0),     # minima razonable
    (1600.0, 800.0, 750.0),    # habitual
    (3000.0, 1200.0, 1100.0),  # maxima razonable (mesa alta)
]

TOL = 1e-6


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def mm(valor):
    """mm -> unidades internas (pies)."""
    return UnitUtils.ConvertToInternalUnits(valor, UnitTypeId.Millimeters)


def a_mm(valor):
    """unidades internas (pies) -> mm."""
    return UnitUtils.ConvertFromInternalUnits(valor, UnitTypeId.Millimeters)


def buscar_plantilla():
    """Busca la plantilla de mobiliario metrica; si no la encuentra, pregunta."""
    raiz = app.FamilyTemplatePath
    candidatos = []
    if raiz and os.path.isdir(raiz):
        for carpeta, _, archivos in os.walk(raiz):
            for nombre in archivos:
                n = nombre.lower()
                if not n.endswith(".rft"):
                    continue
                es_mobiliario = ("furniture" in n) or ("mobiliario" in n)
                es_sistema = ("system" in n) or ("sistema" in n)
                # "metric" (EN) / "metrico" o "métrico" (ES) contienen "tric"
                es_metrica = "tric" in n
                if es_mobiliario and not es_sistema:
                    candidatos.append((0 if es_metrica else 1,
                                       os.path.join(carpeta, nombre)))
    if len(candidatos) == 1:
        return candidatos[0][1]
    if len(candidatos) > 1:
        candidatos.sort()
        opciones = [c[1] for c in candidatos]
        elegida = forms.SelectFromList.show(
            opciones,
            title="Elige la plantilla de Mobiliario",
            multiselect=False,
        )
        if elegida:
            return elegida
    return forms.pick_file(
        file_ext="rft",
        init_dir=raiz if raiz and os.path.isdir(raiz) else None,
        title="Selecciona la plantilla de familia de Mobiliario (.rft)",
    )


def vista_planta(fdoc):
    for v in FilteredElementCollector(fdoc).OfClass(ViewPlan):
        if not v.IsTemplate and v.ViewType == ViewType.FloorPlan:
            return v
    raise Exception("La plantilla no contiene una vista de planta.")


def planos_centrales(fdoc):
    """Devuelve (plano eje X=0, plano eje Y=0) de la plantilla, si existen."""
    centro_x = None  # plano de normal X que pasa por x=0 (Centro Izq/Der)
    centro_y = None  # plano de normal Y que pasa por y=0 (Centro Frontal/Post)
    for rp in FilteredElementCollector(fdoc).OfClass(ReferencePlane):
        n = rp.Normal
        p = rp.BubbleEnd
        if abs(abs(n.X) - 1.0) < 1e-6 and abs(p.X) < 1e-6:
            centro_x = rp
        elif abs(abs(n.Y) - 1.0) < 1e-6 and abs(p.Y) < 1e-6:
            centro_y = rp
    return centro_x, centro_y


def plano_x(fdoc, vista, x, nombre, largo):
    """Plano de referencia vertical en x (normal X)."""
    rp = fdoc.FamilyCreate.NewReferencePlane(
        XYZ(x, -largo, 0), XYZ(x, largo, 0), XYZ(0, 0, 1), vista)
    rp.Name = nombre
    return rp


def plano_y(fdoc, vista, y, nombre, largo):
    """Plano de referencia vertical en y (normal Y)."""
    rp = fdoc.FamilyCreate.NewReferencePlane(
        XYZ(-largo, y, 0), XYZ(largo, y, 0), XYZ(0, 0, 1), vista)
    rp.Name = nombre
    return rp


def cota(fdoc, vista, planos, p0, p1, etiqueta=None, eq=False):
    """Cota lineal entre planos de referencia, opcionalmente etiquetada o EQ."""
    ra = ReferenceArray()
    for rp in planos:
        ra.Append(rp.GetReference())
    dim = fdoc.FamilyCreate.NewLinearDimension(vista, Line.CreateBound(p0, p1), ra)
    if etiqueta is not None:
        dim.FamilyLabel = etiqueta
    if eq:
        dim.AreSegmentsEqual = True
    return dim


def rectangulo(x0, x1, y0, y1):
    p = [XYZ(x0, y0, 0), XYZ(x1, y0, 0), XYZ(x1, y1, 0), XYZ(x0, y1, 0)]
    ca = CurveArray()
    for i in range(4):
        ca.Append(Line.CreateBound(p[i], p[(i + 1) % 4]))
    perfil = CurveArrArray()
    perfil.Append(ca)
    return perfil


def extrusion(fdoc, sketch_plane, x0, x1, y0, y1, inicio, fin):
    ext = fdoc.FamilyCreate.NewExtrusion(
        True, rectangulo(x0, x1, y0, y1), sketch_plane, fin)
    ext.StartOffset = inicio
    ext.EndOffset = fin
    return ext


def ref_cara(elem, normal, eje, valor):
    """Referencia de la cara plana con esa normal situada en eje=valor."""
    opts = Options()
    opts.ComputeReferences = True
    geo = elem.get_Geometry(opts)
    for g in geo:
        if not isinstance(g, Solid) or g.Faces.Size == 0:
            continue
        for f in g.Faces:
            if not isinstance(f, PlanarFace):
                continue
            if not f.FaceNormal.IsAlmostEqualTo(normal):
                continue
            o = f.Origin
            coord = o.X if eje == "x" else (o.Y if eje == "y" else o.Z)
            if abs(coord - valor) < 1e-4:
                return f.Reference
    raise Exception("No se encontro la cara {} en {}={:.4f}".format(
        normal, eje, valor))


def alinear(fdoc, vista, plano, elem, normal, eje, valor):
    al = fdoc.FamilyCreate.NewAlignment(
        vista, plano.GetReference(), ref_cara(elem, normal, eje, valor))
    al.IsLocked = True
    return al


def asociar(fm, elem, bip, fparam):
    p = elem.get_Parameter(bip)
    if p is None:
        raise Exception("El elemento {} no tiene el parametro {}".format(
            elem.Id, bip))
    fm.AssociateElementParameterToFamilyParameter(p, fparam)


# ---------------------------------------------------------------------------
# Construccion de la familia
# ---------------------------------------------------------------------------
def construir(fdoc):
    fm = fdoc.FamilyManager
    vista = vista_planta(fdoc)

    nombre_t, ancho, prof, altura = TIPOS[0]
    W, D, H = mm(ancho), mm(prof), mm(altura)
    E, L, R = mm(ESPESOR_TABLERO), mm(LADO_PATA), mm(RETRANQUEO_PATAS)
    HP = H - E
    largo = mm(max(ancho, prof))  # extension de los planos de referencia

    t = Transaction(fdoc, "Crear mesa parametrica")
    t.Start()
    try:
        # --- 1. Tipo y parametros --------------------------------------
        fm.NewType(nombre_t)

        def add(nombre, spec, grupo=GroupTypeId.Geometry, ejemplar=False):
            return fm.AddParameter(nombre, grupo, spec, ejemplar)

        p_ancho = add(P_ANCHO, SpecTypeId.Length)
        p_prof = add(P_PROF, SpecTypeId.Length)
        p_alt = add(P_ALTURA, SpecTypeId.Length)
        p_esp = add(P_ESPESOR, SpecTypeId.Length)
        p_lado = add(P_LADO_PATA, SpecTypeId.Length)
        p_ret = add(P_RETRANQUEO, SpecTypeId.Length)
        p_altp = add(P_ALT_PATAS, SpecTypeId.Length)
        p_mt = add(P_MAT_TABLERO, SpecTypeId.Reference.Material,
                   GroupTypeId.Materials)
        p_mp = add(P_MAT_PATAS, SpecTypeId.Reference.Material,
                   GroupTypeId.Materials)

        fm.Set(p_ancho, W)
        fm.Set(p_prof, D)
        fm.Set(p_alt, H)
        fm.Set(p_esp, E)
        fm.Set(p_lado, L)
        fm.Set(p_ret, R)
        fm.SetFormula(p_altp, "{} - {}".format(P_ALTURA, P_ESPESOR))

        # --- 2. Planos de referencia -----------------------------------
        cx, cy = planos_centrales(fdoc)
        if cx is None:
            cx = plano_x(fdoc, vista, 0.0, "Ref_Eje_X", largo)
        if cy is None:
            cy = plano_y(fdoc, vista, 0.0, "Ref_Eje_Y", largo)

        izq = plano_x(fdoc, vista, -W / 2, "Ref_Izquierda", largo)
        der = plano_x(fdoc, vista, W / 2, "Ref_Derecha", largo)
        fro = plano_y(fdoc, vista, -D / 2, "Ref_Frontal", largo)
        tra = plano_y(fdoc, vista, D / 2, "Ref_Trasera", largo)

        xi_e, xi_i = -W / 2 + R, -W / 2 + R + L
        xd_i, xd_e = W / 2 - R - L, W / 2 - R
        yf_e, yf_i = -D / 2 + R, -D / 2 + R + L
        yt_i, yt_e = D / 2 - R - L, D / 2 - R

        pi_e = plano_x(fdoc, vista, xi_e, "Ref_Pata_Izq_Ext", largo)
        pi_i = plano_x(fdoc, vista, xi_i, "Ref_Pata_Izq_Int", largo)
        pd_i = plano_x(fdoc, vista, xd_i, "Ref_Pata_Der_Int", largo)
        pd_e = plano_x(fdoc, vista, xd_e, "Ref_Pata_Der_Ext", largo)
        pf_e = plano_y(fdoc, vista, yf_e, "Ref_Pata_Fro_Ext", largo)
        pf_i = plano_y(fdoc, vista, yf_i, "Ref_Pata_Fro_Int", largo)
        pt_i = plano_y(fdoc, vista, yt_i, "Ref_Pata_Tra_Int", largo)
        pt_e = plano_y(fdoc, vista, yt_e, "Ref_Pata_Tra_Ext", largo)

        # --- 3. Cotas etiquetadas -------------------------------------
        off = mm(300)
        yd1, yd2, yd3 = -D / 2 - off, -D / 2 - 2 * off, -D / 2 - 0.5 * off
        xd1, xd2, xd3 = -W / 2 - off, -W / 2 - 2 * off, -W / 2 - 0.5 * off

        def lx(y):
            return XYZ(-W, y, 0), XYZ(W, y, 0)

        def ly(x):
            return XYZ(x, -D, 0), XYZ(x, D, 0)

        cota(fdoc, vista, [izq, cx, der], *lx(yd1), eq=True)
        cota(fdoc, vista, [izq, der], *lx(yd2), etiqueta=p_ancho)
        cota(fdoc, vista, [fro, cy, tra], *ly(xd1), eq=True)
        cota(fdoc, vista, [fro, tra], *ly(xd2), etiqueta=p_prof)

        cota(fdoc, vista, [izq, pi_e], *lx(yd3), etiqueta=p_ret)
        cota(fdoc, vista, [pd_e, der], *lx(yd3), etiqueta=p_ret)
        cota(fdoc, vista, [fro, pf_e], *ly(xd3), etiqueta=p_ret)
        cota(fdoc, vista, [pt_e, tra], *ly(xd3), etiqueta=p_ret)

        cota(fdoc, vista, [pi_e, pi_i], *lx(yd3), etiqueta=p_lado)
        cota(fdoc, vista, [pd_i, pd_e], *lx(yd3), etiqueta=p_lado)
        cota(fdoc, vista, [pf_e, pf_i], *ly(xd3), etiqueta=p_lado)
        cota(fdoc, vista, [pt_i, pt_e], *ly(xd3), etiqueta=p_lado)

        # --- 4. Geometria ---------------------------------------------
        sp = SketchPlane.Create(fdoc, Plane.CreateByNormalAndOrigin(
            XYZ.BasisZ, XYZ.Zero))

        tablero = extrusion(fdoc, sp, -W / 2, W / 2, -D / 2, D / 2, HP, H)
        patas = [
            (extrusion(fdoc, sp, xi_e, xi_i, yf_e, yf_i, 0.0, HP),
             pi_e, pi_i, pf_e, pf_i, xi_e, xi_i, yf_e, yf_i),
            (extrusion(fdoc, sp, xd_i, xd_e, yf_e, yf_i, 0.0, HP),
             pd_i, pd_e, pf_e, pf_i, xd_i, xd_e, yf_e, yf_i),
            (extrusion(fdoc, sp, xi_e, xi_i, yt_i, yt_e, 0.0, HP),
             pi_e, pi_i, pt_i, pt_e, xi_e, xi_i, yt_i, yt_e),
            (extrusion(fdoc, sp, xd_i, xd_e, yt_i, yt_e, 0.0, HP),
             pd_i, pd_e, pt_i, pt_e, xd_i, xd_e, yt_i, yt_e),
        ]
        fdoc.Regenerate()

        # --- 5. Bloqueo de caras a planos (en planta) ------------------
        nx, px_ = XYZ(-1, 0, 0), XYZ(1, 0, 0)
        ny, py_ = XYZ(0, -1, 0), XYZ(0, 1, 0)

        alinear(fdoc, vista, izq, tablero, nx, "x", -W / 2)
        alinear(fdoc, vista, der, tablero, px_, "x", W / 2)
        alinear(fdoc, vista, fro, tablero, ny, "y", -D / 2)
        alinear(fdoc, vista, tra, tablero, py_, "y", D / 2)

        for ext, rx0, rx1, ry0, ry1, x0, x1, y0, y1 in patas:
            alinear(fdoc, vista, rx0, ext, nx, "x", x0)
            alinear(fdoc, vista, rx1, ext, px_, "x", x1)
            alinear(fdoc, vista, ry0, ext, ny, "y", y0)
            alinear(fdoc, vista, ry1, ext, py_, "y", y1)

        # --- 6. Alturas y materiales asociados a parametros ------------
        asociar(fm, tablero, BuiltInParameter.EXTRUSION_START_PARAM, p_altp)
        asociar(fm, tablero, BuiltInParameter.EXTRUSION_END_PARAM, p_alt)
        asociar(fm, tablero, BuiltInParameter.MATERIAL_ID_PARAM, p_mt)
        for item in patas:
            ext = item[0]
            asociar(fm, ext, BuiltInParameter.EXTRUSION_END_PARAM, p_altp)
            asociar(fm, ext, BuiltInParameter.MATERIAL_ID_PARAM, p_mp)

        fdoc.Regenerate()

        # --- 7. Tipos adicionales -------------------------------------
        primer_tipo = fm.CurrentType
        for nombre, a, p, h in TIPOS[1:]:
            fm.NewType(nombre)
            fm.Set(p_ancho, mm(a))
            fm.Set(p_prof, mm(p))
            fm.Set(p_alt, mm(h))
            fdoc.Regenerate()
        fm.CurrentType = primer_tipo
        fdoc.Regenerate()

        t.Commit()
    except Exception:
        if t.HasStarted() and not t.HasEnded():
            t.RollBack()
        raise

    return tablero, patas


def prueba_flexion(fdoc, tablero):
    """Flexiona Ancho/Profundidad/Altura y comprueba el tablero. Se revierte."""
    fm = fdoc.FamilyManager
    params = {}
    for p in fm.GetParameters():
        params[p.Definition.Name] = p

    resultados = []
    t = Transaction(fdoc, "Prueba de flexion")
    t.Start()
    try:
        for a, p, h in PRUEBAS_FLEXION:
            estado = "OK"
            detalle = ""
            try:
                fm.Set(params[P_ANCHO], mm(a))
                fm.Set(params[P_PROF], mm(p))
                fm.Set(params[P_ALTURA], mm(h))
                fdoc.Regenerate()
                bb = tablero.get_BoundingBox(None)
                ma = a_mm(bb.Max.X - bb.Min.X)
                mp = a_mm(bb.Max.Y - bb.Min.Y)
                mh = a_mm(bb.Max.Z)
                if abs(ma - a) > 0.5 or abs(mp - p) > 0.5 or abs(mh - h) > 0.5:
                    estado = "FALLO"
                detalle = "medido {:.0f} x {:.0f} x {:.0f}".format(ma, mp, mh)
            except Exception as ex:
                estado = "ERROR"
                detalle = str(ex)
            resultados.append(("{:.0f} x {:.0f} x {:.0f}".format(a, p, h),
                               estado, detalle))
    finally:
        t.RollBack()
    return resultados


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    plantilla = buscar_plantilla()
    if not plantilla:
        forms.alert("No se selecciono plantilla. Operacion cancelada.")
        return
    output.print_md("**Plantilla:** `{}`".format(plantilla))

    destino = forms.save_file(file_ext="rfa", default_name=NOMBRE_FAMILIA)
    if not destino:
        forms.alert("No se eligio ruta de guardado. Operacion cancelada.")
        return

    fdoc = app.NewFamilyDocument(plantilla)
    if fdoc is None:
        forms.alert("Revit no pudo crear el documento de familia.")
        return

    cerrado = False
    try:
        tablero, _ = construir(fdoc)
        output.print_md("Geometria, parametros y cotas creados.")

        resultados = prueba_flexion(fdoc, tablero)
        output.print_md("### Prueba de flexion (tablero)")
        output.print_table(
            table_data=[list(r) for r in resultados],
            columns=["Ancho x Prof x Altura (mm)", "Resultado", "Detalle"],
        )
        fallos = [r for r in resultados if r[1] != "OK"]

        opts = SaveAsOptions()
        opts.OverwriteExistingFile = True  # el dialogo de Windows ya pidio confirmacion
        fdoc.SaveAs(destino, opts)
        output.print_md("**Familia guardada:** `{}`".format(destino))

        proyecto = uiapp.ActiveUIDocument.Document if uiapp.ActiveUIDocument else None
        if proyecto is not None and not proyecto.IsFamilyDocument:
            if forms.alert("Familia creada. Cargarla en el proyecto activo?",
                           yes=True, no=True):
                fdoc.LoadFamily(proyecto)
                output.print_md("Familia cargada en **{}**.".format(proyecto.Title))

        fdoc.Close(False)
        cerrado = True

        if fallos:
            forms.alert("La familia se guardo, pero {} prueba(s) de flexion "
                        "fallaron. Revisa la ventana de salida.".format(len(fallos)))
        elif forms.alert("Abrir la familia en el Editor de familias?",
                         yes=True, no=True):
            uiapp.OpenAndActivateDocument(destino)
    except Exception as ex:
        output.print_md("**Error:** {}".format(ex))
        forms.alert("Error al crear la familia:\n{}".format(ex))
    finally:
        if not cerrado:
            try:
                fdoc.Close(False)
            except Exception:
                pass


main()
