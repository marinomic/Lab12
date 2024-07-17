from database.DB_connect import DBConnect


class DAO():

# BASEBALL
    @staticmethod
    def getSalaryOfTeams(year, idMap):
        """
        Il peso di ciascun arco del grafo deve corrispondere alla somma dei salari dei giocatori delle due
        squadre nell’anno considerato. Selezionare i salari di tutte le squadre che hanno giocato in tale anno.
        """
        query = """
                       SELECT t.teamCode, t.ID, SUM(salary) as totalSalary
                       FROM salaries s, teams t, appearances a
                       WHERE s.year = t.year
                       AND a.teamID = t.ID 
                       AND s.playerID = a.playerID
                       AND s.year = a.year
                       AND t.year = %s
                       GROUP BY t.teamCode
                   """
        cursor.execute(query, (year,))
        result = {}
        for row in cursor:
            result[idMap[row['ID']]] = row['totalSalary']
# --------------------------------------------------------------------------------------------------------------


# ARTS MIA

    @staticmethod
    def getAllConnessioni(idMap: dict):
        """
        Un arco collega due oggetti se sono stati esposti contemporaneamente nella stessa exhibition
        """
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """
        select eo1.object_id as u, eo2.object_id as v, count(*) as weight
        from exhibition_objects eo1, exhibition_objects eo2
        where eo1.exhibition_id = eo2.exhibition_id 
        and eo1.object_id < eo2.object_id 
        group by eo1.object_id, eo2.object_id 
        order by weight desc """
        cursor.execute(query)
        for row in cursor:
            result.append(Connessione(idMap[row['u']], idMap[row['v']], row['weight']))
        return result

    @staticmethod
    def getWeight(u: ArtObject, v: ArtObject):
        """
         E il peso dell’arco rappresenta il numero di exhibition in cui tali oggetti sono stati contemporaneamente esposti.
        """
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """select count(*)
                    from exhibition_objects eo1, exhibition_objects eo2
                    where eo1.exhibition_id = eo2.exhibition_id 
                    and eo1.object_id < eo2.object_id 
                    and eo1.object_id = %s
                    and eo2.object_id = %s"""
        cursor.execute(query, (u.object_id, v.object_id))
        for row in cursor:
            result.append(row)
# --------------------------------------------------------------------------------------------------------------

# FLIGTH DELAYS
    @staticmethod
    def getAllNodes(x_compagnie, idMap):
        """
        I vertici devono rappresentare gli aeroporti su cui operano almeno x compagnie aeree (in arrivo o in partenza)
        """
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT tmp.ID, tmp.IATA_CODE, COUNT(*) AS N
        FROM (
        SELECT a.ID , a.IATA_CODE , f.AIRLINE_ID
        FROM airports a , flights f 
        WHERE a.ID = f.ORIGIN_AIRPORT_ID or a.ID = f.DESTINATION_AIRPORT_ID 
        GROUP BY a.ID , a.IATA_CODE , f.AIRLINE_ID
        ) AS tmp
        GROUP BY tmp.ID, tmp.IATA_CODE
        HAVING N >= %s
        """
        cursor.execute(query, (x_compagnie,))
        for row in cursor:
            result.append(idMap[row['ID']])

    # Metodo 1 in cui con python poi verifico se i nodi esistono nel grafo
    # e aggiungo il peso per ogni volo
    @staticmethod
    def getAllEdgesV1(idMap):
        """
        Gli archi devono rappresentare le rotte tra gli aeroporti collegati tra di loro da almeno un volo.
         Il peso dell’arco deve rappresentare il numero totale di voli tra i due aeroporti (poiché il grafo non è orientato,
          considerare tutti i voli in entrambe le direzioni: A->B e B->A).
        """
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """select f.ORIGIN_AIRPORT_ID , f.DESTINATION_AIRPORT_ID, count(*) as peso
                    from flights f 
                    group by f.ORIGIN_AIRPORT_ID , f.DESTINATION_AIRPORT_ID 
                    order by f.ORIGIN_AIRPORT_ID , f.DESTINATION_AIRPORT_ID"""
        cursor.execute(query)
        for row in cursor:
            result.append(Connessione(idMap[row['ORIGIN_AIRPORT_ID']],
                                      idMap[row['DESTINATION_AIRPORT_ID']],
                                      row['peso']))
    # Metodo 2 in cui con sql faccio già il join tra i voli e i voli inversi e aggiungo il peso
    @staticmethod
    def getAllEdgesV2(idMap):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """SELECT t1.ORIGIN_AIRPORT_ID, t1.DESTINATION_AIRPORT_ID, COALESCE(t1.n, 0) + coalesce(t2.n, 0) as peso
                        from 
                        (SELECT f.ORIGIN_AIRPORT_ID , f.DESTINATION_AIRPORT_ID , count(*) as n
                        FROM flights f 
                        group by f.ORIGIN_AIRPORT_ID , f.DESTINATION_AIRPORT_ID
                        order by f.ORIGIN_AIRPORT_ID , f.DESTINATION_AIRPORT_ID ) t1
                        left join 
                        (SELECT f.ORIGIN_AIRPORT_ID , f.DESTINATION_AIRPORT_ID , count(*) as n
                        FROM flights f 
                        group by f.ORIGIN_AIRPORT_ID , f.DESTINATION_AIRPORT_ID
                        order by f.ORIGIN_AIRPORT_ID , f.DESTINATION_AIRPORT_ID ) t2
                        on t1.ORIGIN_AIRPORT_ID = t2.DESTINATION_AIRPORT_ID and t1.DESTINATION_AIRPORT_ID = t2.ORIGIN_AIRPORT_ID
                        where t1.ORIGIN_AIRPORT_ID < t1.DESTINATION_AIRPORT_ID or t2.ORIGIN_AIRPORT_ID is null"""
        cursor.execute(query)
        for row in cursor:
            result.append(Connessione(idMap[row["ORIGIN_AIRPORT_ID"]],
                                      idMap[row["DESTINATION_AIRPORT_ID"]],
                                      row["peso"]))
# --------------------------------------------------------------------------------------------------------------

# ITUNES

    @staticmethod
    def getAllALbums(durata):
        """
        I vertici sono tutti gli album musicali (tabella Album) la cui durata
         (intesa come somma delle durate dei brani a esso appartenenti) sia superiore a d (scelta dall'utente).
        """
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """select a.*, sum(t.Milliseconds) as totDurata
                    from album a , track t 
                    where a.AlbumId = t.AlbumId 
                    group by a.AlbumId
                    having totDurata/60000 > %s"""
        cursor.execute(query, (durata,))
        for row in cursor:
            result.append(Album(**row))

    @staticmethod
    def getEdges(idMap):
        """
        Due album a1 e a2 sono collegati tra loro se almeno una canzone (tabella track) di a1 e una canzone di a2
        sono state inserite da un utente all’interno di una stessa playlist (tabella PlaylistTrack).
        """
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """
        select distinctrow t.AlbumId as a1, t2.AlbumId as a2
        from playlisttrack p , track t , playlisttrack p2 , track t2 
        where t.AlbumId <> t2.AlbumId 
        and t.TrackId = p.TrackId 
        and t2.TrackId = p2.TrackId
        and p2.PlaylistId = p.PlaylistId
        """
        cursor.execute(query)
        for row in cursor:
            # aggiungo solo se i nodi gia' esistono, cioè se gli album hanno la durata maggiore di quella inserita
            if row['a1'] in idMap and row['a2'] in idMap:
                result.append((idMap[row['a1']], idMap[row['a2']]))

# --------------------------------------------------------------------------------------------------------------

# NYC-HOTSPOTS

# come nodi creo classe e riempo oggetti con il risultato della query
    @staticmethod
    def getAllEdges(provider):
    """
    Due località l1 e l2 sono collegate da un arco se la DISTANZA TRA LE DUE LOCALITÀ è minore o uguale alla SOGLIA X INSERITA DALL’UTENTE.
    """
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT n1.Location as n1Loc, n2.Location as n2Loc, avg(n1.Latitude) as n1Lat, avg(n1.Longitude) as n1Long, avg(n2.Latitude) as n2Lat, avg(n2.Longitude) as n2Long
                    FROM nyc_wifi_hotspot_locations n1 , nyc_wifi_hotspot_locations n2 
                    WHERE n1.Provider = n2.Provider 
                    and n1.Provider = %s
                    and n1.Location < n2.Location 
                    GROUP by n1.Location, n2.Location
                """
        cursor.execute(query, (provider,))
        for row in cursor:
            loc1 = Location(row['n1Loc'], row['n1Lat'], row['n1Long'])
            loc2 = Location(row['n2Loc'], row['n2Lat'], row['n2Long'])
            result.append((loc1, loc2))
# --------------------------------------------------------------------------------------------------------------

# GENE_SMALL

@staticmethod
    def getAllGenes():
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """select * from genes"""
        cursor.execute(query)
        for row in cursor:
            result.append(Gene(**row))
    @staticmethod
    def getAllChromosomes():
        """
        I vertici siano tutti i cromosomi (tabella genes, colonna chromosome, considerando solo i valori diversi da 0).
        """
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """select distinct Chromosome
                    from genes
                    where Chromosome >0"""
        cursor.execute(query)
        for row in cursor:
            result.append(row['Chromosome'])
    @staticmethod
    def getAllConnectedGenes():
        """ Un arco collega due cromosomi diversi solo se i due cromosomi contengono due geni (uno per cromosoma)
         che compaiono (nello stesso ordine) nella tabella interactions. Si noti che, per ciascun cromosoma, possono
         esistere più geni, e ciascuno di essi potrebbe essere presente più volte (associato a function diverse)."""
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """select g1.GeneID as Gene1, g2.GeneID as Gene2, i.Expression_Corr
                    FROM genes g1, genes g2, interactions i 
                    where  g1.GeneID = i.GeneID1 and g2.GeneID = i.GeneID2  
                    and g2.Chromosome != g1.Chromosome
                    and g2.Chromosome>0
                    and g1.Chromosome>0
                    group by g1.GeneID, g2.GeneID"""
        cursor.execute(query)
        for row in cursor:
            result.append((row['Gene1'], row['Gene2'], row['Expression_Corr']))
# --------------------------------------------------------------------------------------------------------------
