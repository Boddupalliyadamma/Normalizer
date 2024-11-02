

import table

def CreateTablewithFunDepend(old_table: table.Table, funct_depend: tuple[list[int], list[int]]) -> table.Table:
    table_funct_depends: list[tuple[list[int], list[int]]] = []
    if len(funct_depend[1]) != 0:
        table_funct_depends.append(funct_depend)
    table_mvds: list[tuple[int, int]] = []
    table_columns: list[int] = []

    det, dep = funct_depend
    dependAttr = det.copy()
    dependAttr.extend(dep.copy())
    table_columns.extend(dependAttr)
    
    for attr in table_columns:
        mvdDepend = old_table.getMvdDepend(attr)
        if len(mvdDepend) == 0:
            continue
        for attr in mvdDepend:
            if not attr in table_columns:
                continue
            new_mvd = (attr, attr)
            table_mvds.append(new_mvd)

    for det, dep in old_table.funct_depends:
        colDeter = all(attr in table_columns for attr in det)
        if colDeter:
            new_dependents: list[int] = []
            for attr in dep:
                if not (attr in table_columns):
                    continue
                new_dependents.append(attr)
            if len(new_dependents) == 0:
                continue
            newDepend = (det, new_dependents)
            if newDepend in table_funct_depends:
                continue
            table_funct_depends.append(newDepend)

    newTable= constructTable(
        old_table=old_table, 
        new_col_indexes=table_columns, 
        primary_key=funct_depend[0], 
        funDependency=table_funct_depends,
        multiValuedAttr=table_mvds
        )
    
    return newTable

def createTablefromColum(old_table: table.Table, table_columns: list[int]) -> table.Table:
    table_funct_depends: list[tuple[list[int], list[int]]] = []
    table_mvds: list[tuple[int, tuple[int, int]]] = []
    
    for attr in table_columns:
        mvdDepend = old_table.getMvdDepend(attr)
        if len(mvdDepend) == 0:
            continue
        for attr in mvdDepend:
            if not attr in table_columns:
                continue
            new_mvd = (attr, attr)
            table_mvds.append(new_mvd)

    for det, dep in old_table.funct_depends:
        colDeter = all(attr in table_columns for attr in det)
        if colDeter:
            new_dependents: list[int] = []
            for attr in dep:
                if not (attr in table_columns):
                    continue
                new_dependents.append(attr)
            if len(new_dependents) == 0:
                continue
            newDepend = (det, new_dependents)
            if newDepend in table_funct_depends:
                continue
            table_funct_depends.append(newDepend)

   
    newTable= constructTable(
        old_table=old_table, 
        new_col_indexes=table_columns, 
        primary_key=[], 
        funDependency=table_funct_depends,
        multiValuedAttr=table_mvds
        )
    return newTable

def transformIndex(index: int, old_columns: list[str], newColum: list[str]) -> int:
    oldCol = old_columns[index]
    newIndex = newColum.index(oldCol)
    return newIndex

def constructTable(
    old_table: table.Table,
    new_col_indexes: list[int],
    primary_key: list[int],
    funDependency: list[tuple[list[int], list[int]]],
    multiValuedAttr: list[tuple[int, int]]
    ) -> table.Table:
    new_col_indexes.sort()
    newColum = [old_table.columns[i] for i in new_col_indexes]
    newTable= table.Table(newColum)
    for det, dep in funDependency:
        newDeter = [transformIndex(i, old_table.columns, newTable.columns) for i in det]
        newDepend = [transformIndex(i, old_table.columns, newTable.columns) for i in dep]
        newTable.funct_depends.append((newDeter, newDepend))
    for det, dep in multiValuedAttr:
        newDeter = transformIndex(det, old_table.columns, newTable.columns)
        newDepend = transformIndex(dep, old_table.columns, newTable.columns)
        newTable.multi_funct_depends.append((newDeter, newDepend))
    
    if len(primary_key) == 0:
        candidate_keys = newTable.get_candidate_keys()
        if len(candidate_keys) == 0:
            raise RuntimeError(
                "A new table was constructed with no explicit primary key, and there are no valid keys that have been found\n"
                "Run Time Error"
                )
        newPrimaryKey = candidate_keys[0]
    else:
        newPrimaryKey = [transformIndex(i, old_table.columns, newTable.columns) for i in primary_key]
    newTable.primary_key = newPrimaryKey

    for tup in old_table.tuples:
        new_tuple: tuple[str] = tuple([tup[i] for i in new_col_indexes])
        if not (new_tuple in newTable.tuples):
            newTable.addTuple(new_tuple)
    return newTable

def is_1nf(my_table: table.Table) -> bool:
    for tuple in my_table.tuples:
        for value in tuple:
            if " " in value:
                return False
    return True

def firstNormalForm(my_table: table.Table) -> list[table.Table]:
    newTable = table.Table(my_table.columns)
    newTable.primary_key = my_table.primary_key
    newTable.funct_depends = my_table.funct_depends
    newTable.multi_funct_depends = my_table.multi_funct_depends
    
    new_tuples: 'list[tuple]' = []
    
    for tuple in my_table.tuples:
        new_tuples.append(tuple)
        for value in tuple:
            if not (" " in value):
                continue
            if tuple in new_tuples:
                new_tuples.remove(tuple)
            
            valIndex = tuple.index(value)
            valueList = value.split()
            for val in valueList:
                newTuple = list(tuple)[:valIndex] + [val] + list(tuple)[valIndex+1:]
                new_tuples.append(newTuple)
    newTable.addTuples(new_tuples)
    
    return [newTable]

def is_2nf(my_table: table.Table) -> bool:
    partialDepend = my_table.getPartialDependency()
    
    return len(partialDepend) == 0

def secondNormalForm(my_table: table.Table) -> list[table.Table]:
    new_dependencies: 'list[tuple[list[int], list[int]]]' = my_table.getPartialDependency()
    
    keyNotInDependency = all(my_table.primary_key != funct_depend[0] for funct_depend in new_dependencies)
    if keyNotInDependency:
        pkDepend = my_table.get_dependents(my_table.primary_key)
        for attr in pkDepend:
            for det, dep in new_dependencies:
                if attr in dep:
                    pkDepend.remove(attr)
        new_dependencies.append((my_table.primary_key, pkDepend))
    
    newTables: list[table.Table] = []
    for funct_depend in new_dependencies:
        newTable = CreateTablewithFunDepend(my_table, funct_depend)
        
        newTables.append(newTable)

    return newTables

def is_3nf(my_table: table.Table) -> bool:
    transitive_dependencies = my_table.getDependency()
    
    return len(transitive_dependencies) == 0

def thirdNormalForm(my_table: table.Table) -> list[table.Table]:
    new_dependencies: 'list[tuple[list[int], list[int]]]' = my_table.getDependency()
    
    pkDepend = my_table.get_dependents(my_table.primary_key)
    for attr in pkDepend:
        for det, dep in new_dependencies:
            if attr in dep:
                pkDepend.remove(attr)
    new_dependencies.append((my_table.primary_key, pkDepend))
    
    newTables: list[table.Table] = []
    for funct_depend in new_dependencies:
        newTable = CreateTablewithFunDepend(my_table, funct_depend)
        
        newTables.append(newTable)

    return newTables

def is_bcnf(my_table: table.Table) -> bool:
    non_superkey_dependencies = my_table.getNONSuperKeyDependency()
    
    return len(non_superkey_dependencies) == 0

def boyceCoddForm(my_table: table.Table) -> list[table.Table]:
    new_dependencies: 'list[tuple[list[int], list[int]]]' = my_table.getNONSuperKeyDependency()
    
    if len(new_dependencies) == 0:
        return [my_table]
    
    newFunDepend = new_dependencies[0]
    xa = CreateTablewithFunDepend(my_table, newFunDepend)
    newColum = list(range(len(my_table.columns)))
    for attr in newFunDepend[1]:
        newColum.remove(attr)
    finalFifth = createTablefromColum(my_table, newColum)
    
    newTables: list[table.Table] = []
    newTables.extend(boyceCoddForm(xa))
    newTables.extend(boyceCoddForm(finalFifth))
    
    return newTables

def is_4nf(my_table: table.Table) -> bool:
    if len(my_table.multi_funct_depends) == 0:
        return True
    new_mvd = my_table.multi_funct_depends[0]
    super_keys = my_table.get_superkeys()
    if [new_mvd[0]] in super_keys:
        return True
    
    return False

def forthNormalForm(my_table: table.Table) -> list[table.Table]:
    if len(my_table.multi_funct_depends) == 0:
        return [my_table]
    new_mvd = my_table.multi_funct_depends[0]
    super_keys = my_table.get_superkeys()
    if [new_mvd[0]] in super_keys:
        return [my_table]
    
    newFunDepend = ([new_mvd[0]], [new_mvd[1]])
    xa = constructTable(
        old_table=my_table, 
        new_col_indexes=[new_mvd[0], new_mvd[1]], 
        primary_key=[], 
        funDependency=[],
        multiValuedAttr=[]
        )
    
    newColum = list(range(len(my_table.columns)))
    newColum.remove(new_mvd[1])
    if len(newColum) == 2:
        finalFifth = constructTable(
            old_table=my_table, 
            new_col_indexes=newColum, 
            primary_key=[], 
            funDependency=[],
            multiValuedAttr=[]
        )
    else:
        finalFifth = createTablefromColum(my_table, newColum)
    
   
    newTables: list[table.Table] = []
    newTables.extend(forthNormalForm(xa))
    newTables.extend(forthNormalForm(finalFifth))

    return newTables


def fifthNormalForm(my_table: table.Table) -> list[table.Table]:
    join_dependencies = my_table.get_join_dependencies()
    
    if not join_dependencies:
        return [my_table]
    
    decomposed_tables = []

    for jd in join_dependencies:
        columns_group1, columns_group2 = jd

        table1_columns = list(set(columns_group1).union(set(my_table.primary_key)))
        table1 = createTablefromColum(my_table, table1_columns)

        table2_columns = list(set(columns_group2).union(set(my_table.primary_key)))
        table2 = createTablefromColum(my_table, table2_columns)

        decomposed_tables.extend(fifthNormalForm(table1))
        decomposed_tables.extend(fifthNormalForm(table2))

    return decomposed_tables
