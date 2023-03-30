def str_to_address(server_addr):
    list_aux = server_addr.split(':')
    list_aux[1] = int(list_aux[1])

    return tuple(list_aux)

def construct_payload(rows):
    return [','.join(e) for e in rows]