import openpyxl

def wirteReportInExcelFile(data):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    for i, v in enumerate(data):
        for j in range(len(v)):
            c = sheet.cell(row=i+1, column=j+1)
            c.value = data[i][j]
    workbook.save(filename="report.xlsx")