# CÓMO RETOMAR EL PROYECTO (para Adrián)

Todo el trabajo nuevo (tesis corregida y aprobada, presentación de 16 slides,
póster, laboratorio MATLAB) está en GitHub, en la rama **geometria-real-nv1640**.
NO está en `main` (main está viejo).

Repo: https://github.com/AdrianLopez012/tesis-lhd-802.11ac.git

---

## SI VUELVES A LA MÁQUINA QUE YA TENÍA EL PROYECTO (versión vieja)

Esa máquina tiene commits antiguos. Para traer lo nuevo SIN conflictos:

```bash
cd  <ruta donde tengas el proyecto allá>

# 1) red de seguridad: guarda lo que hubiera viejo (no pierdes nada)
git stash
git branch respaldo-maquina-vieja

# 2) trae TODO lo nuevo de GitHub y pon la máquina idéntica al remoto
git fetch origin
git checkout geometria-real-nv1640
git reset --hard origin/geometria-real-nv1640
```

Verifica que llegó lo último:
```bash
git log --oneline -1
```
Debe decir:  **adfc62e Respaldar PDF de entregables...**  -> si lo ves, cogió todo. OK

NO hagas `git pull` a secas allá (puede dar conflicto viejo-vs-nuevo).

---

## SI ES UNA MÁQUINA/CUENTA TOTALMENTE NUEVA (nunca tuvo el proyecto)

Terminal en la carpeta donde quieras guardarlo (ej. Documents):
```bash
git clone https://github.com/AdrianLopez012/tesis-lhd-802.11ac.git
cd tesis-lhd-802.11ac
git checkout geometria-real-nv1640
```

---

## VERIFICAR QUE COGIÓ BIEN (en cualquier caso)

```bash
ls fase4/presentacion/Sustentacion_LopezPascual_TdT2.pptx
ls fase4/trabajo/tesis_v2.docx
tail -40 TRASPASO_CONTEXTO.md
```
Si aparecen los archivos y el texto de la sección 15 -> todo correcto.

---

## PARA QUE CLAUDE RETOME EL CONTEXTO

Abre la sesión dentro de la carpeta del proyecto y dile:
> "Lee TRASPASO_CONTEXTO.md, en especial la sección 15, para retomar el proyecto de tesis"

Esa sección 15 documenta TODO lo hecho el 15-16 de julio: entregables, la PPT,
el laboratorio MATLAB, los pendientes (informe de similitud + ensayo) y los
próximos pasos.

---

## PENDIENTES REALES (lo que falta hacer)
1. Informe de similitud: cuando el profesor mande el reporte Turnitin, llenar la
   página 2 de la tesis (datos del asesor + %), regenerar PDF y subir a PAIDEIA.
2. Ensayar la sustentación (18 min) + estudiar banco_preguntas_jurado.docx.
3. ExpoSTEM 21 jul (asistencia obligatoria).
