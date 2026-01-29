
def merge_sort_amigos(lista_amigos):
    if len(lista_amigos) <= 1:
        return lista_amigos
    
    mitad = len(lista_amigos) // 2
    izquierda = merge_sort_amigos(lista_amigos[:mitad])
    derecha = merge_sort_amigos(lista_amigos[mitad:])
    
    return merge(izquierda, derecha)


def merge(izquierda, derecha):
    resultado = []
    i = 0
    j = 0
    
    while i < len(izquierda) and j < len(derecha):
        nombre_izq = f"{izquierda[i]['nombre']} {izquierda[i]['apellido']}".lower()
        nombre_der = f"{derecha[j]['nombre']} {derecha[j]['apellido']}".lower()
        
        if nombre_izq <= nombre_der:
            resultado.append(izquierda[i])
            i += 1
        else:
            resultado.append(derecha[j])
            j += 1
    
    while i < len(izquierda):
        resultado.append(izquierda[i])
        i += 1
    
    while j < len(derecha):
        resultado.append(derecha[j])
        j += 1
    
    return resultado

