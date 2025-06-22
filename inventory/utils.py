
def update_product_stock(product):
    product.current_stock = product.godown_stock + product.office_stock
    product.save()

def transfer_to_office_stock(product, required_qty):
    if product.office_stock >= required_qty:
        return True
    
    needed = required_qty - product.office_stock

    if product.godown_stock >= needed:
        product.godown_stock -= needed
        product.office_stock += needed
        update_product_stock(product)
        return True
    return False

def reduce_office_stock(product, qty):
    if not transfer_to_office_stock(product, qty):
        raise ValueError(f"There is not enough stock in the warehouse for {product.name}.")
    if product.office_stock < qty:
        raise ValueError(f"There are not enough products in the office stock for {product.name}.")
    
    product.office_stock -= qty
    update_product_stock(product)