import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy as sp
from sympy import symbols, solve, limit, oo, pi, E, log, exp, sin, cos, tan, sqrt
import math


class FunctionAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Funciones Matemáticas")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variable simbólica
        self.x = symbols('x', real=True)
        self.function = None
        self.evaluated_point = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Entrada de función
        ttk.Label(main_frame, text="Función f(x):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.function_entry = ttk.Entry(main_frame, width=50, font=('Courier', 11))
        self.function_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Entrada de valor x
        ttk.Label(main_frame, text="Valor x (opcional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.x_entry = ttk.Entry(main_frame, width=20)
        self.x_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=2, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Analizar", command=self.analyze_function).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # Frame para resultados y gráfica
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Panel de resultados
        results_frame = ttk.LabelFrame(content_frame, text="Análisis de la Función", padding="10")
        results_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, width=50, height=25, 
                                                     font=('Courier', 10))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Panel de gráfica
        graph_frame = ttk.LabelFrame(content_frame, text="Gráfica", padding="10")
        graph_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)
        
        # Configurar matplotlib
        plt.style.use('default')
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Ejemplos
        examples_frame = ttk.LabelFrame(main_frame, text="Ejemplos de funciones", padding="5")
        examples_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        examples_text = ("Ejemplos: x**2, x**2-4, sin(x), log(x), sqrt(x), 1/x, exp(x)\n"
                        "Usa ** para potencias, sqrt() para raíz cuadrada, log() para logaritmo natural")
        ttk.Label(examples_frame, text=examples_text, font=('Arial', 9)).pack()
    
    def clear_all(self):
        """Limpia todos los campos y resultados"""
        self.function_entry.delete(0, tk.END)
        self.x_entry.delete(0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.ax.clear()
        self.canvas.draw()
        self.function = None
        self.evaluated_point = None
    
    def analyze_function(self):
        """Analiza la función ingresada"""
        try:
            function_str = self.function_entry.get().strip()
            if not function_str:
                messagebox.showerror("Error", "Por favor ingrese una función")
                return
            
            self.add_result("Iniciando análisis...")
            self.add_result(f"Función ingresada: {function_str}")
            
            # Parsear la función con manejo de errores mejorado
            try:
                # Reemplazos comunes para mejorar compatibilidad
                function_str_clean = function_str.replace('^', '**')
                self.function = sp.sympify(function_str_clean, locals={'x': self.x})
                self.add_result(f"Función parseada: f(x) = {self.function}")
            except Exception as parse_error:
                messagebox.showerror("Error de Sintaxis", 
                    f"No se pudo interpretar la función: {str(parse_error)}\n\n"
                    f"Revise la sintaxis. Use ** para potencias, no ^")
                return
            
            # Limpiar resultados previos
            self.results_text.delete(1.0, tk.END)
            self.add_result(f"Función: f(x) = {self.function}")
            self.add_result("="*60)
            
            # Análisis de dominio
            self.analyze_domain()
            
            # Análisis de recorrido
            self.analyze_range()
            
            # Intersecciones
            self.find_intersections()
            
            # Evaluación de punto específico
            x_value = self.x_entry.get().strip()
            if x_value:
                self.evaluate_point(x_value)
            
            # Generar gráfica
            self.plot_function()
            
        except Exception as e:
            error_msg = f"Error general: {str(e)}"
            self.add_result(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def add_result(self, text):
        """Añade texto al panel de resultados"""
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END)
        self.root.update()  # Actualizar interfaz
    
    def analyze_domain(self):
        """Analiza el dominio de la función"""
        self.add_result("ANÁLISIS DEL DOMINIO:")
        self.add_result("-" * 25)
        
        try:
            # Análisis básico por tipo de función
            function_str = str(self.function)
            
            # Verificar si hay divisiones por cero
            has_division = False
            division_points = []
            
            # Buscar denominadores
            try:
                numer, denom = self.function.as_numer_denom()
                if denom != 1 and denom != sp.Integer(1):
                    has_division = True
                    zeros = solve(denom, self.x)
                    for zero in zeros:
                        if zero.is_real:
                            division_points.append(float(zero))
                    self.add_result(f"Denominador encontrado: {denom}")
                    self.add_result(f"Puntos problemáticos: {division_points}")
            except:
                pass
            
            # Verificar logaritmos
            has_log = 'log' in function_str
            if has_log:
                self.add_result("Contiene logaritmos - requiere argumento positivo")
            
            # Verificar raíces cuadradas
            has_sqrt = 'sqrt' in function_str
            if has_sqrt:
                self.add_result("Contiene raíces cuadradas - requiere argumento no negativo")
            
            # Conclusión sobre el dominio
            if not has_division and not has_log and not has_sqrt:
                self.add_result("✓ DOMINIO: Todos los números reales (ℝ)")
                self.add_result("  Justificación: No hay restricciones en la función")
            else:
                self.add_result("⚠ DOMINIO: Restringido")
                if division_points:
                    self.add_result(f"  Excluir puntos: {division_points}")
                if has_log:
                    self.add_result("  Restricción: argumento de log > 0")
                if has_sqrt:
                    self.add_result("  Restricción: argumento de sqrt ≥ 0")
                    
        except Exception as e:
            self.add_result(f"Error en análisis de dominio: {str(e)}")
        
        self.add_result("")
    
    def analyze_range(self):
        """Analiza el recorrido de la función"""
        self.add_result("ANÁLISIS DEL RECORRIDO:")
        self.add_result("-" * 26)
        
        try:
            # Calcular límites en infinito
            try:
                limit_pos_inf = limit(self.function, self.x, oo)
                limit_neg_inf = limit(self.function, self.x, -oo)
                
                self.add_result("Límites en el infinito:")
                self.add_result(f"  lim(x→+∞) f(x) = {limit_pos_inf}")
                self.add_result(f"  lim(x→-∞) f(x) = {limit_neg_inf}")
            except:
                self.add_result("No se pudieron calcular todos los límites")
            
            # Encontrar derivada y puntos críticos
            try:
                derivative = sp.diff(self.function, self.x)
                self.add_result(f"Derivada: f'(x) = {derivative}")
                
                critical_points = solve(derivative, self.x)
                if critical_points:
                    self.add_result(f"Puntos críticos: {critical_points}")
                    for cp in critical_points[:3]:  # Máximo 3 puntos para evitar sobrecarga
                        if cp.is_real:
                            try:
                                value = self.function.subs(self.x, cp)
                                self.add_result(f"  f({cp}) = {value}")
                            except:
                                pass
                else:
                    self.add_result("No hay puntos críticos finitos")
            except:
                self.add_result("No se pudo calcular la derivada")
                
        except Exception as e:
            self.add_result(f"Error en análisis de recorrido: {str(e)}")
        
        self.add_result("")
    
    def find_intersections(self):
        """Encuentra las intersecciones con los ejes"""
        self.add_result("INTERSECCIONES CON LOS EJES:")
        self.add_result("-" * 32)
        
        # Intersección con eje Y (x = 0)
        self.add_result("Intersección con eje Y (x = 0):")
        try:
            y_intercept = self.function.subs(self.x, 0)
            y_value = float(y_intercept.evalf())
            self.add_result(f"  f(0) = {y_intercept}")
            self.add_result(f"  f(0) = {y_value}")
            self.add_result(f"  Punto: (0, {y_value})")
        except Exception as e:
            self.add_result(f"  No definida en x=0: {str(e)}")
        
        # Intersecciones con eje X (f(x) = 0)
        self.add_result(f"\nIntersecciones con eje X (f(x) = 0):")
        try:
            self.add_result(f"Resolviendo: {self.function} = 0")
            x_intercepts = solve(self.function, self.x)
            
            if x_intercepts:
                self.add_result(f"Soluciones: {len(x_intercepts)} encontradas")
                real_intercepts = []
                for intercept in x_intercepts:
                    try:
                        if intercept.is_real:
                            x_val = float(intercept.evalf())
                            real_intercepts.append(x_val)
                            self.add_result(f"  ({x_val:.4f}, 0)")
                    except:
                        self.add_result(f"  {intercept} (simbólica)")
                        
                if not real_intercepts:
                    self.add_result("  No hay intersecciones reales con el eje X")
            else:
                self.add_result("  No hay intersecciones con el eje X")
                
        except Exception as e:
            self.add_result(f"  Error: {str(e)}")
        
        self.add_result("")
    
    def evaluate_point(self, x_value_str):
        """Evalúa la función en un punto específico"""
        self.add_result("EVALUACIÓN DE PUNTO ESPECÍFICO:")
        self.add_result("-" * 35)
        
        try:
            x_value = float(x_value_str)
            self.add_result(f"Evaluando f({x_value}):")
            self.add_result(f"f(x) = {self.function}")
            
            # Mostrar sustitución
            self.add_result(f"Sustituyendo x = {x_value}:")
            substituted = self.function.subs(self.x, x_value)
            self.add_result(f"f({x_value}) = {substituted}")
            
            # Calcular resultado numérico
            result = float(substituted.evalf())
            self.add_result(f"f({x_value}) = {result}")
            
            # Mostrar par ordenado
            self.add_result(f"\n✓ Par ordenado: ({x_value}, {result})")
            
            self.evaluated_point = (x_value, result)
            
        except ValueError:
            self.add_result(f"✗ Error: '{x_value_str}' no es un número válido")
        except Exception as e:
            self.add_result(f"✗ Error evaluando: {str(e)}")
        
        self.add_result("")
    
    def plot_function(self):
        """Genera la gráfica de la función - Versión mejorada"""
        self.ax.clear()
        self.add_result("Generando gráfica...")
        
        try:
            # Configuración básica
            x_min, x_max = -10, 10
            num_points = 1000
            
            # Generar puntos para la gráfica
            x_values = []
            y_values = []
            
            # Crear lista de valores x
            step = (x_max - x_min) / num_points
            for i in range(num_points + 1):
                x_val = x_min + i * step
                
                try:
                    # Evaluar la función
                    y_val = self.function.subs(self.x, x_val)
                    y_num = float(y_val.evalf())
                    
                    # Filtrar valores muy grandes o infinitos
                    if abs(y_num) < 100 and not math.isinf(y_num) and not math.isnan(y_num):
                        x_values.append(x_val)
                        y_values.append(y_num)
                        
                except:
                    # Saltar puntos problemáticos
                    continue
            
            if len(x_values) < 10:
                self.ax.text(0.5, 0.5, 'No se pudo generar suficientes puntos\npara la gráfica', 
                           transform=self.ax.transAxes, ha='center', va='center', fontsize=12)
                self.canvas.draw()
                return
            
            # Graficar la función principal
            self.ax.plot(x_values, y_values, 'b-', linewidth=2, label=f'f(x) = {self.function}')
            self.add_result(f"✓ Gráfica generada con {len(x_values)} puntos")
            
            # Marcar intersección con eje Y
            try:
                y_intercept = float(self.function.subs(self.x, 0).evalf())
                if not math.isinf(y_intercept) and not math.isnan(y_intercept):
                    self.ax.plot(0, y_intercept, 'go', markersize=8, 
                               label=f'Eje Y: (0, {y_intercept:.2f})')
            except:
                pass
            
            # Marcar intersecciones con eje X
            try:
                x_intercepts = solve(self.function, self.x)
                for intercept in x_intercepts[:5]:  # Max 5 intersecciones
                    try:
                        if intercept.is_real:
                            x_int = float(intercept.evalf())
                            if x_min <= x_int <= x_max:
                                self.ax.plot(x_int, 0, 'ro', markersize=8, 
                                           label=f'Eje X: ({x_int:.2f}, 0)')
                    except:
                        pass
            except:
                pass
            
            # Marcar punto evaluado
            if self.evaluated_point:
                px, py = self.evaluated_point
                if x_min <= px <= x_max:
                    self.ax.plot(px, py, 'mo', markersize=12, 
                               label=f'Evaluado: ({px}, {py:.2f})')
            
            # Configurar la gráfica
            self.ax.grid(True, alpha=0.3)
            self.ax.axhline(y=0, color='k', linewidth=0.8, alpha=0.7)
            self.ax.axvline(x=0, color='k', linewidth=0.8, alpha=0.7)
            self.ax.set_xlabel('x', fontsize=12, fontweight='bold')
            self.ax.set_ylabel('f(x)', fontsize=12, fontweight='bold')
            self.ax.set_title(f'Gráfica de f(x) = {self.function}', fontsize=14, fontweight='bold')
            
            # Configurar límites del eje Y
            if y_values:
                y_min, y_max = min(y_values), max(y_values)
                y_range = y_max - y_min
                if y_range > 0:
                    margin = 0.1 * y_range
                    self.ax.set_ylim(y_min - margin, y_max + margin)
            
            # Leyenda
            self.ax.legend(loc='best', fontsize=10)
            
            # Actualizar canvas
            self.canvas.draw()
            self.add_result("✓ Gráfica completada")
            
        except Exception as e:
            error_msg = f"Error al generar gráfica: {str(e)}"
            self.add_result(f"✗ {error_msg}")
            self.ax.text(0.5, 0.5, error_msg, 
                        transform=self.ax.transAxes, ha='center', va='center')
            self.canvas.draw()


def main():
    """Función principal"""
    try:
        root = tk.Tk()
        app = FunctionAnalyzer(root)
        root.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        input("Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
