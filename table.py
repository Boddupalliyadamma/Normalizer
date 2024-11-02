
class Table:
    def __init__(
        self, 
        columns: list[str],
        tuples: 'list[tuple[str]]' = []
    ):
        self.columns: list[str] = columns
        
        self.tuples: 'list[tuple[str]]' = []
        for tuple in tuples:
            self.addTuple(tuple)
        self.primary_key: list[int] = []
        self.funct_depends: 'list[tuple[list[int], list[int]]]'= []
        self.multi_funct_depends: 'list[tuple[int, int]]' = []
        
    def setPrimaryKey(self, attributes: list[str])-> None:
        
        for attr in attributes:
            self.checkAttrWhetherValid(attr)
        
        for attr in attributes:
            self.primary_key.append(self.columns.index(attr))
    
    def checkWhetherSuperKey(self, key: list[int]) -> bool:
        remainAttr = list(range(len(self.columns)))
        
        for attr in key:
            remainAttr.remove(attr)
        if len(remainAttr) == 0:
            return True
        
        effectiveKey = key.copy()
        invariant = True
        while invariant:
            invariant = False
            
            for det, dep in self.funct_depends:
                detEffectiveKey = all(attr in effectiveKey for attr in det)
                if not detEffectiveKey:
                    continue
                depEffectiveKey = all(attr in effectiveKey for attr in dep)
                if depEffectiveKey:
                    continue
                for attr in dep:
                    if attr in remainAttr:
                        remainAttr.remove(attr)
                    if len(remainAttr) == 0:
                        return True 
                    if not (attr in effectiveKey):
                        effectiveKey.append(attr)
                invariant = True
                break
        return False
    
    def superKeyRecursion(self, current_attributes: list[int], superKey: list[list[int]] = []) -> list[list[int]]:
        
        if current_attributes in superKey:
            return superKey
        is_superkey = self.checkWhetherSuperKey(current_attributes)
        if not is_superkey:
            return superKey
        
        superKey.append(current_attributes)
        
        for attr in current_attributes:
            new_attributes = current_attributes.copy()
            new_attributes.remove(attr)
            
            self.superKeyRecursion(new_attributes, superKey)
        return superKey
    
    def getSuperKey(self) -> list[list[int]]:
        currColum = list(range(len(self.columns)))
        supkey = self.superKeyRecursion(currColum, [])
        return supkey
            
    def getCandidateKey(self) -> list[list[int]]:
        superKey = self.getSuperKey()
        superKey.sort(key=len)
        
        candidate_keys: list[list[int]] = []
        
        for i in superKey:
            isCandidateKey = True
            for attr in i:
                temp = i.copy()
                temp.remove(attr)
                if temp in superKey:
                    isCandidateKey = False
                    break
            if isCandidateKey:
                candidate_keys.append(i)
        
        return candidate_keys
            
    def getPrimers(self) -> list[int]:
        candidate_keys = self.getCandidateKey()
        
        primeAttr = []
        for key in candidate_keys:
            primeAttr.extend(attr for attr in key if attr not in primeAttr)
        return primeAttr
    
    def setFunctionalDependency(self, *dependencies: tuple[list[str], list[str]]) -> None:
        for depend in dependencies:
            determ = depend[0]
            determList: list[int] = []
            for attr in determ:
                self.checkAttrWhetherValid(attr)
            dependent = depend[1]
            depend_list: list[int] = []
            for attr in dependent:
                self.checkAttrWhetherValid(attr)
            
            for attr in determ:
                index = self.columns.index(attr)
                determList.append(index)
            for attr in dependent:
                index = self.columns.index(attr)
                depend_list.append(index)
            
            self.funct_depends.append((determList, depend_list))
            
    def getDeterminants(self, dependent: int) -> list[list[int]]:
        determs = []
        for det, dep in self.funct_depends:
            if not (dependent in dep):
                continue
            determs.append(det)
        return determs
    
    def getDepend(self, determ: list[int]) -> list[int]:
        for det, dep in self.funct_depends:
            if determ != det:
                continue
            return dep
        return []
    
    def getPartialDependency(self) -> list[tuple[list[int], list[int]]]:
        
        dependencies: list[tuple[list[int], list[int]]] = []
        
        primes = self.getPrimers()
        candidate_keys = self.getCandidateKey()
        nonPrime = list(range(len(self.columns)))
        for attr in primes:
            nonPrime.remove(attr)
            
        for attr in nonPrime:
            determs = self.getDeterminants(attr)
            
            
            for key in candidate_keys:
                for det in determs:
                    detSubsetKey = all(attr in key for attr in det)
                    if not detSubsetKey:
                        continue
                    detIsKey = det == key
                    if detIsKey:
                        continue
                    
                    dependents = self.getDepend(det)
                    dep: list[int] = []
                    for attr in dependents:
                        if not (attr in primes):
                            dep.append(attr)
                    newDepend = (det, dep)
                    if not (newDepend in dependencies):
                        dependencies.append(newDepend)
                        
        return dependencies
    
    def getDependency(self) -> list[tuple[list[int], list[int]]]:
        dependencies: list[tuple[list[int], list[int]]] = []
       
        primes = self.getPrimers()
        nonPrime = list(range(len(self.columns)))
        for attr in primes:
            nonPrime.remove(attr)
        
        for det, dep in self.funct_depends:
            det_is_non_prime = all(attr in nonPrime for attr in det)
            
            if not det_is_non_prime:
                continue
            dependent: list[int] = []
            for attr in dep:
                if not (attr in primes):
                    dependent.append(attr)
            if len(dependent) == 0:
                continue
            newDepend = (det, dependent)
            if not (newDepend in dependencies):
                dependencies.append(newDepend)
        return dependencies

    def getNONSuperKeyDependency(self) -> list[tuple[list[int], list[int]]]:
        dependencies: list[tuple[list[int], list[int]]] = []
        superKey = self.getSuperKey()
        for det, dep in self.funct_depends:
            detSuperKey = det in superKey
            if not detSuperKey:
                newDepend = (det, dep)
                dependencies.append(newDepend)
        return dependencies
        
    def setMultiValuedFunDependency(self, *dependencies: tuple[int, int]) -> None:
        for depend in dependencies:
            determ = depend[0]
            self.checkAttrWhetherValid(determ)
            dependent = depend[1]
            self.checkAttrWhetherValid(dependent)
            
            detIndex = self.columns.index(determ)
            depIndex = self.columns.index(dependent)
            
            newDepend = (detIndex, depIndex)
            
            self.multi_funct_depends.append(newDepend)
    
    def getMvdDepend(self, determ: int) -> list[int]:
        dependents = []
        for det, dep in self.multi_funct_depends:
            if determ != det:
                continue
            dependents.append(dep)
        return dependents
        
    def checkAttrWhetherValid(self, attr: str) -> None:
        if not (attr in self.columns):
            raise RuntimeError(f"'{attr}' is not a valid attribute")
    
    def addTuple(self, tuple: tuple[str]) -> None:
        if len(tuple) != len(self.columns):
            raise RuntimeError(f"{tuple} values dont line up with {self.columns}")
        self.tuples.append(tuple)
    
    def addTuples(self, tuples: list[tuple[str]]) -> None:
        for tuple in tuples:
            self.addTuple(tuple)
    
    def deleteTuple(self, primary_key: tuple) -> None:
        searchTuple = self.tuples.copy()
        if len(primary_key) != len(self.primary_key):
            raise RuntimeError(f"{primary_key} values dont line up with {self.primary_key}")
        for i in range(len(primary_key)):
            tupleMatch = []
            pkIndex = self.primary_key[i]
            for tuple in searchTuple:
                if tuple[pkIndex] == primary_key[i]: 
                    tupleMatch.append(tuple)
            searchTuple = tupleMatch.copy()
        if len(searchTuple) == 0:
            raise RuntimeError(f"No tuple found with PK {primary_key}")
        if len(searchTuple) != 1:
            raise RuntimeError(f"PK {primary_key} does not uniquely describe tuple, returned {searchTuple}")
        self.tuples.remove(searchTuple[0])
    
    def getColum(self, indexes: list[int]) -> str:
        string = ""
        
        element = self.columns[indexes[0]]
        string += element
        for i in indexes[1:]:
            string += f", {self.columns[i]}"
        
        return string

    def showTable(self) -> None:
        header = ' | '.join(self.columns)
        print(header)

        separator = '+'.join('-' * (len(col) + 2) for col in self.columns)
        print(separator)


        for row in self.tuples:
            formatted_row = ' | '.join(str(col) for col in row)
            print(formatted_row)

        print(separator)
    
    def showPrimaryKey(self) -> None:
        pk_str = self.getColum(self.primary_key)
        print(f"PK: {{ {pk_str} }}")

    def showFunctionalDependency(self) -> None:
        if len(self.funct_depends) == 0:
            return
        print("Functional dependencies:")
        for depend in self.funct_depends:
            determ = depend[0]
            determ_str = self.getColum(determ)
            
            depenant = depend[1]
            depend_str = self.getColum(depenant)
            
            print(f" - {determ_str} -> {depend_str}")
    
    def showMVD(self) -> None:
        if len(self.multi_funct_depends) == 0:
            return
        print("Multivalue Functional dependencies:")
        for depend in self.multi_funct_depends:
            determ = depend[0]
            determ_str = self.getColum([determ])
            
            depenant = depend[1]
            depend_str = self.getColum([depenant])
            print(f" - {determ_str} -> {depend_str}")

    def get_join_dependencies(self) -> list[tuple[list[int], list[int]]]:
        join_dependencies: list[tuple[list[int], list[int]]] = []
        
        for det, dep in self.funct_depends:
            if all(attr in self.columns for attr in det + dep):
                join_dependencies.append((det, dep))
                
        return join_dependencies



