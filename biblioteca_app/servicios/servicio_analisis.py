"""
servicios/servicio_analisis.py
--------------------------------------
Capa de Ciencia de Datos del proyecto. Usa pandas/numpy para
transformar los datos del sistema en estadísticas descriptivas y
usa matplotlib/seaborn para generar gráficos que se devuelven como
strings base64 (listos para embeber en HTML con <img src="data:...">
sin necesidad de guardar archivos en disco).

Aplica los tres elementos requeridos de Ciencia de Datos:
  - PROCESAMIENTO: lectura desde BD vía ServicioReportes + lectura
    de CSV/Excel para carga masiva (ver método importar_libros_desde_archivo).
  - ANÁLISIS: limpieza de datos, transformación, estadísticas descriptivas
    (describe(), value_counts(), groupby, resample).
  - VISUALIZACIÓN: gráficos de barras, circular, histograma, serie temporal
    y un dashboard con todos ellos integrados en la vista web.
"""

import io
import base64
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend sin GUI, obligatorio en Flask (sin pantalla)
import matplotlib.pyplot as plt
import seaborn as sns

from servicios.servicio_reportes import ServicioReportes

# Paleta y estilo globales para coherencia visual entre gráficos
sns.set_theme(style="whitegrid", palette="muted")


def _figura_a_base64(fig) -> str:
    """Convierte una figura matplotlib a string base64 para embeber en HTML."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


class ServicioAnalisis:
    def __init__(self):
        self._servicio_reportes = ServicioReportes()

    # ------------------------------------------------------------------ #
    #  PROCESAMIENTO Y TRANSFORMACIÓN DE DATOS                            #
    # ------------------------------------------------------------------ #

    def _df_prestamos_por_categoria(self) -> pd.DataFrame:
        """Lee los datos desde BD y los convierte en DataFrame limpio."""
        filas = self._servicio_reportes.prestamos_por_categoria()
        df = pd.DataFrame(filas)
        if df.empty:
            return pd.DataFrame(columns=["nombre_categoria", "total_prestamos"])
        # Limpieza: sin nulos, tipos correctos
        df = df.dropna(subset=["nombre_categoria"])
        df["total_prestamos"] = pd.to_numeric(df["total_prestamos"], errors="coerce").fillna(0).astype(int)
        df = df.sort_values("total_prestamos", ascending=False).reset_index(drop=True)
        return df

    def _df_libros_mas_prestados(self, limite: int = 10) -> pd.DataFrame:
        filas = self._servicio_reportes.libros_mas_prestados(limite)
        df = pd.DataFrame(filas)
        if df.empty:
            return pd.DataFrame(columns=["titulo", "total_prestamos"])
        df = df.dropna(subset=["titulo"])
        df["total_prestamos"] = pd.to_numeric(df["total_prestamos"], errors="coerce").fillna(0).astype(int)
        # Truncar títulos largos para que quepan en el gráfico
        df["titulo_corto"] = df["titulo"].str.slice(0, 35)
        return df

    def _df_distribucion_membresias(self) -> pd.DataFrame:
        filas = self._servicio_reportes.distribucion_membresias()
        df = pd.DataFrame(filas)
        if df.empty:
            return pd.DataFrame(columns=["tipo_membresia", "total_usuarios"])
        df["total_usuarios"] = pd.to_numeric(df["total_usuarios"], errors="coerce").fillna(0).astype(int)
        return df

    def _df_prestamos_por_mes(self, anio: int) -> pd.DataFrame:
        filas = self._servicio_reportes.prestamos_por_mes(anio)
        nombres_mes = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
                       7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
        # Siempre partir de los 12 meses para que la serie temporal sea completa
        todos_meses = pd.DataFrame({"mes": range(1, 13)})
        if filas:
            df_datos = pd.DataFrame(filas)
            df_datos["mes"] = pd.to_numeric(df_datos["mes"], errors="coerce").astype(int)
            df_datos["total"] = pd.to_numeric(df_datos["total"], errors="coerce").fillna(0).astype(int)
            df = todos_meses.merge(df_datos, on="mes", how="left").fillna(0)
        else:
            df = todos_meses.copy()
            df["total"] = 0
        df["total"] = df["total"].astype(int)
        df["mes_nombre"] = df["mes"].map(nombres_mes)
        return df

    # ------------------------------------------------------------------ #
    #  ESTADÍSTICAS DESCRIPTIVAS                                          #
    # ------------------------------------------------------------------ #

    def estadisticas_prestamos_por_categoria(self) -> dict:
        """
        Estadísticas descriptivas (numpy/pandas) sobre los préstamos
        agrupados por categoría: total, media, máximo, mínimo, desv. estándar.
        """
        df = self._df_prestamos_por_categoria()
        if df.empty or df["total_prestamos"].sum() == 0:
            return {"sin_datos": True}

        serie = df["total_prestamos"]
        return {
            "sin_datos": False,
            "total_prestamos": int(serie.sum()),
            "categorias_con_prestamos": int((serie > 0).sum()),
            "media": round(float(np.mean(serie)), 2),
            "mediana": round(float(np.median(serie)), 2),
            "maximo": int(serie.max()),
            "minimo": int(serie.min()),
            "desv_estandar": round(float(np.std(serie)), 2),
            "categoria_mas_popular": df.iloc[0]["nombre_categoria"],
        }

    def estadisticas_multas(self) -> dict:
        resumen = self._servicio_reportes.resumen_multas()
        if not resumen or not resumen.get("total_multas"):
            return {"sin_datos": True}
        return {
            "sin_datos": False,
            "total_multas": int(resumen["total_multas"] or 0),
            "pendientes": int(resumen["pendientes"] or 0),
            "pagadas": int(resumen["pagadas"] or 0),
            "monto_total": float(resumen["monto_total"] or 0),
            "tasa_pago": round(
                (int(resumen["pagadas"] or 0) / int(resumen["total_multas"])) * 100, 1
            ) if resumen["total_multas"] else 0,
        }

    # ------------------------------------------------------------------ #
    #  VISUALIZACIONES                                                     #
    # ------------------------------------------------------------------ #

    def grafico_barras_prestamos_por_categoria(self) -> str:
        """Gráfico de barras horizontales: préstamos por categoría."""
        df = self._df_prestamos_por_categoria()
        fig, ax = plt.subplots(figsize=(8, 4))

        if df.empty or df["total_prestamos"].sum() == 0:
            ax.text(0.5, 0.5, "Sin datos de préstamos aún",
                    ha="center", va="center", transform=ax.transAxes, color="gray")
        else:
            colores = sns.color_palette("Blues_d", len(df))
            ax.barh(df["nombre_categoria"], df["total_prestamos"], color=colores)
            ax.set_xlabel("Total de préstamos")
            ax.set_title("Préstamos por categoría")
            for i, v in enumerate(df["total_prestamos"]):
                ax.text(v + 0.1, i, str(v), va="center", fontsize=9)
            ax.invert_yaxis()

        return _figura_a_base64(fig)

    def grafico_circular_membresias(self) -> str:
        """Gráfico circular: distribución de usuarios por tipo de membresía."""
        df = self._df_distribucion_membresias()
        fig, ax = plt.subplots(figsize=(6, 5))

        if df.empty or df["total_usuarios"].sum() == 0:
            ax.text(0.5, 0.5, "Sin datos de usuarios aún",
                    ha="center", va="center", transform=ax.transAxes, color="gray")
        else:
            colores = sns.color_palette("pastel", len(df))
            wedges, texts, autotexts = ax.pie(
                df["total_usuarios"],
                labels=df["tipo_membresia"],
                autopct="%1.1f%%",
                colors=colores,
                startangle=90,
            )
            for text in autotexts:
                text.set_fontsize(10)
            ax.set_title("Distribución de membresías")

        return _figura_a_base64(fig)

    def grafico_libros_mas_prestados(self, limite: int = 8) -> str:
        """Gráfico de barras verticales: libros más prestados."""
        df = self._df_libros_mas_prestados(limite)
        fig, ax = plt.subplots(figsize=(9, 4))

        if df.empty or df["total_prestamos"].sum() == 0:
            ax.text(0.5, 0.5, "Sin datos de préstamos aún",
                    ha="center", va="center", transform=ax.transAxes, color="gray")
        else:
            colores = sns.color_palette("Greens_d", len(df))
            ax.bar(df["titulo_corto"], df["total_prestamos"], color=colores)
            ax.set_ylabel("Total de préstamos")
            ax.set_title(f"Top {len(df)} libros más prestados")
            plt.xticks(rotation=30, ha="right", fontsize=8)

        return _figura_a_base64(fig)

    def grafico_serie_temporal(self, anio: int = None) -> str:
        """Serie temporal: préstamos por mes durante un año."""
        import datetime
        anio = anio or datetime.date.today().year
        df = self._df_prestamos_por_mes(anio)
        fig, ax = plt.subplots(figsize=(9, 4))

        ax.plot(df["mes_nombre"], df["total"], marker="o", linewidth=2,
                color=sns.color_palette("muted")[0])
        ax.fill_between(df["mes_nombre"], df["total"], alpha=0.15,
                        color=sns.color_palette("muted")[0])
        ax.set_title(f"Préstamos por mes — {anio}")
        ax.set_ylabel("Préstamos")
        ax.set_xlabel("Mes")
        plt.xticks(rotation=20, fontsize=9)

        if df["total"].sum() == 0:
            ax.text(0.5, 0.5, f"Sin préstamos registrados en {anio}",
                    ha="center", va="center", transform=ax.transAxes,
                    color="gray", fontsize=11)

        return _figura_a_base64(fig)

    def grafico_histograma_multas(self) -> str:
        """
        Histograma de montos de multas pendientes.
        PROCESAMIENTO: limpieza de nulos y conversión de tipo antes de graficar.
        """
        from persistencia.repositorio_prestamos import RepositorioMultas
        repo = RepositorioMultas()
        filas = repo.ejecutar_consulta_personalizada(
            "SELECT monto FROM multas WHERE estado_pago = 'PENDIENTE'"
        )
        df = pd.DataFrame(filas)
        fig, ax = plt.subplots(figsize=(7, 4))

        if df.empty:
            ax.text(0.5, 0.5, "Sin multas pendientes",
                    ha="center", va="center", transform=ax.transAxes, color="gray")
        else:
            df["monto"] = pd.to_numeric(df["monto"], errors="coerce").dropna()
            sns.histplot(df["monto"], bins=10, kde=True, ax=ax,
                         color=sns.color_palette("muted")[3])
            ax.set_title("Distribución de montos de multas pendientes")
            ax.set_xlabel("Monto (S/)")
            ax.set_ylabel("Frecuencia")

        return _figura_a_base64(fig)

    def datos_dashboard_json(self, anio: int = None) -> dict:
        """
        Devuelve los datos del dashboard en formato JSON-serializable
        (listas de labels y valores) para que Chart.js los renderice
        en el cliente como gráficos interactivos.
        Mantiene los métodos de matplotlib para exportación a imagen.
        """
        import datetime
        anio = anio or datetime.date.today().year

        # Préstamos por categoría
        df_cat = self._df_prestamos_por_categoria()
        categorias = df_cat["nombre_categoria"].tolist() if not df_cat.empty else []
        totales_cat = [int(v) for v in df_cat["total_prestamos"].tolist()] if not df_cat.empty else []

        # Membresías
        df_mem = self._df_distribucion_membresias()
        membresias = df_mem["tipo_membresia"].tolist() if not df_mem.empty else []
        totales_mem = [int(v) for v in df_mem["total_usuarios"].tolist()] if not df_mem.empty else []

        # Top libros
        df_lib = self._df_libros_mas_prestados(8)
        titulos = df_lib["titulo_corto"].tolist() if not df_lib.empty else []
        totales_lib = [int(v) for v in df_lib["total_prestamos"].tolist()] if not df_lib.empty else []

        # Serie temporal
        df_mes = self._df_prestamos_por_mes(anio)
        meses = df_mes["mes_nombre"].tolist()
        totales_mes = [int(v) for v in df_mes["total"].tolist()]

        # Multas (histograma → distribución en rangos)
        from persistencia.repositorio_prestamos import RepositorioMultas
        filas_multas = RepositorioMultas().ejecutar_consulta_personalizada(
            "SELECT monto FROM multas WHERE estado_pago = 'PENDIENTE'"
        )
        import pandas as pd
        df_multas = pd.DataFrame(filas_multas)
        if not df_multas.empty:
            df_multas["monto"] = pd.to_numeric(df_multas["monto"], errors="coerce").dropna()
            bins = [0, 5, 10, 15, 20, 30, 50, 100]
            labels_hist = ["0-5", "5-10", "10-15", "15-20", "20-30", "30-50", "50+"]
            counts = pd.cut(df_multas["monto"], bins=bins, labels=labels_hist).value_counts().reindex(labels_hist, fill_value=0)
            hist_labels = labels_hist
            hist_data = [int(v) for v in counts.tolist()]
        else:
            hist_labels, hist_data = [], []

        return {
            "anio": anio,
            "estadisticas_categorias": self.estadisticas_prestamos_por_categoria(),
            "estadisticas_multas": self.estadisticas_multas(),
            "categorias": {"labels": categorias, "data": totales_cat},
            "membresias": {"labels": membresias, "data": totales_mem},
            "top_libros": {"labels": titulos, "data": totales_lib},
            "serie_temporal": {"labels": meses, "data": totales_mes},
            "histograma_multas": {"labels": hist_labels, "data": hist_data},
        }

    def generar_dashboard_completo(self, anio: int = None) -> dict:
        """
        Genera todos los gráficos y estadísticas de una vez.
        Devuelve un dict listo para pasar directamente a la plantilla Jinja2.
        """
        import datetime
        anio = anio or datetime.date.today().year
        return {
            "anio": anio,
            "estadisticas_categorias": self.estadisticas_prestamos_por_categoria(),
            "estadisticas_multas": self.estadisticas_multas(),
            "grafico_categorias": self.grafico_barras_prestamos_por_categoria(),
            "grafico_membresias": self.grafico_circular_membresias(),
            "grafico_top_libros": self.grafico_libros_mas_prestados(),
            "grafico_serie_temporal": self.grafico_serie_temporal(anio),
            "grafico_histograma_multas": self.grafico_histograma_multas(),
        }

    # ------------------------------------------------------------------ #
    #  CARGA MASIVA DESDE CSV / EXCEL                                     #
    # ------------------------------------------------------------------ #

    def importar_libros_desde_archivo(self, ruta_archivo: str, id_categoria: int, id_estado: int) -> dict:
        """
        Lee un archivo CSV o Excel (detecta por extensión), limpia los datos,
        valida las columnas requeridas y devuelve un resumen de la importación.
        El llamador (controlador) se encarga de persistir los libros válidos.

        Columnas requeridas en el archivo: ISBN, titulo, autor
        Columnas opcionales: editorial, anio_publicacion

        Devuelve:
            {
              "validos": [lista de dicts con datos de libro listos para insertar],
              "errores": [lista de strings describiendo filas con problemas],
              "total_leidos": int,
              "total_validos": int,
              "total_errores": int,
            }
        """
        extension = ruta_archivo.rsplit(".", 1)[-1].lower()
        try:
            if extension in ("xlsx", "xls"):
                df = pd.read_excel(ruta_archivo, dtype=str)
            elif extension == "csv":
                df = pd.read_csv(ruta_archivo, dtype=str, encoding="utf-8-sig")
            else:
                return {"error": f"Formato no soportado: .{extension}. Use .csv, .xlsx o .xls"}
        except Exception as e:
            return {"error": f"No se pudo leer el archivo: {e}"}

        # --- LIMPIEZA ---
        # Normalizar nombres de columnas: sin espacios, en minúsculas
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        columnas_requeridas = {"isbn", "titulo", "autor"}
        columnas_faltantes = columnas_requeridas - set(df.columns)
        if columnas_faltantes:
            return {"error": f"Columnas obligatorias faltantes en el archivo: {columnas_faltantes}. "
                             f"Columnas encontradas: {list(df.columns)}"}

        # Eliminar filas donde ISBN, titulo o autor estén todos vacíos (filas basura)
        df = df.dropna(subset=["isbn", "titulo", "autor"], how="all")
        # NO usar fillna en anio_publicacion — debe quedarse como NaN para que
        # _convertir_anio lo detecte y devuelva None.
        for col in ["editorial"]:
            if col not in df.columns:
                df[col] = ""
        if "anio_publicacion" not in df.columns:
            df["anio_publicacion"] = None
        df["editorial"] = df["editorial"].fillna("")

        # Transformación: limpiar espacios, convertir año a int si viene como float ("2008.0")
        df["isbn"] = df["isbn"].str.strip()
        df["titulo"] = df["titulo"].str.strip()
        df["autor"] = df["autor"].str.strip()
        df["editorial"] = df["editorial"].str.strip()

        def _convertir_anio(valor):
            if valor is None:
                return None
            try:
                if pd.isna(valor):
                    return None
            except (TypeError, ValueError):
                pass
            try:
                return int(float(str(valor)))
            except (ValueError, TypeError):
                return None

        df["anio_publicacion"] = df["anio_publicacion"].apply(_convertir_anio)

        # --- VALIDACIÓN fila por fila ---
        validos, errores = [], []
        for i, fila in df.iterrows():
            fila_num = i + 2  # +2: la fila 1 es el encabezado, i empieza en 0
            isbn_val = str(fila["isbn"]).strip() if pd.notna(fila["isbn"]) else ""
            titulo_val = str(fila["titulo"]).strip() if pd.notna(fila["titulo"]) else ""
            autor_val = str(fila["autor"]).strip() if pd.notna(fila["autor"]) else ""

            if not isbn_val or isbn_val.lower() in ("nan", "none"):
                errores.append(f"Fila {fila_num}: ISBN vacío o inválido.")
                continue
            if not titulo_val or titulo_val.lower() in ("nan", "none"):
                errores.append(f"Fila {fila_num} (ISBN {isbn_val}): título vacío.")
                continue
            if not autor_val or autor_val.lower() in ("nan", "none"):
                errores.append(f"Fila {fila_num} (ISBN {isbn_val}): autor vacío.")
                continue

            anio = fila["anio_publicacion"]
            # pd.isna cubre tanto None como numpy.nan, que pandas puede devolver
            # incluso después de un apply que devolvió None (depende del dtype de la columna)
            if anio is not None and not pd.isna(anio) and not (1450 <= int(anio) <= 2100):
                errores.append(f"Fila {fila_num} (ISBN {isbn_val}): año fuera de rango ({int(anio)}). Se guardará sin año.")
                anio = None
            elif anio is not None and pd.isna(anio):
                anio = None

            validos.append({
                "isbn": isbn_val,
                "titulo": titulo_val,
                "autor": autor_val,
                "editorial": str(fila["editorial"]).strip() if pd.notna(fila["editorial"]) and str(fila["editorial"]).lower() not in ("nan","none","") else None,
                "anio_publicacion": anio,
                "id_categoria": id_categoria,
                "id_estado": id_estado,
            })

        return {
            "validos": validos,
            "errores": errores,
            "total_leidos": len(df),
            "total_validos": len(validos),
            "total_errores": len(errores),
        }
