import pandas as pd
import openpyxl, xlsxwriter


def list_sales_to_exel(list_sales: list, date_report: str, count: int, cost_price: int, marginality: float,
                       net_profit: int, dict_order_product: dict, admin: bool = True):
    date_report_ = date_report.replace('/', '.')
    dict_sales = {"№ заказа": [], "дата": [], "время": [], "@username": [], "ключ": [], "стоимость": [],
                  "категория": [], "продукт": [], "тип выдачи": [], "новый ключ": []}
    for sales in list_sales:
        dict_sales["№ заказа"].append(sales[0])
        dict_sales["дата"].append(sales[1])
        dict_sales["время"].append(sales[2])
        dict_sales["@username"].append(sales[3])
        dict_sales["ключ"].append(sales[4])
        dict_sales["стоимость"].append(sales[5])
        dict_sales["категория"].append(sales[6])
        dict_sales["продукт"].append(sales[7])
        dict_sales["тип выдачи"].append(sales[8])
        # dict_sales["номер категории"].append(sales[9])
        dict_sales["новый ключ"].append(sales[10])
    for key in dict_sales.keys():
        print(key, len(dict_sales[key]))
    df_sales = pd.DataFrame(dict_sales)
    if admin:
        dict_report = {"Сумма продаж": [count, None, None], "Себестоимость": [cost_price, None, None],
                       "Маржинальность": [marginality, None, None], "Чистая прибыль": [net_profit, None, None]}
    else:
        dict_report = {}
    for category, dict_poduct in dict_order_product.items():
        dict_report[category] = []
        for product, num in dict_poduct.items():
            dict_report[category].append(f'{product}: {num}')
        for i in range(2):
            if len(dict_report[category]) != 3:
                dict_report[category].append(None)
            else:
                break
    print(dict_report)
    df_report = pd.DataFrame(dict_report)
    # sales_sheets = {f'Продажи за {date_report_}': df_sales, 'Финансовые показатели за': df_report)

    with pd.ExcelWriter(path='./sales.xlsx', engine='xlsxwriter') as writer:
        df_sales.to_excel(writer, sheet_name=f'Продажи {date_report_}', index=False)
        df_report.to_excel(writer, sheet_name=f'Отчет {date_report_}', index=False)
