from table import Table
import normalizer
import csv
import sys
from parser import parse_csv
from typing import List

def inputFunDepends(myTable: Table) -> None:

    print()
    cnt = 0
    for col in myTable.columns:
        print(f"{cnt}) {col}")
        cnt += 1
    print(
        "Please enter any valid functional dependencies.\n"
        "Format example: 0,1 -> 2,3"
    )
    done = False
    while not done:
        entry = input(": ")
        if entry.strip() == "":
            return
        if not ("->" in entry):
            print("Try again, there was no '->' in your definition.")
            continue
        splentry = entry.split("->")
        
        deter = splentry[0]
        depend = splentry[1]
        
        spldeter = deter.split(",")
        spldepend = depend.split(",")
        
        try:
            strdeter = [int(attr.strip()) for attr in spldeter]
            strdepend = [int(attr.strip()) for attr in spldepend]
        except ValueError as err:
            print(f"Error in input: {err}")
            continue
        try:
            for i in strdeter:
                myTable.columns[i]
            for i in strdepend:
                myTable.columns[i]
            myTable.funct_depends.append((strdeter, strdepend))
            print(f"Successfully added {[myTable.columns[i] for i in strdeter]} -> {[myTable.columns[i] for i in strdepend]} to the list of functional dependencies.")
        except IndexError as err:
            print(f"Found issue with one or many in entered attributes: {err}")
            continue
        
    
def inputMVDS(myTable: Table) -> None:
    print()
    cnt = 0
    for col in myTable.columns:
        print(f"{cnt}) {col}")
        cnt += 1
    print("Enter any valid multivalued functional dependencies.\nFormat: determinant ->-> dependendent ")
    done = False
    while not done:
        entry = input(": ")
        if entry.strip() == "":
            return
        if not ("->->" in entry):
            print("Didn't find '->' in your defination. Please Try again!")
            continue
        splentry = entry.split("->->")
        
        deter = splentry[0]
        depend = splentry[1]
        
        try:
            numerdert = int(deter.strip())
            numerdepen = int(depend.strip())
        except ValueError as err:
            print(f"Error in input: {err}")
            continue
        
        try:
            myTable.columns[numerdert]
            myTable.columns[numerdepen]
            myTable.multi_funct_depends.append((numerdert, numerdepen))
            print(f"Added {myTable.columns[numerdert]} ->-> {myTable.columns[numerdepen]} to list of functional dependencies.")
        except RuntimeError as err:
            print(f"Found an Issue in your Attributes: {err}")
            continue

def  getPrimaryKey(myTable: Table) -> None:

    print()
    candidate_keys = myTable.get_candidate_keys()
    cnt = 0
    for key in candidate_keys:
        print(f"{cnt}) {[myTable.columns[i] for i in key]}")
        cnt += 1
    print("Enter a candidate key to convert into primary key")
    done = False
    while not done:
        entry = input(": ")
        try:
            nentry = int(entry.strip())
        except ValueError as err:
            print(f"Error in input: {err}")
            continue
            
        try:
            myTable.primary_key = candidate_keys[nentry]
            done = True
        except IndexError as err:
            print(f"Error in input: {err}")
            


def  createTable() -> Table:

    while True:
        print()
        file = input("Input a CSV file with a single table: ")
        try:
            with open(file, 'r') as file:
                csvRead = csv.reader(file)
                csvCols = next(csvRead)
                csvRow = list(csvRead)
                return Table(csvCols, csvRow)
        except FileNotFoundError as err:
            print(err)
        except RuntimeError as err:
            print(err)
            
def findNormalForm(myTable: Table) -> None:

    form = ""
    if not normalizer.is_1nf(myTable):
        form = "It is not in any Normalized Form"
    elif not normalizer.is_2nf(myTable):
        form = "1NF"
    elif not normalizer.is_3nf(myTable):
        form = "2NF"
    elif not normalizer.is_bcnf(myTable):
        form = "3NF"
    elif not normalizer.is_4nf(myTable):
        form = "BCNF"
    else:
        form = "4NF or 5NF"
    
    print("The Highest normal form is:", form)
            
def normalizeToForm(start_table: Table, form: int) -> List[Table]:

    form_cnt = 0
    table_list = [start_table]
    while form_cnt != form:
        print()
        form_cnt += 1
        new_table_list: list[Table] = []
        print_str = ""
        for myTable in table_list:
            if form_cnt == 1:
                print_str = "Normalized 1NF"
                new_table_list += normalizer.firstNormalForm(myTable)
            elif form_cnt == 2:
                print_str = "Normalized 2NF"
                new_table_list += normalizer.secondNormalForm(myTable)
            elif form_cnt == 3:
                print_str = "Normalized 3NF"
                new_table_list += normalizer.thirdNormalForm(myTable)
            elif form_cnt == 4:
                print_str = "Normalized BCNF"
                new_table_list += normalizer.boyceCoddForm(myTable)
            elif form_cnt == 5:
                print_str = "Normalized 4NF"
                new_table_list += normalizer.forthNormalForm(myTable)
            elif form_cnt == 6:
                print_str = "Normalized 5NF"
                new_table_list += normalizer.fifthNormalForm(myTable)
            else:
                raise RuntimeError(f"Runtime err")
        print(f"{print_str}")
        for new_table in new_table_list:
            print()
            new_table.showTable()
            new_table.showPrimaryKey()
            new_table.showFunctionalDependency()
            new_table.showMVD()
        table_list = new_table_list
    return table_list

def main():
    myTable =  createTable()
    
    inputFunDepends(myTable)
    getPrimaryKey(myTable)
    inputMVDS(myTable)
    
    normal_form = int(input(
        "which form you would like to normalize ?\n"
        "1) 1NF\n"
        "2) 2NF\n"
        "3) 3NF\n"
        "4) BCNF\n"
        "5) 4NF\n"
        "6) 5NF\n"
        "Form: "
    ))
    
    find_highest_form = input("Find the highest form of the input table? (1: Yes, 2: No): ")
    
    print("\nOriginal Table")
    myTable.showTable()
    myTable.showPrimaryKey()
    myTable.showFunctionalDependency()
    myTable.showMVD()
    
    normalizeToForm(myTable, normal_form)
    
    if find_highest_form.strip() == "1":
        print()
        findNormalForm(myTable)
    
    # DEBUG

def debug_main(myTable: Table):
    print("\nOriginal Table")
    myTable.showTable()
    myTable.showPrimaryKey()
    myTable.showFunctionalDependency()
    myTable.showMVD()
    
    super_keys = myTable.get_superkeys()
    super_keys.sort(key=len)
    print(f"Super keys: ")
    for key in super_keys:
        print(key)
    candidate_keys = myTable.get_candidate_keys()
    print(f"Candidate keys:")
    for key in candidate_keys:
        print([myTable.columns[i] for i in key])
    
    fnf_tables: list[Table] = normalizer.firstNormalForm(myTable)
    print("\n1NF")
    print(fnf_tables)
    for fnf in fnf_tables:
        fnf.showTable()
        fnf.showFunctionalDependency()
        fnf.showMVD()
    
    snf_tables: list[Table] = []
    for fnf in fnf_tables:
        snf_tables.extend(normalizer.secondNormalForm(fnf))
    
    print("\n2NF")
    for snf in snf_tables:
        snf.showTable()
        snf.showPrimaryKey()
        snf.showFunctionalDependency()
        snf.showMVD()
    
    tnf_tables: list[Table] = []
    for snf in snf_tables:
        tnf_tables.extend(normalizer.thirdNormalForm(snf))
    
    print("\n3NF")
    for tnf in tnf_tables:
        tnf.showTable()
        tnf.showPrimaryKey()
        tnf.showFunctionalDependency()
        tnf.showMVD()
        
    bcnf_tables: list[Table] = []
    for tnf in tnf_tables:
        bcnf_tables.extend(normalizer.boyceCoddForm(tnf))
    
    print("\nBCNF")
    for bcnf in bcnf_tables:
        bcnf.showTable()
        bcnf.showPrimaryKey()
        bcnf.showFunctionalDependency()
        bcnf.showMVD()
    
    fnf_tables: list[Table] = []
    for bcnf in bcnf_tables:
        fnf_tables.extend(normalizer.forthNormalForm(bcnf))
    
    print("\n4NF")
    for fnf in fnf_tables:
        fnf.showTable()
        fnf.showPrimaryKey()
        fnf.showFunctionalDependency()
        fnf.showMVD()

def debug():
    csvCols, csvRow = parse_csv("Company_details.csv")
    myTable = Table(csvCols, csvRow)
    
    myTable.setPrimaryKey(["EmployeeID", "ProjectName", "ProjectManager"])
    
    myTable.setFunctionalDependency(
        (["EmployeeID"], ["FirstName", "LastName", "Department"]),
        (["ProjectName", "ProjectManager"], ["ProjectStart", "ProjectEnd"]),
        (["ProjectManager"], ["ManagerEmail"])
    )
    
    myTable.setMultiValuedFunDependency(
        ("ProjectName", "ProjectManager"),
        ("EmployeeID", "ProjectName"),
        ("EmployeeID", "ProjectManager")
    )
    
    debug_main(myTable)


def debug():
    csvCols, csvRow = parse_csv("library_system.csv")
    myTable = Table(csvCols, csvRow)
    
    myTable.setPrimaryKey(["BookID", "BorrowerID", "BorrowDate"])
    
    myTable.setFunctionalDependency(
        (["BookID"], ["Title", "Author", "ISBN", "Publisher", "PublishYear", "Category"]),
        (["BorrowerID"], ["BorrowerName"]),
        (["StaffID"], ["StaffName", "StaffRole"])
    )
    
    myTable.setMultiValuedFunDependency(
        ("BorrowerID", "BookID"),
        ("BookID", "BorrowDate"),
        ("BookID", "StaffID")
    )

    debug_main(myTable)



if __name__ == "__main__":
    main()
    #debug()
    #debug2()
