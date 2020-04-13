# ScrapingStadia

Aquest projecte s'ha realitzat amb l'objectiu d'entregar una pràctica amb els coneixements apresos sobre les tècniques de Web Scraping a l'assignatura _Tipologia i cicle de vida de les dades_, que es realitza dins el [Màster de Ciència de Dades de la UOC](https://estudis.uoc.edu/ca/masters-universitaris/data-science/pla-estudis).

A més del codi aquí present, s'entrega amb un document pdf que descriu la feina feta. Aquest document es troba dins la carpeta /pdf d'aquest mateix projecte.

### Instal·lació de les llibreries necessàries

```
pip install -r requirements.txt
```

A més, si volem accedir als preus dels jocs de Stadia, haurem d'indicar el nostre nom d'usuari i password a l'arxiu `config.properties`.

### Executar el codi

Hi ha quatre modes per a obtenir les dades:

1. Obtenir totes les dades:

    ```
    python3 main.py all
    ```

2. Obtenir només les dades dels títols dels jocs i informació per als jocs en altres plataformes.

    ```
    python3 main.py external
    ```
   
3. Obtenir només dades dels preus dels jocs de Stadia.
    
      ```
      python3 main.py stadia-only
      ```
     
4. Actualitzar els preus dels jocs en a l'arxiu `output_data/data.csv`.

    ```
    python3 main.py stadia-update
    ```
   
### Fitxer ouptut

El fitxer output es troba a `output_data/data.csv`

### Full de respostes de l'exercici 

El full de respostes de l'exercici es troba a `pdf/respostes.pdf`