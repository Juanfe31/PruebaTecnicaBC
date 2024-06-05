Entregable

El repositorio viene con los dos primeros puntos ya ejecutados, "Punto1SQL.py" crea una bd "cliente_tasa.db", esta ya viene creada en el repo, si desea que se cree la bd nuevamente 
elimine la que viene por defecto y ejecute

"Punto2Python.py" crea un excel con tres paginas llamado "ReporteTasasClientesPython.xlxs", la primera contiene la asignacion de tasas y valores finales por obligacion,
la segunda con el agrupado por cliente para los totales y la tercera trae las tasas (esta pagina no se modifica en codigo, es solo infromativa), de igual manera que el punto 1 ya viene con 
el resultado, elimine la que viene por defecto y ejecute

finalmente "Punto3AP.py" necesita de la bd "cliente_tasa.db" para funcionar, se ejecuta y queda activo en el localhost "http://localhost:8000/" este tiene dos posibles llamados ambos consultas
/obligaciones/{num_documento} muestra la información de productos, tasas efectivas y valor final del cliente que sea consultado, pueden ser varios registros
/finales/{num_documento} muestra el valor total del cliente que sea consultado y el numero productos asociados

ej: http://localhost:8000/obligaciones/1032058622
