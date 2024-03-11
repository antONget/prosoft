import gspread
import logging

gp = gspread.service_account(filename='services/ostatli-telegram-bot.json')
# gp = gspread.service_account(filename='services/test.json')

#Open Google spreadsheet
# gsheet = gp.open('prosoft_1')
gsheet = gp.open('Ключи')


# select worksheet
office_sheet = gsheet.worksheet("Ключи Office ")
office365_sheet = gsheet.worksheet("Ключи Office  365")
windows_sheet = gsheet.worksheet("Ключи Windows")
project_sheet = gsheet.worksheet("Ключи Project")
visio_sheet = gsheet.worksheet("Ключи Visio")
order_sheet = gsheet.worksheet("Заказы")
cost_sheet = gsheet.worksheet("Стоимость")

dict_category = {
    "office": office_sheet,
    "Office 365": office365_sheet,
    "windows": windows_sheet,
    "project": project_sheet,
    "visio": visio_sheet
}

def get_list_product(category):
    sheet = dict_category[category]
    values = sheet.get_all_values()
    list_product = []
    for item in values[0]:
        if item != '':
            # print(item)
            list_product.append(item)
    return list_product


def get_list_orders():
    values = order_sheet.get_all_values()
    list_orders = []
    for item in values:
        list_orders.append(item)
    return list_orders

def get_key_product(category: str, product: int) -> list:
    logging.info(f'get_key_product')
    print("product:", product)
    sheet = dict_category[category]
    values = sheet.get_all_values()
    list_key = []
    for i, item in enumerate(values):
        # print(item[product:product+7])
        slice_item = item[product*7:product*7+7]
        slice_item.append(i)
        list_key.append(slice_item)
    return list_key


def get_info_order(id_order: str) -> list:
    logging.info(f'get_info_order')
    values = order_sheet.get_all_values()
    for i, item in enumerate(values):
        if id_order in item:
            return item
    return False


def get_key_product_office365(category: str) -> list:
    logging.info(f'get_key_product_office365')
    sheet = dict_category[category]
    values = sheet.get_all_values()
    list_key = []
    for i, item in enumerate(values):
        slice_item = item[:3]
        slice_item.append(i)
        list_key.append(slice_item)
    return list_key


def get_cost_product(product: str, typelink: str = 'None') -> str:
    logging.info(f'get_cost_product, {product}:{typelink}')
    values = cost_sheet.get_all_values()
    cost_key = 0
    product = product.strip()
    for row, item in enumerate(values):
        print(item[:2], product in item[:3], 'online' in typelink, item[1] == 'online')
        if product in item[:3] and 'online' in typelink and item[1] == 'online':
            print(1, item[4])
            cost_key = item[4]
        elif product in item[:3] and 'phone' in typelink and item[1] == 'phone':
            print(2, item[4])
            cost_key = item[4]
        elif product in item[:3] and 'linking' in typelink and item[1] == 'linking':
            print(3, item[4])
            cost_key = item[4]
        else:
            if product == 'Office 365' and item[1] == 'None':
                cost_key = item[4]
                print(4, item[4])
    print(cost_key)
    return cost_key


# добавить значения
def append_order(id_order, date, time, username, key, cost, category, product, type_give, id_product=-1):
    logging.info(f'append_order')
    order_sheet.append_row([id_order, date, time, username, key, cost, category, product, type_give, id_product])


def update_row_key_product(category: str, id_product_in_category: int, id_key: int) -> None:
    logging.info(f'update_row_key_product')
    sheet = dict_category[category]
    values_list = sheet.row_values(id_key+1)[id_product_in_category*7:id_product_in_category*7+7]
    print(values_list)
    if id_product_in_category >= 0:
        for i, value in enumerate(values_list):
            if value == '✅':
                col = i + 7 * id_product_in_category
                print(id_key+1, col)
                sheet.update_cell(id_key+1, col+1, '❌')
                break
    else:
        sheet.update_cell(id_key+1, 2, '❌')


def update_row_key_product_cancel(category: str, key: str) -> None:
    logging.info(f'update_row_key_product_cancel: {key}')
    sheet = dict_category[category]

    if category == 'Office 365':
        value_list = sheet.get_all_values()
        for i, row_value in enumerate(value_list):
            if key in row_value[0]:
                sheet.update_cell(i+1, 2, '✅')
    else:
        cell = sheet.find(key)
        print(cell.row, cell.col)
        for i in range(7):
            # print(sheet.cell(cell.row, cell.col+1+i).value)
            if sheet.cell(cell.row, cell.col+1+i).value == '❌':
                sheet.update_cell(cell.row, cell.col+1+i, '✅')
                break


def delete_row_order(id_order: str) -> None:
    logging.info(f'delete_row_order {id_order}')
    cell = order_sheet.find(id_order)
    order_sheet.delete_rows(cell.row)


def update_row_order_listkey(id_order: str, listkey: str) -> None:
    logging.info(f'delete_row_order {id_order}')
    cell = order_sheet.find(id_order)
    order_sheet.update_cell(cell.row, 5, listkey)

def update_row_key_product_new_key(new_key:str, id_order: str) -> None:
    logging.info(f'update_row_key_product_new_key')
    values_list = order_sheet.get_all_values()
    for row, order in enumerate(values_list):
        if order[0] == id_order:
            col = 11
            if not order_sheet.cell(row+1, 11).value:
                order_sheet.update_cell(row+1, col, new_key)
            else:
                col += 1
                order_sheet.update_cell(row + 1, col, new_key)


# поиск строки и столбца положения значения
def values_row_col():
    values = office_sheet.get_all_values()
    print(values)


def get_values_hand_product(product) -> str:
    logging.info(f'get_values_hand_product')
    values_list = cost_sheet.get_all_values()
    cell = cost_sheet.find('Ключ по запросу')
    for row, notes in enumerate(values_list[cell.row:]):
        # print(product, notes[2])
        if product in notes[2]:
            # print(cell.row, cell.col)
            print(cost_sheet.cell(row+22, 5).value)
            return cost_sheet.cell(row+22, 5).value
        if notes[2] == '':
            break



if __name__ == '__main__':
    get_key_product(category='windows', product=0)
