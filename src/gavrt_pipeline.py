# Program to read in GAVRT data files and produce fits files of the individual
# observed objects in the data file.

def rd_gvrtdata(file):
    '''
       Reads in Excel file with GAVRT raw data
    '''

    import openpyxl

    wrk_book = openpyxl.load_workbook(file)
    raw_data = wrk_book.active
    
    return raw_data

datafl = "../data/data_107_2016.xlsx"
rd_table = rd_gvrtdata(datafl)

print rd_table['A1'].value

example_list = [1,2,2,2,2,2,3]
example_set = set(example_list)
print example_set
print len(example_set)