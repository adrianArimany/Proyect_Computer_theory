# Simulador de Autómatas Finitos Probabilísticos (PFA)

Este proyecto implementa un **simulador interactivo de Autómatas Finitos Probabilísticos (PFA)** en Python utilizando [Streamlit](https://streamlit.io/).  
Permite cargar autómatas desde archivos `.json`, visualizar su diagrama, y analizar probabilidades de aceptación de palabras mediante:

- **Simulación Monte Carlo** (estimación probabilística).
- **Método matricial** (cálculo exacto).
- **Análisis de puntos de corte (cut-points)**.
- **Probabilidades de retorno en bucles (loop return)**.

---

# Autor:

- Adrian Arimany Zamora 211063

---

## Características principales

- **Carga de PFAs desde JSON**  
  Archivos con la definición de estados, alfabeto, transiciones, estado inicial y estados de aceptación.

- **Visualización del autómata**  
  Diagrama de estados y transiciones con `networkx` y `matplotlib`.

- **Evaluación de palabras**  
  Probabilidad de aceptación de palabras individuales:
  - Comparación Monte Carlo vs Método matricial.
  - Benchmarks de tiempo de ejecución.
  - Gráficas de precisión.

- **Análisis de puntos de corte (Cut-point analysis)**  
  Determina si la probabilidad de aceptación de una palabra supera un umbral o cae dentro de un intervalo.  
  Incluye búsqueda de palabras que cumplen con el criterio dentro de un límite de tiempo.

- **Probabilidades de bucle (Loop return)**  
  Calcula la probabilidad de aceptación de repeticiones de un símbolo (\(a^k\)) tanto con:
  - **Método matricial (exacto)**.
  - **Método Monte Carlo (aproximado para grandes k)**.
  Permite estudiar la convergencia de probabilidades cuando \(k\) es grande.

- **Interfaz interactiva en Streamlit**  
  - Barra lateral para cargar archivos.
  - Tres secciones principales: *Palabras*, *Cut-points*, *Bucles*.  
  - Tablas con coloreado para distinguir métodos (Monte Carlo en rojo, Matricial en azul).
  - Gráficas comparativas.

---

## Ejecución

1. Clonar este repositorio:
   
   ```bash
   git clone https://github.com/adrianArimany/Proyect_Computer_theory.git
   cd Proyect_Computer_theory
   ```

2.Crear un entorno virtual e instalar dependencias:

   ```bash
   python3 -m venv myenv
   source myenv/bin/activate   # Linux/Mac
   myenv\Scripts\activate      # Windows

   pip install -r requirements.txt
   ```

3. Ejecutar la aplicación Streamlit:

```bash
python3 -m streamlit run main.py
```

