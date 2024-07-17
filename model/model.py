import copy
import random

import networkx as nx


class Model:
    def __init__(self):
        self._grafo = None

# --------------------------------------------------------------------------------------------------------------

# BASEBALL

    def getBestPath(self, v0):
        """
      Calcoli un PERCORSO DI PESO MASSIMO avente le seguenti caratteristiche:
      •Il PUNTO DI PARTENZA è il vertice selezionato al punto 1.e.
      •OGNI VERTICE PUÒ COMPARIRE UNA SOLA VOLTA
      •Il PESO degli archi nel percorso deve essere STRETTAMENTE DECRESCENTE.
      """
        self._solBest = []
        self._totCosto = 0

        parziale = [v0]
        listaVicini = []
        for v in self._grafo.neighbors(v0):
            pesoV = self._grafo[v0][v]['weight']
            listaVicini.append((v, pesoV))
        listaVicini.sort(key=lambda x: x[1], reverse=True)

        parziale.append(listaVicini[0][0])
        self._ricorsioneV2(parziale)
        parziale.pop()
        return self.getWeightOfPath(self._solBest)

        # Per ottenere la lista di nodi con i suoi pesi, possiamo usare il metodo getWeightOfPath

    def getWeightOfPath(self, path):
        listTuples = [(path[0], 0)]
        for i in range(len(path) - 1):
            listTuples.append((path[i + 1], self._grafo[path[i]][path[i + 1]]['weight']))
        return listTuples

    def _ricorsioneV2(self, parziale):
        # caso terminale
        if self._calcolaPeso(parziale) > self._totCosto:
            self._solBest = copy.deepcopy(parziale)
            self._totCosto = self._calcolaPeso(parziale)

        # per ottimizzare la ricorsione siccome non abbiamo un caso terminale specifico,
        # possiamo usare la lista dei vicini del nodo corrente e ordinarla per peso decrescente
        # e poi iterare su di essa
        listaVicini = []
        for v in self._grafo.neighbors(parziale[-1]):
            pesoV = self._grafo[parziale[-1]][v]['weight']
            listaVicini.append((v, pesoV))

        listaVicini.sort(key=lambda x: x[1], reverse=True)

        for v1 in listaVicini:
            if (v1[0] not in parziale and
                    v1[1] < self._grafo[parziale[-2]][parziale[-1]]['weight']):
                parziale.append(v1[0])
                self._ricorsioneV2(parziale)
                parziale.pop()
                return  # se non mettiamo il return, la ricorsione continua a scendere e non si ferma

    def _calcolaPeso(self, listOfNodes):
        if len(listOfNodes) == 1:
            return 0
        peso = 0
        for i in range(len(listOfNodes) - 1):
            peso += self._grafo[listOfNodes[i]][listOfNodes[i + 1]]['weight']
        return peso

# --------------------------------------------------------------------------------------------------------------

# ARTS MIA

# Per calcolare la COMPONENTE CONNESSA conviene usare DFS e siccome ci interessano i numeri di vertici che la compongono
# come richiesto nella traccia, non conviene utilizzare dfs_edges perchè restituisce solo gli archi del grafo. Proviamo
# invece a utilizzare
# 1) dfs_successors che restituisce un dizionario con i successori di ogni nodo visitato.
# 2) dfs_predecessors che restituisce un dizionario con i predecessori di ogni nodo visitato.
# 3) dfs_tree che restituisce un albero di copertura del grafo.
# 4) node_connected_component che restituisce la componente connessa di un nodo.
# Siccome il grafo non è orientato, prendere i successori o i predecessori è indifferente. L'unica differenza è che
# dfs_successors restituisce un dizionario con come chiave un nodo e come valore una lista di tutti i suoi successori
# (vedi debug per capire meglio) mentre dfs_predecessors ha come valore per ogni chiave il singolo nodo predecessore,
# siccome il noto in chiave sarà stato raggiunto da un solo altro nodo.
# Facendo il testModel e debuggando len(successors.values) e len(predecessors.values) si nota quindi che il numero
# risultante è minore per i predecessori rispetto ai successori(perchè gli elementi values di successori sono liste di nodi).
    def getCompConnessa(self, idOggetto):
        # return nx.node_connected_component(self._grafo, self._idMap[idOggetto])
        #  Metodo 1) dfs_successors
        v0 = self._idMap[idOggetto]
        # Per separare i nodi memorizzati nelle liste e metterli separatamente tutti in'unica lista uso il metodo extend
        # che prende come argomento un iterabile e lo aggiunge alla lista.
        allSucc = []
        successors = nx.dfs_successors(self._grafo, v0)
        for v in successors.values():
            allSucc.extend(v)
        print(f"Metodo 1 (succ): {len(allSucc)}")

        # Metodo 2) dfs_predecessors
        predecessors = nx.dfs_predecessors(self._grafo, v0)
        print(f"Metodo 2 (pred): {len(predecessors.values())}")

        # Metodo 3) dfs_tree
        tree = nx.dfs_tree(self._grafo,
                           v0)  # restituisce un albero di copertura del grafo, contiene anche il nodo source, q
        # quindi risulterà avere un nodo in più rispetto ai precedenti metodi
        print(f"Metodo 3 (tree): {len(tree.nodes)}")

        # Metodo 4) node_connected_component
        compCon = nx.node_connected_component(self._grafo,
                                              v0)  # restituisce un set di nodi, anche questo contiene il nodo source
        print(f"Metodo 4 (node_connected_component): {len(compCon)}")

        return len(compCon)  # restituisco il numero di nodi della componente connessa, come richiesto nella traccia

    def getBestPath(self, lunghezza, source):
        """
        Il programma dovrà cercare il cammino di peso massimo, avente lunghezza pari a lunghezza, il cui vertice iniziale coincida
        con il vertice selezionato idOggetto, che comprenda esclusivamente vertici che abbiano tutti la stessa classification.
        """
        self._solBest = []
        self._costBest = 0
        parziale = [source]
        for v in self._grafo.neighbors(source):
            parziale.append(v)
            self.ricorsiva(parziale, lunghezza)
            parziale.pop()
        return self._costBest, self._solBest

    def ricorsiva(self, parziale, lunghezza):
        # caso terminale, controllo se parziale è una soluzione valida e se è migliore del best trovato finora
        if len(parziale) == lunghezza:
            peso = self.calcolaPeso(parziale)
            if peso > self._costBest:
                self._costBest = peso
                self._solBest = copy.deepcopy(parziale)
            return
        # caso ricorsivo, se arrivo qui allora len(parziale) < lunghezza
        ultimo = parziale[-1]
        for vicino in self._grafo.neighbors(ultimo):
            # vincolo: vicino lo aggiungo solo se ha la stessa classification dell'ultimo nodo inserito in parziale
            if vicino.classification == ultimo.classification and vicino not in parziale:
                parziale.append(vicino)
                self.ricorsiva(parziale, lunghezza)
                parziale.pop()

    def calcolaPeso(self, listObj):
        peso = 0
        # per calcolare il peso del cammino, sommo i pesi degli archi che collegano i nodi del cammino
        for i in range(0, len(listObj) - 1):
            peso += self._grafo[listObj[i]][listObj[i + 1]]['weight']
        return peso

    def getObjFromId(self, idOggetto):
        return self._idMap[idOggetto]

# --------------------------------------------------------------------------------------------------------------

# FLIGHT DELAYS
# guardare anche la mia versione di ricorsione su git se serve

    # Con Dijkstra troverò il cammino con peso minore tra due nodi
    def trovaCamminoDijkstra(self, aP, aA):
        return nx.dijkstra_path(self._grafo, aP, aA)

    # Con BFS troverò il cammino più corto tra due nodi, non necessariamente con peso minore
    def trovaCamminoBFS(self, aP, aA):
        tree = nx.bfs_tree(self._grafo, aP)
        # Costruiamo il cammino a partire da aA, quindi aP sarà l'ultimo elemento,
        # partiamo dalla foglia e risaliamo al nodo radice
        if aA in tree:
            print(f"{aA} è presente nell'albero di vista BFS")
        path = [aA]
        while path[-1] != aP:
            parent = list(tree.predecessors(path[-1]))[0]
            path.append(parent)
        # Perciò invertiamo il cammino
        path.reverse()
        return path

    # Con DFS troverò il cammino più lungo tra due nodi, non necessariamente con peso maggiore
    def trovaCamminoDFS(self, aP, aA):
        tree = nx.dfs_tree(self._grafo, aP)
        if aA in tree:
            print(f"{aA} è presente nell'albero di vista DFS")
        path = [aA]
        while path[-1] != aP:
            parent = list(tree.predecessors(path[-1]))[0]
            path.append(parent)

        path.reverse()
        return path

    # Fatto dal professore

    def getBestItinerary(self, aP, aA, tratteMax):
        self._bestItinerary = []
        self._bestItineraryWeight = 0
        parziale = [aP]
        # for v in self._grafo.neighbors(aP):
        #   parziale.append(v)
        self.ricorsiva(parziale, aA, tratteMax)
        #   parziale.pop()
        return self._bestItinerary, self._bestItineraryWeight

    def ricorsiva(self, parziale, target, tratteMax):
        """
        Cercare l’itinerario di viaggio tra a1 e a2 che massimizzi il numero totale di voli per ciascuna delle tratte del percorso selezionato
        (in altre parole, il percorso che massimizzi la somma dei pesi degli archi attraversati), utilizzando al massimo t tratte.
         """
        # CASO TERMINALE
        # Verificare che parziale sia una soluzione ammissibile
        if len(parziale) == tratteMax + 1:
            return
        # Verificare se la soluzione trovata è migliore di quella attuale
        peso = self.calcolaPeso(parziale)
        if (peso > self._bestItineraryWeight
                and parziale[-1] == target):
            self._bestItinerary = copy.deepcopy(parziale)
            self._bestItineraryWeight = peso

        # CASO RICORSIVO
        # Posso ancora aggiungere nodi
        ultimoNodo = parziale[-1]  # ultimo nodo che ho aggiunto
        # Prendo i vicini dell'ultimo nodo e provo ad aggiungerli
        for vicino in self._grafo.neighbors(ultimoNodo):
            # Tipicamente qua inserisco dei vincoli, per esempio questo:
            if vicino not in parziale:
                # Ma nel nostro caso non è richisto dalla traccia alcun vincolo
                parziale.append(vicino)
                # Ricorsione
                self.ricorsiva(parziale, target, tratteMax)
                parziale.pop()

    def calcolaPeso(self, listOfNodes):
        peso = 0
        for i in range(1, len(listOfNodes)):
            peso += self._grafo[listOfNodes[i - 1]][listOfNodes[i]]['weight']
        return peso

# --------------------------------------------------------------------------------------------------------------

# ITUNES

    def getSetAlbum(self, a1, soglia):
        self._solBest = None
        self._totCosto = 0
        connessa = nx.node_connected_component(self._grafo, a1)
        parziale = set([a1])
        connessa.remove(a1)

        self._ricorsione(parziale, connessa, soglia)

        return self._solBest, self.calcolaPeso(self._solBest)

    def _ricorsione(self, parziale, connessa, soglia):
        """
        Utilizzare un algoritmo ricorsivo per estrarre UN SET di album dal grafo che abbia le seguenti caratteristiche:
            • includa a1;
            • includa solo album appartenenti alla stessa componente connessa di a1;
            • includa il maggior numero possibile di album;
            • abbia una durata complessiva, definita come la somma della durata degli album in esso contenuti, non superiore dTOT.
        """
        # CASO TERMINALE
        # 1) Verificare che parziale sia una soluzione ammissibile
        # Questo controllo devo farlo prima di salvare la soluzione ottima, altrimenti rischio di
        # salvare una soluzione non ammissibile
        if self.calcolaPeso(parziale) > soglia:
            return
        # 2) Verificare se la soluzione trovata è migliore di quella attuale
        if len(parziale) > self._totCosto:
            self._solBest = copy.deepcopy(parziale)
            self._totCosto = len(parziale)

        # 3) CASO RICORSIVO
        # Posso ancora aggiungere nodi
        # 4) Prendo i vicini dell'ultimo nodo e provo ad aggiungerli
        for nodo in connessa:
            # Tipicamente qua inserisco dei vincoli, per esempio questo:
            if nodo not in parziale:
                parziale.add(nodo)
                # Per accorciare i cicli dentro la ricorsione posso fare una copia di connessa e rimuovere il nodo
                # che ho appena aggiunto a parziale, in modo da non ripassare su di esso
                # rimanenti = copy.deepcopy(connessa)
                # rimanenti.remove(nodo)
                self._ricorsione(parziale, connessa, soglia)
                parziale.remove(nodo)

    def calcolaPeso(self, listOfNodes):
        dtot = 0
        for a in listOfNodes:
            dtot += a.totDurata
        # oppure
        # return sum([a.totDurata for a in listOfNodes]) / 60000
        return dtot / 60000

# --------------------------------------------------------------------------------------------------------------

# NYC-HOTSPOTS

# vedere per l'aggiunta di archi con condizione di distanza
# vedere per la ricerca dei vertici del grafo che hanno IL MAGGIOR NUMERO DI VICINI.
    def getCammino(self, target, substring):
        sources = self.getNodesMostVicini()
        source = sources[random.randint(0, len(sources) - 1)][0]

        if nx.has_path(self._grafo, source, target):
            print(f"Cammino tra {source} e {target} esiste")
        else:
            print(f"Cammino tra {source} e {target} NON esiste")
            return [], source

        self._bestPath = []
        self._bestLength = 0
        parziale = [source]
        self._ricorsione(parziale, target, substring)

        return self._bestPath, source

    def _ricorsione(self, parziale, target, substring):
        """
        Trovare (se esiste), un cammino aciclico semplice che abbia le seguenti caratteristiche:
• INIZI DA una delle località calcolate al punto 1d (scelta in modo casuale) E TERMINI IN T;
• TOCCHI IL MAGGIOR NUMERO DI LOCALITÀ;
• non passi per località il cui nome contenga la sottostringa s.
        """
        if parziale[-1] == target:
            if len(parziale) > len(self._bestPath):
                self._bestPath = copy.deepcopy(parziale)
                self._bestLength = len(parziale)
            return

        for v in self._grafo.neighbors(parziale[-1]):
            if v not in parziale and v.Location.find(substring) != -1:
                parziale.append(v)
                self._ricorsione(parziale, target, substring)
                parziale.pop()
# --------------------------------------------------------------------------------------------------------------

# METRO PARIS
    # vari modi di trovare gli archi
    # + questa roba
    @staticmethod
    def getTraversalTime(v0, v1, linea):
        p0 = (v0.coordX, v0.coordY)
        p1 = (v1.coordX, v1.coordY)
        distanza = distance(p0, p1).km
        vel = linea.velocita
        tempo = distanza / vel * 60  # tempo in minuti
        return tempo

    # calcola il percorso migliore tra due fermate utilizzando l'algoritmo di Dijkstra
    # per ottenere la lista dei nodi percorsi per raggiungere la destinazione, come richiesto dalla traccia
    def getBestPath(self, source, target):
        """
        Calcola il percorso migliore tra due fermate utilizzando l'algoritmo di Dijkstra.
        """
        path = nx.dijkstra_path(self._grafo, source, target, weight="weight")
        return path

    # se volessi ottenere anche il costo minimo (tempo totale) per raggiungere la destinazione, posso utilizzare la funzione nx.dijkstra_path_length
    # oppure direttamente nx.single_source_dijkstra(self._grafo, source, target) che appunto mi
    # restituisce sia il costo minimo che il percorso (in quest'ordine in una tupla) per raggiungere la destinazione.
    def getBestPathAndCost(self, source, target):
        """
        Calcola il percorso migliore tra due fermate utilizzando l'algoritmo di Dijkstra e restituisce il costo minimo per raggiungere la destinazione.
        """
        costoTot, path = nx.single_source_dijkstra(self._grafo, source, target)
        return round(costoTot, 3), path

# + spiegazione del senso e funzionamento della idMap
# --------------------------------------------------------------------------------------------------------------

# LAB14 GENE_SMALL

    def searchPath(self, t):

        for n in self.get_nodes():
            partial = []
            # Scelta di partial_edges: La lista partial_edges è essenziale per tenere traccia degli archi specifici
            # che compongono il percorso corrente. Questo è importante perché, in un grafo diretto,
            # la direzione degli archi influisce sulla validità del percorso. Inoltre, il peso totale
            # del percorso, che è un criterio chiave per trovare il percorso più lungo, dipende dagli archi specifici inclusi nel percorso
            partial_edges = []

            partial.append(n)
            self.ricorsione(partial, partial_edges, t)

        return self.solBest, self.computeWeightPath(self.solBest)

    def ricorsione(self, partial, partial_edges, t):
        """
        L'algoritmo di ricorsione in questione è progettato per esplorare un grafo diretto, cercando di trovare il percorso più lungo
         (in termini di peso totale degli archi) che soddisfa un certo criterio, definito da una soglia t.
        """
        n_last = partial[-1]
# 1) Ricerca dei Vicini Ammissibili:
# Viene chiamata la funzione getAdmissibleNeighbs per trovare tutti i vicini di n_last che non sono già presenti
# nel percorso parziale e che hanno un arco con un peso maggiore della soglia t. Questo passaggio assicura che il
# percorso esplorato sia sempre diretto in avanti e che il peso degli archi soddisfi il criterio specificato.
        neigh = self.getAdmissibleNeighbs(n_last, partial_edges, t)

# 2) Caso Base (Terminale) della Ricorsione:
# Se non ci sono vicini ammissibili, significa che il percorso non può essere ulteriormente esteso. A questo punto,
# il peso totale del percorso corrente viene calcolato e confrontato con il peso del miglior percorso trovato fino a quel momento (solBest).
# Se il percorso corrente è migliore, diventa il nuovo miglior percorso.
        if len(neigh) == 0:
            weight_path = self.computeWeightPath(partial_edges)
            weight_path_best = self.computeWeightPath(self.solBest)
            if weight_path > weight_path_best:
                self.solBest = partial_edges[:]
            return

# Espansione del Percorso:
# Se ci sono vicini ammissibili, l'algoritmo itera su ciascuno di essi. Per ogni vicino:
        for n in neigh:
            partial.append(n)  # Viene aggiunto al percorso parziale.
            partial_edges.append((n_last, n, self._grafo.get_edge_data(n_last, n)))  # Viene aggiunto l'arco corrispondente (da n_last al vicino) a partial_edges.
            self.ricorsione(partial, partial_edges, t)  # Viene effettuata una chiamata ricorsiva per continuare l'esplorazione a partire dal nuovo nodo aggiunto.
            partial.pop()          # Dopo la chiamata ricorsiva, il nodo e l'arco appena aggiunti vengono rimossi per permettere l'esplorazione di altri percorsi potenziali.
            partial_edges.pop()
# Terminazione: La ricorsione termina quando tutti i percorsi possibili sono stati esplorati. Il miglior percorso trovato (solBest) e il suo peso sono il risultato dell'algoritmo.

# La funzione get_edge_data(n_last, n) restituisce un dizionario contenente i dati associati all'arco che collega
# il nodo n_last al nodo n nel grafo diretto self._grafo. Questi dati includono tipicamente il peso dell'arco,
# rappresentato dalla chiave 'weight' nel dizionario, oltre ad altre possibili informazioni specifiche dell'arco.
    def getAdmissibleNeighbs(self, n_last, partial_edges, t):
        all_neigh = self._grafo.edges(n_last, data=True)
        result = []
        for e in all_neigh:
            if e[2]["weight"] > t:
                # Per ogni arco e che parte da n_last, viene creato un arco inverso e_inv. Questo passaggio è necessario
                # per verificare che l'arco non sia già stato percorso in direzione inversa, mantenendo la coerenza del percorso in un grafo diretto.
                e_inv = (e[1], e[0], e[2])
                if (e_inv not in partial_edges) and (e not in partial_edges):
                    # Questo controllo previene l'inclusione di cicli nel percorso, garantendo che ogni arco sia considerato
                    # una sola volta e solo in una direzione, in linea con la definizione di un percorso semplice in un grafo diretto
                    result.append(e[1])
                    # il nodo destinazione dell'arco, indicato con e[1], viene aggiunto all'elenco result
        return result

    def computeWeightPath(self, mylist):
        if not isinstance(mylist, list):
            return 0  # Return 0 or some other default value indicating no weight
        weight = 0
        for e in mylist:
            weight += e[2]['weight']
        return weight
# --------------------------------------------------------------------------------------------------------------
